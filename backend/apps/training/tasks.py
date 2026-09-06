import uuid
import logging
from datetime import datetime, timedelta

from agents.agent_registry import register_agent
from agents.event_bus import EventBus
from agents.event_schemas import TrainingAssignedV1, TrainingCompletedV1
from apps.training.models import TrainingModule, TrainingProgress
from apps.employees.models import Employee

logger = logging.getLogger(__name__)
bus = EventBus()


@register_agent('plan.created')
async def handle_plan_created(event_data: dict):
    """
    Training Management Agent: triggered when a new Learning Plan is created.
    Assigns the recommended modules to the employee with calculated due dates.
    """
    event_id = event_data.get('event_id')
    employee_id = event_data.get('employee_id')
    plan_id = event_data.get('plan_id')
    recommended_modules = event_data.get('recommended_modules', [])

    logger.info(f"Training Management Agent: Received plan.created for employee {employee_id}")

    if not recommended_modules:
        logger.warning(f"Plan {plan_id} has no recommended modules. Skipping.")
        return

    # Idempotency check: Don't assign the same modules for the same plan twice
    existing_progress = TrainingProgress.objects(plan_id=plan_id).count()
    if existing_progress > 0:
        logger.info(f"Training already assigned for plan {plan_id}. Skipping.")
        return

    # Assign modules with staggered due dates
    # We will assign the first module due in 7 days, the next due in 14 days, etc.
    base_due_date = datetime.utcnow() + timedelta(days=7)
    
    for i, module_id in enumerate(recommended_modules):
        if not TrainingModule.objects(module_id=module_id).first():
            logger.warning("Skipping unknown training module %s for plan %s", module_id, plan_id)
            continue
        # Calculate staggered due date (1 week per module)
        due_date = base_due_date + timedelta(days=7 * i)
        
        progress = TrainingProgress(
            employee_id=employee_id,
            module_id=module_id,
            plan_id=plan_id,
            completion_status='not_started',
            assigned_at=datetime.utcnow(),
            due_date=due_date
        )
        progress.save()
        logger.info(f"Assigned module {module_id} to employee {employee_id} (Due: {due_date.date()})")
        
        # Publish training.assigned event
        assign_event = TrainingAssignedV1(
            event_id=str(uuid.uuid4()),
            employee_id=employee_id,
            module_id=module_id,
            progress_id=str(progress.progress_id),
            due_date=due_date.isoformat()
        )
        bus.publish('training.assigned', assign_event.model_dump())


# Progress tracking logic (called from views)
async def process_training_completion(progress_id: str, score: float = None):
    """
    Marks a training module as completed and publishes training.completed event.
    """
    try:
        progress = TrainingProgress.objects.get(progress_id=progress_id)
    except TrainingProgress.DoesNotExist:
        logger.error(f"TrainingProgress {progress_id} not found.")
        return
        
    progress.completion_status = 'completed'
    progress.completed_at = datetime.utcnow()
    progress.updated_at = datetime.utcnow()
    if score is not None:
        progress.score = score
    progress.save()
    
    logger.info(f"Marked progress {progress_id} as completed for employee {progress.employee_id}")
    
    from agents.event_schemas import ProgressUpdatedV1
    
    event = TrainingCompletedV1(
        event_id=str(uuid.uuid4()),
        employee_id=progress.employee_id,
        module_id=progress.module_id,
        score=score
    )
    bus.publish('training.completed', event.model_dump())

    progress_event = ProgressUpdatedV1(
        event_id=str(uuid.uuid4()),
        employee_id=progress.employee_id,
        module_id=progress.module_id,
        progress_id=str(progress.progress_id),
        completion_status='completed',
        score=score
    )
    bus.publish('progress.updated', progress_event.model_dump())

@register_agent('progress.updated')
async def handle_progress_updated(event_data: dict):
    """
    Progress Monitoring Agent: Tracks completion and flags at-risk employees or reschedules.
    """
    employee_id = event_data.get('employee_id')
    completion_status = event_data.get('completion_status')
    progress_id = event_data.get('progress_id')
    
    logger.info(f"Progress Monitoring Agent: Received progress.updated for {employee_id} ({completion_status})")
    
    if completion_status == 'completed':
        # If they completed a module, check if they have overdue modules and extend deadlines
        overdue_modules = TrainingProgress.objects(
            employee_id=employee_id, 
            completion_status='not_started',
            due_date__lt=datetime.utcnow()
        )
        for p in overdue_modules:
            # Grant a 3-day extension since they are making progress elsewhere
            p.due_date = p.due_date + timedelta(days=3)
            p.updated_at = datetime.utcnow()
            p.save()
            logger.info(f"Progress Monitor: Extended deadline for overdue module {p.module_id} for employee {employee_id}")
