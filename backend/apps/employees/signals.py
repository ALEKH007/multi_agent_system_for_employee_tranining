from mongoengine import signals
from .models import Employee
from agents.event_bus import EventBus
from agents.event_schemas import EmployeeRegisteredV1
import logging
import uuid

logger = logging.getLogger(__name__)

def employee_post_save(sender, document: Employee, created: bool, **kwargs):
    """
    Signal handler triggered after an Employee document is saved.
    Publishes an event to the Redis event bus if it's a new employee.
    """
    if created:
        try:
            bus = EventBus()
            event = EmployeeRegisteredV1(
                event_id=str(uuid.uuid4()),
                employee_id=str(document.employee_id),
                name=document.name,
                department_id=str(document.department_id),
                role=document.role,
                joining_date=document.joining_date.isoformat()
            )
            bus.publish('employee.registered', event.model_dump())
            logger.info(f"Published employee.registered event for {document.employee_id}")
        except Exception as e:
            logger.error(f"Failed to publish employee.registered event: {str(e)}")

# Connect the signal
signals.post_save.connect(employee_post_save, sender=Employee)
