import asyncio
import logging
import signal
import sys
from django.core.management.base import BaseCommand
from agents.event_bus import EventBus
from agents.agent_registry import get_registry

# Import all apps to ensure decorators are executed and agents registered
import django
django.setup()

# Import task modules to trigger @register_agent decorator execution
from apps.assessments import tasks as assessment_tasks  # noqa: F401
from apps.recommendations import tasks as recommendation_tasks # noqa: F401
from apps.training import tasks as training_tasks # noqa: F401
# from apps.progress import tasks as progress_tasks
from apps.analytics import tasks as analytics_tasks # noqa: F401
from apps.notifications import tasks as notification_tasks # noqa: F401

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Starts the Event Bus subscribers for all registered AI Agents.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Multi-Agent System Event Bus..."))
        
        registry = get_registry()
        if not registry:
            self.stdout.write(self.style.WARNING("No agents registered in the system!"))
        
        bus = EventBus()
        loop = asyncio.get_event_loop()
        
        tasks = []
        for channel, handlers in registry.items():
            for handler in handlers:
                # Create a task for each handler subscribing to the channel
                task = loop.create_task(bus.subscribe(channel, handler))
                tasks.append(task)
                self.stdout.write(self.style.SUCCESS(f"Started subscriber: {handler.__name__} on {channel}"))

        # Setup graceful shutdown
        def shutdown_handler(sig, frame):
            logger.info("Shutting down agents...")
            for task in tasks:
                task.cancel()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        try:
            # Run all subscriber loops concurrently
            if tasks:
                loop.run_until_complete(asyncio.gather(*tasks))
            else:
                # Just keep alive if no tasks
                loop.run_forever()
        except asyncio.CancelledError:
            pass
        finally:
            loop.close()
            self.stdout.write(self.style.SUCCESS("Event Bus shut down successfully."))
