"""
Chatbot CrewAI Crew — Context-aware conversational agent.

Uses two agents:
  1. Context Retriever: Fetches employee profile, training status, assessments.
  2. Response Agent: Generates a helpful response using the employee context.
"""

import json
import logging
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from common.security import get_secret
from common.llm_client import OpenRouterClient

logger = logging.getLogger(__name__)

# System prompt with guardrails
SYSTEM_PROMPT = """You are an AI assistant for employee onboarding and training.

You help employees with:
- Understanding their onboarding process and next steps
- Questions about their training modules and assessments
- Company policies and HR processes
- Technical questions related to their role
- Navigating the employee training platform

GUARDRAILS:
- NEVER reveal personal information (PII) about other employees.
- NEVER make up specific company policies. If unsure, say "I recommend checking with your HR representative."
- NEVER answer questions unrelated to work, training, or onboarding.
- If a question is outside your knowledge, respond with: "I'd recommend reaching out to your HR team for that. Would you like me to connect you?"
- Keep responses concise, professional, and encouraging.
"""


class ChatbotCrew:
    """
    CrewAI orchestrator for the chatbot. Uses a two-agent pipeline:
    1. Context Retriever gathers employee-specific information
    2. Response Agent crafts a contextual answer
    """

    def __init__(self):
        api_key = get_secret('OPENROUTER_API_KEY')
        client = OpenRouterClient()

        self.llm = ChatOpenAI(
            model=client.default_model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "http://localhost:8000"},
        )

        self.context_retriever = Agent(
            role='Employee Context Retriever',
            goal='Gather all relevant context about the employee to help answer their question accurately.',
            backstory='You are an internal data specialist who quickly retrieves employee profiles, training status, and assessment results to provide context for answering questions.',
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
        )

        self.response_agent = Agent(
            role='Employee Support Agent',
            goal='Provide a helpful, accurate, and encouraging response to the employee\'s question.',
            backstory=SYSTEM_PROMPT,
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
        )

    def get_response(self, query: str, employee_context: dict) -> str:
        """
        Runs the two-agent crew to generate a response.
        
        Args:
            query: The employee's question
            employee_context: Dict with employee profile, training status, etc.
        
        Returns:
            The chatbot's response string.
        """
        context_str = json.dumps(employee_context, default=str, indent=2)

        context_task = Task(
            description=f"""Given the following employee context, summarize the most relevant information 
for answering this question: "{query}"

Employee Context:
{context_str}

Summarize ONLY the relevant parts of the context. Do not make up information.""",
            expected_output="A concise summary of the relevant employee context.",
            agent=self.context_retriever,
        )

        response_task = Task(
            description=f"""Using the context summary from the Context Retriever, answer the employee's question:
"{query}"

Rules:
- Be concise and helpful (max 3 paragraphs).
- Never reveal other employees' information.
- If unsure, direct them to HR.
- Be encouraging and professional.
- Do NOT include any JSON or metadata in your response — just the answer text.""",
            expected_output="A clear, helpful response to the employee's question.",
            agent=self.response_agent,
        )

        crew = Crew(
            agents=[self.context_retriever, self.response_agent],
            tasks=[context_task, response_task],
            process=Process.sequential,
            verbose=False,
        )

        try:
            result = crew.kickoff()
            return str(result).strip()
        except Exception as e:
            logger.error(f"ChatbotCrew failed: {e}")
            return "I'm having trouble processing your request right now. Please try again in a moment, or reach out to your HR representative for immediate assistance."
