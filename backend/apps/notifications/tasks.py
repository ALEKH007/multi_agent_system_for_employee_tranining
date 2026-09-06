import logging
from agents.agent_registry import register_agent
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)

@register_agent('training.assigned')
async def handle_training_assigned(event_data: dict):
    """
    Creates a notification when a new training module is assigned.
    """
    employee_id = event_data.get('employee_id')
    module_id = event_data.get('module_id')
    
    # Create in-app notification
    notif = Notification(
        employee_id=employee_id,
        message=f"You have been assigned a new training module: {module_id}.",
        type='system'
    )
    notif.save()
    logger.info(f"NotificationAgent: Created assigned notification for {employee_id}")

@register_agent('progress.updated')
async def handle_progress_updated(event_data: dict):
    """
    Creates notifications based on progress updates (e.g., overdue alerts or completions).
    """
    employee_id = event_data.get('employee_id')
    status = event_data.get('completion_status')
    
    if status == 'completed':
        # Send congratulatory message
        notif = Notification(
            employee_id=employee_id,
            message=f"Congratulations! You've successfully completed a training module.",
            type='system'
        )
        notif.save()
        logger.info(f"NotificationAgent: Created completion notification for {employee_id}")
