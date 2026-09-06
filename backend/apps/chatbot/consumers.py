"""
Chatbot WebSocket Consumer — Async Django Channels consumer.

Authenticates via JWT cookie on handshake. Rate-limited per connection.
Receives employee messages, runs CrewAI, and streams the response back.
"""

import uuid
import json
import time
import logging
import asyncio
import concurrent.futures
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.authentication.utils import verify_jwt_token
from apps.authentication.models import User
from apps.chatbot.models import ChatLog
from apps.chatbot.crew import ChatbotCrew
from agents.event_bus import EventBus
from agents.event_schemas import SupportQueryRaisedV1

logger = logging.getLogger(__name__)

# Rate limit: max messages per minute per user
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = 60  # seconds


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for the AI chatbot.
    Authenticates via JWT in the HttpOnly cookie (not URL params — avoids token leaking in server logs).
    """

    async def connect(self):
        """Authenticate the WebSocket handshake using the JWT cookie."""
        self.user = None
        self.employee_id = None
        self.message_timestamps = []  # For rate limiting

        # Extract JWT from cookies (secure — not in URL params)
        cookies = self.scope.get('cookies', {})
        token = cookies.get('auth_token')

        if not token:
            logger.warning("WebSocket connection rejected: no auth_token cookie")
            await self.close(code=4001)
            return

        payload = verify_jwt_token(token)
        if not payload:
            logger.warning("WebSocket connection rejected: invalid/expired JWT")
            await self.close(code=4001)
            return

        user_id = payload.get('user_id')
        try:
            self.user = User.objects.get(user_id=user_id)
            self.employee_id = self.user.employee_id
        except User.DoesNotExist:
            logger.warning(f"WebSocket connection rejected: user {user_id} not found")
            await self.close(code=4001)
            return

        await self.accept()
        logger.info(f"WebSocket connected: user={user_id}")

        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'system',
            'message': f'Hello {self.user.username}! I\'m your AI training assistant. How can I help you today?',
        }))

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected: user={getattr(self, 'employee_id', 'unknown')} code={close_code}")

    async def receive(self, text_data):
        """Handle incoming messages from the client."""
        if not self.user:
            await self.close(code=4001)
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format.',
            }))
            return

        query = data.get('message', '').strip()

        if not query:
            return

        # Input length validation
        if len(query) > 2000:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message too long. Please keep it under 2000 characters.',
            }))
            return

        # Rate limiting
        now = time.time()
        self.message_timestamps = [t for t in self.message_timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(self.message_timestamps) >= RATE_LIMIT_MAX:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'You\'re sending messages too quickly. Please wait a moment.',
            }))
            return
        self.message_timestamps.append(now)

        # Send typing indicator
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'message': 'Thinking...',
        }))

        # Build employee context for the crew
        employee_context = await self._build_employee_context()

        # Run CrewAI in a thread pool (it's CPU/IO bound and synchronous)
        loop = asyncio.get_event_loop()
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                response_text = await loop.run_in_executor(
                    pool,
                    self._run_crew_sync,
                    query,
                    employee_context,
                )
        except Exception as e:
            logger.error(f"Chatbot crew execution failed: {e}")
            response_text = "I'm having trouble right now. Please try again shortly, or contact your HR representative."

        # Save chat log
        resolved = "reach out to" not in response_text.lower() and "connect you" not in response_text.lower()
        chat_log = ChatLog(
            employee_id=self.employee_id,
            query_text=query,
            response_text=response_text,
            resolved=resolved,
        )
        chat_log.save()

        # Publish support.query_raised event for analytics
        bus = EventBus()
        event = SupportQueryRaisedV1(
            event_id=str(uuid.uuid4()),
            employee_id=self.employee_id,
            chat_id=str(chat_log.chat_id),
            query_text=query[:200],  # Truncate for event bus — full text is in ChatLog
            resolved=resolved,
        )
        bus.publish('support.query_raised', event.model_dump())

        # Send the response
        await self.send(text_data=json.dumps({
            'type': 'response',
            'message': response_text,
            'chat_id': str(chat_log.chat_id),
            'resolved': resolved,
        }))

    def _run_crew_sync(self, query: str, employee_context: dict) -> str:
        """Synchronous wrapper for CrewAI execution."""
        crew = ChatbotCrew()
        return crew.get_response(query, employee_context)

    async def _build_employee_context(self) -> dict:
        """
        Gathers the employee's current context for the chatbot crew.
        Includes profile, training progress, and recent assessment results.
        """
        context = {
            'username': self.user.username,
            'role': getattr(self.user, 'role', 'employee'),
            'employee_id': self.employee_id,
        }

        try:
            from apps.employees.models import Employee
            employee = Employee.objects(employee_id=self.employee_id).first()
            if employee:
                context['name'] = employee.name
                context['department'] = employee.department_id
                context['joining_date'] = str(employee.joining_date)
        except Exception:
            pass

        try:
            from apps.training.models import TrainingProgress
            progress = TrainingProgress.objects(employee_id=self.employee_id)
            context['training_progress'] = [
                {
                    'module_id': p.module_id,
                    'status': p.completion_status,
                    'due_date': str(p.due_date),
                    'score': p.score,
                }
                for p in progress
            ]
        except Exception:
            context['training_progress'] = []

        try:
            from apps.assessments.models import SkillAssessment
            assessment = SkillAssessment.objects(employee_id=self.employee_id).order_by('-created_at').first()
            if assessment:
                context['latest_assessment'] = {
                    'title': assessment.title,
                    'score': assessment.skill_score,
                    'weak_areas': assessment.weak_areas,
                    'strong_areas': assessment.strong_areas,
                    'status': assessment.status,
                }
        except Exception:
            pass

        return context
