"""
Skill Assessment Agent — Event-driven task handler.

Subscribes to:
  - `employee.registered` → Creates a pending assessment for the new employee.

Publishes:
  - `assessment.completed` → After scoring a submitted assessment.

This module also provides the scoring engine and LLM-based question generation.
"""

import uuid
import logging
from datetime import datetime
from collections import defaultdict

from agents.agent_registry import register_agent
from agents.event_bus import EventBus
from agents.event_schemas import AssessmentCompletedV1
from common.llm_client import OpenRouterClient
from apps.assessments.models import SkillAssessment, AssessmentTemplate

logger = logging.getLogger(__name__)
bus = EventBus()


# ---------------------------------------------------------------------------
# Default fallback questions if no template exists and LLM generation fails
# ---------------------------------------------------------------------------
FALLBACK_QUESTIONS = [
    {
        "question_id": "fb_1",
        "text": "Which of the following is NOT a core principle of effective teamwork?",
        "options": [
            "Clear communication",
            "Individual competition",
            "Mutual respect",
            "Shared accountability"
        ],
        "correct_answer": "Individual competition",
        "category": "soft_skills"
    },
    {
        "question_id": "fb_2",
        "text": "What is the primary benefit of time management in a professional setting?",
        "options": [
            "Working longer hours",
            "Increased productivity and reduced stress",
            "Avoiding delegation",
            "Multitasking on every project"
        ],
        "correct_answer": "Increased productivity and reduced stress",
        "category": "soft_skills"
    },
    {
        "question_id": "fb_3",
        "text": "In project management, what does 'scope creep' refer to?",
        "options": [
            "A project finishing ahead of schedule",
            "Uncontrolled expansion of project requirements",
            "A team member leaving mid-project",
            "Budget overruns due to inflation"
        ],
        "correct_answer": "Uncontrolled expansion of project requirements",
        "category": "project_management"
    },
    {
        "question_id": "fb_4",
        "text": "Which communication style is generally most effective in professional environments?",
        "options": [
            "Passive",
            "Aggressive",
            "Assertive",
            "Passive-aggressive"
        ],
        "correct_answer": "Assertive",
        "category": "communication"
    },
    {
        "question_id": "fb_5",
        "text": "What does SMART stand for when setting goals?",
        "options": [
            "Simple, Measurable, Achievable, Relevant, Timely",
            "Specific, Measurable, Achievable, Relevant, Time-bound",
            "Strategic, Manageable, Actionable, Realistic, Trackable",
            "Scalable, Meaningful, Accessible, Reliable, Targeted"
        ],
        "correct_answer": "Specific, Measurable, Achievable, Relevant, Time-bound",
        "category": "project_management"
    },
]


