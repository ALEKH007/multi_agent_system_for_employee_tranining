import uuid
from datetime import datetime, timedelta
from mongoengine import Document, StringField, DateTimeField, UUIDField, FloatField

class TrainingModule(Document):
    """
    Represents a training module or course in the catalog.
    """
    DIFFICULTY_CHOICES = ('beginner', 'intermediate', 'advanced')

    module_id = StringField(primary_key=True)  # Keeping it simple like 'm1', 'm2' for now, or UUIDs
    title = StringField(required=True, max_length=255)
    category = StringField(required=True, max_length=100)
    difficulty = StringField(choices=DIFFICULTY_CHOICES, default='intermediate')
    duration_minutes = FloatField(default=60.0)
    content_url = StringField(required=False)
    description = StringField(max_length=1000, default='')

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'training_modules',
        'indexes': ['category']
    }

class TrainingProgress(Document):
    """
    Tracks an employee's progress on an assigned training module.
    """
    STATUS_CHOICES = ('not_started', 'in_progress', 'completed', 'overdue')

    progress_id = UUIDField(primary_key=True, default=uuid.uuid4)
    employee_id = StringField(required=True)  # UUID string ref to Employee
    module_id = StringField(required=True)  # Ref to TrainingModule.module_id
    plan_id = StringField(required=True) # Ref to LearningPlan that recommended this
    
    completion_status = StringField(choices=STATUS_CHOICES, default='not_started')
    score = FloatField(null=True)  # Optional score if module has a quiz
    
    assigned_at = DateTimeField(default=datetime.utcnow)
    due_date = DateTimeField(required=True)
    completed_at = DateTimeField(null=True)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'training_progress',
        'indexes': ['employee_id', 'module_id', 'completion_status'],
    }
