import uuid
from datetime import datetime
from mongoengine import Document, StringField, BooleanField, DateTimeField, UUIDField

class Notification(Document):
    """
    In-app notification for employees and managers.
    """
    notification_id = UUIDField(primary_key=True, default=uuid.uuid4)
    employee_id = StringField(required=True)  # UUID string ref to Employee
    message = StringField(required=True, max_length=500)
    type = StringField(choices=('reminder', 'alert', 'system'), default='system')
    
    read_status = BooleanField(default=False)
    sent_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'notifications',
        'indexes': ['employee_id', 'read_status', '-sent_at'],
        'ordering': ['-sent_at'],
    }