async def generate_questions_via_llm(role: str, num_questions: int = 10) -> list:
    """
    Uses the OpenRouter LLM to generate role-specific assessment questions.
    Falls back to template or hardcoded questions on failure.
    """
    try:
        client = OpenRouterClient()
        
        prompt = f"""Generate exactly {num_questions} multiple-choice assessment questions for a new employee 
with the role: "{role}". Each question should test skills relevant to this role.

Return the questions as a JSON array. Each element must have this exact structure:
{{
  "question_id": "q1",
  "text": "The question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": "The correct option text (must match one of the options exactly)",
  "category": "category_name"
}}

Use these category names where appropriate: technical, communication, problem_solving, 
domain_knowledge, soft_skills, project_management, data_analysis, leadership.

Return ONLY the JSON array, no markdown formatting, no explanation."""

        messages = [
            {"role": "system", "content": "You are an HR assessment specialist. You generate high-quality, role-appropriate skill assessment questions. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]

        response = await client.generate_chat_completion_async(messages)
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # Strip markdown code fences if present
        content = content.strip()
        if content.startswith('```'):
            # Remove opening fence
            first_newline = content.index('\n')
            content = content[first_newline + 1:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        import json
        questions = json.loads(content)
        
        # Validate structure
        if not isinstance(questions, list) or len(questions) == 0:
            raise ValueError("LLM returned invalid question format")
        
        for i, q in enumerate(questions):
            if not all(k in q for k in ('text', 'options', 'correct_answer', 'category')):
                raise ValueError(f"Question {i} missing required fields")
            # Ensure question_id is set
            if 'question_id' not in q:
                q['question_id'] = f"q{i+1}"
        
        logger.info(f"LLM generated {len(questions)} questions for role '{role}'")
        return questions

    except Exception as e:
        logger.warning(f"LLM question generation failed for role '{role}': {e}. Using fallback.")
        return None


def get_questions_for_role(role: str) -> list:
    """
    Retrieves assessment questions for a given role.
    Priority: AssessmentTemplate → LLM generation → Fallback hardcoded.
    Note: This is sync; the async LLM path is called separately.
    """
    # Try to find an existing template
    template = AssessmentTemplate.objects(role=role).first()
    if template and template.questions:
        logger.info(f"Using template '{template.title}' for role '{role}'")
        return list(template.questions)
    
    # No template found — return fallback (LLM generation happens async in the agent)
    logger.info(f"No template for role '{role}', using fallback questions")
    return list(FALLBACK_QUESTIONS)


def score_assessment(assessment: SkillAssessment) -> dict:
    """
    Scores a submitted assessment by comparing answers to correct answers.
    Returns a dict with: skill_score, weak_areas, strong_areas, category_scores.
    """
    if not assessment.questions or not assessment.answers:
        return {
            'skill_score': 0.0,
            'weak_areas': [],
            'strong_areas': [],
            'category_scores': {}
        }
    
    # Build a lookup of correct answers
    correct_lookup = {}
    question_categories = {}
    for q in assessment.questions:
        qid = q.get('question_id')
        correct_lookup[qid] = q.get('correct_answer')
        question_categories[qid] = q.get('category', 'general')
    
    # Score per category
    category_correct = defaultdict(int)
    category_total = defaultdict(int)
    total_correct = 0
    total_questions = len(assessment.questions)
    
    # Build answer lookup
    answer_lookup = {}
    for a in assessment.answers:
        answer_lookup[a.get('question_id')] = a.get('selected_answer')
    
    for qid, correct_answer in correct_lookup.items():
        category = question_categories[qid]
        category_total[category] += 1
        
        submitted = answer_lookup.get(qid)
        if submitted and submitted.strip() == correct_answer.strip():
            total_correct += 1
            category_correct[category] += 1
    
    # Calculate overall score
    skill_score = (total_correct / total_questions * 100.0) if total_questions > 0 else 0.0
    
    # Calculate per-category scores and determine weak/strong areas
    category_scores = {}
    weak_areas = []
    strong_areas = []
    
    WEAK_THRESHOLD = 50.0
    STRONG_THRESHOLD = 75.0
    
    for category, total in category_total.items():
        correct = category_correct.get(category, 0)
        pct = (correct / total * 100.0) if total > 0 else 0.0
        category_scores[category] = round(pct, 1)
        
        if pct < WEAK_THRESHOLD:
            weak_areas.append(category)
        elif pct >= STRONG_THRESHOLD:
            strong_areas.append(category)
    
    return {
        'skill_score': round(skill_score, 1),
        'weak_areas': weak_areas,
        'strong_areas': strong_areas,
        'category_scores': category_scores,
    }


# ---------------------------------------------------------------------------
# Agent Handler: employee.registered
# ---------------------------------------------------------------------------
@register_agent('employee.registered')
async def handle_employee_registered(event_data: dict):
    """
    Triggered when a new employee is registered.
    Creates a pending skill assessment for the employee.
    Idempotent: skips if an assessment with the same trigger_event_id already exists.
    """
    event_id = event_data.get('event_id')
    employee_id = event_data.get('employee_id')
    role = event_data.get('role', 'general')
    name = event_data.get('name', 'Employee')
    
    logger.info(f"Skill Assessment Agent: Received employee.registered for {employee_id}")
    
    # Idempotency check
    existing = SkillAssessment.objects(trigger_event_id=event_id).first()
    if existing:
        logger.info(f"Assessment already exists for event {event_id}. Skipping.")
        return
    
    # Try LLM-generated questions first, fall back to templates/hardcoded
    questions = await generate_questions_via_llm(role)
    if not questions:
        questions = get_questions_for_role(role)
    
    # Create the assessment
    assessment = SkillAssessment(
        employee_id=employee_id,
        title=f"Initial Skill Assessment for {name}",
        description=f"Onboarding assessment covering core competencies for the {role} role.",
        questions=questions,
        status='pending',
        trigger_event_id=event_id,
    )
    assessment.save()
    
    logger.info(f"Created pending assessment {assessment.assessment_id} for employee {employee_id}")


# ---------------------------------------------------------------------------
# Scoring handler (called from views when employee submits answers)
# ---------------------------------------------------------------------------
async def process_assessment_submission(assessment_id: str) -> dict:
    """
    Scores a submitted assessment and publishes assessment.completed event.
    Called from the views layer after answers are saved.
    """
    assessment = SkillAssessment.objects.get(assessment_id=assessment_id)
    
    # Score
    results = score_assessment(assessment)
    
    # Update assessment record
    assessment.skill_score = results['skill_score']
    assessment.weak_areas = results['weak_areas']
    assessment.strong_areas = results['strong_areas']
    assessment.category_scores = results['category_scores']
    assessment.status = 'completed'
    assessment.completed_at = datetime.utcnow()
    assessment.save()
    
    # Publish assessment.completed event
    event = AssessmentCompletedV1(
        event_id=str(uuid.uuid4()),
        employee_id=assessment.employee_id,
        assessment_id=str(assessment.assessment_id),
        skill_score=results['skill_score'],
        weak_areas=results['weak_areas'],
        strong_areas=results['strong_areas'],
    )
    bus.publish('assessment.completed', event.model_dump())
    
    logger.info(
        f"Assessment {assessment_id} scored: {results['skill_score']}% | "
        f"Weak: {results['weak_areas']} | Strong: {results['strong_areas']}"
    )
    
    return results
