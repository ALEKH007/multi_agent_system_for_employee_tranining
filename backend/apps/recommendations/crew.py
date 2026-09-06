import os
import json
import logging
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from common.security import get_secret
from common.llm_client import OpenRouterClient

logger = logging.getLogger(__name__)

class RecommendationCrew:
    """
    CrewAI Orchestrator for generating Learning Plans based on Skill Assessments.
    """
    
    def __init__(self):
        # Configure CrewAI to use OpenRouter via Langchain's ChatOpenAI wrapper
        api_key = get_secret('OPENROUTER_API_KEY')
        client = OpenRouterClient()
        
        self.llm = ChatOpenAI(
            model=client.default_model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "http://localhost:8000"}
        )
        
        self.skill_analyst = Agent(
            role='Skill Gap Analyst',
            goal='Analyze assessment results and identify critical skill gaps.',
            backstory='An expert HR analyst specializing in evaluating employee skills and determining priority areas for professional development.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        self.curriculum_designer = Agent(
            role='Curriculum Designer',
            goal='Match identified skill gaps with available training modules to create a personalized learning plan.',
            backstory='An experienced instructional designer who excels at curating training materials to address specific learning needs.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        self.plan_reviewer = Agent(
            role='Learning Plan Reviewer',
            goal='Review the proposed learning plan to ensure it is comprehensive, feasible, and directly addresses the employee\'s weak areas.',
            backstory='A senior L&D manager who ensures training plans are effective and realistic before they are assigned to employees.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def generate_plan(self, employee_role: str, weak_areas: list, strong_areas: list, available_modules: list) -> list:
        """
        Executes the CrewAI process to generate a learning plan.
        Returns a list of dicts: [{"module_id": "...", "reasoning": "..."}]
        """
        modules_str = json.dumps([{
            "module_id": str(m.get('module_id')),
            "title": m.get('title'),
            "category": m.get('category'),
            "difficulty": m.get('difficulty')
        } for m in available_modules])
        
        analyze_task = Task(
            description=f"""Analyze the following assessment results for a {employee_role}.
Weak Areas: {weak_areas}
Strong Areas: {strong_areas}
Identify the top 3 priority areas that need improvement to excel in this role.""",
            expected_output="A list of the top 3 priority learning areas with a brief justification for each.",
            agent=self.skill_analyst
        )
        
        design_task = Task(
            description=f"""Given the priority areas identified by the Skill Gap Analyst, select the most appropriate modules from this catalog:
{modules_str}
Assign at least one module per weak area, considering the employee's role ({employee_role}).""",
            expected_output="A drafted learning plan mapping selected module IDs to the priority areas they address.",
            agent=self.curriculum_designer
        )
        
        review_task = Task(
            description="""Review the drafted learning plan. Ensure it directly addresses the weak areas without overwhelming the employee.
Output the final plan STRICTLY as a JSON array of objects, with each object having exactly two keys: 'module_id' and 'reasoning'.
Example: [{"module_id": "m123", "reasoning": "Addresses the gap in Python basics."}]
Do not include any other text or markdown formatting outside the JSON array.""",
            expected_output="A valid JSON array of objects with 'module_id' and 'reasoning' keys.",
            agent=self.plan_reviewer
        )
        
        crew = Crew(
            agents=[self.skill_analyst, self.curriculum_designer, self.plan_reviewer],
            tasks=[analyze_task, design_task, review_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            # The result from CrewAI might be wrapped in a CrewOutput object or be a string
            result_str = str(result).strip()
            
            # Clean up potential markdown formatting
            if result_str.startswith('```'):
                first_newline = result_str.find('\n')
                result_str = result_str[first_newline + 1:]
            if result_str.endswith('```'):
                result_str = result_str[:-3]
                
            plan_data = json.loads(result_str.strip())
            
            if not isinstance(plan_data, list):
                logger.error(f"CrewAI returned non-list output: {plan_data}")
                return []
                
            return plan_data
            
        except Exception as e:
            logger.error(f"Failed to generate learning plan via CrewAI: {e}")
            return []
