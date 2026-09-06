import uuid
import logging
from datetime import datetime

from agents.agent_registry import register_agent
from agents.event_bus import EventBus
from agents.event_schemas import PlanCreatedV1
from apps.recommendations.models import LearningPlan
from apps.recommendations.crew import RecommendationCrew
from apps.employees.models import Employee
from apps.training.models import TrainingModule

logger = logging.getLogger(__name__)
bus = EventBus()

def get_available_modules():
    """Return only modules that actually exist in the training catalog."""
    return [
        {
            "module_id": module.module_id,
            "title": module.title,
            "category": module.category,
            "difficulty": module.difficulty,
        }
        for module in TrainingModule.objects.all()
    ]

@register_agent('assessment.completed')
async def handle_assessment_completed(event_data: dict):
    """
    Triggered when a skill assessment is completed.
    Uses CrewAI to generate a personalized learning plan based on the assessment gaps.
    """
    event_id = event_data.get('event_id')
    employee_id = event_data.get('employee_id')
    assessment_id = event_data.get('assessment_id')
    weak_areas = event_data.get('weak_areas', [])
    strong_areas = event_data.get('strong_areas', [])  # might not be in event, fallback to empty
    
    logger.info(f"Recommendation Agent: Received assessment.completed for {employee_id}")
    
    # Idempotency check: Don't generate multiple plans for the same assessment completion
    # We use the assessment_id to link the plan, since an employee might take multiple assessments
    # but only one plan should be generated per assessment.
    existing = LearningPlan.objects(assessment_id=assessment_id).first()
    if existing:
        logger.info(f"Learning Plan already exists for assessment {assessment_id}. Skipping.")
        return
        
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        role = employee.role
    except Exception as e:
        logger.error(f"Could not fetch employee {employee_id}: {e}")
        role = "general employee"
        
    available_modules = get_available_modules()
    if not available_modules:
        logger.warning("No training modules are configured; no plan can be assigned.")
    
    # Execute CrewAI orchestration only when the catalogue can support a plan.
    logger.info(f"Kicking off CrewAI to generate plan for {employee_id} (Role: {role})")
    
    # Run crew synchronously (CrewAI's kickoff is sync by default)
    # In a fully async system, we'd wrap this in run_in_executor
    import asyncio
    loop = asyncio.get_event_loop()
    
    def run_crew():
        crew = RecommendationCrew()
        return crew.generate_plan(role, weak_areas, strong_areas, available_modules)
        
    try:
        if not available_modules:
            raise RuntimeError("Training catalogue is empty")
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            recommended_modules = await loop.run_in_executor(pool, run_crew)
    except Exception as e:
        logger.error(f"CrewAI execution failed: {e}")
        recommended_modules = []
        
    if not recommended_modules:
        logger.warning(f"CrewAI returned empty plan for {employee_id}. Using fallback rule-based mapping.")
        # Fallback logic: assign one module per weak area if a match exists
        recommended_modules = []
        for wa in weak_areas:
            match = next((m for m in available_modules if m['category'] == wa), None)
            if match:
                recommended_modules.append({
                    "module_id": match['module_id'],
                    "reasoning": f"Fallback rule: Addresses weak area in {wa}"
                })
                
    # Create the Learning Plan
    plan = LearningPlan(
        employee_id=employee_id,
        assessment_id=assessment_id,
        recommended_modules=recommended_modules,
        created_by_model="crewai-openrouter-orchestration" if recommended_modules else "fallback-rules"
    )
    plan.save()
    logger.info(f"Created Learning Plan {plan.plan_id} for employee {employee_id}")
    
    # Publish plan.created event
    event = PlanCreatedV1(
        event_id=str(uuid.uuid4()),
        employee_id=employee_id,
        plan_id=str(plan.plan_id),
        recommended_modules=[str(m['module_id']) for m in recommended_modules]
    )
    bus.publish('plan.created', event.model_dump())
    logger.info(f"Published plan.created event for {employee_id}")
