import uuid
from datetime import datetime
from mongoengine import Document, StringField, BooleanField, DateTimeField, UUIDField


class ChatLog(Document):
    """
    Persists every chatbot interaction for audit, analytics, and escalation tracking.
    """
    chat_id = UUIDField(primary_key=True, default=uuid.uuid4)
    employee_id = StringField(required=True)  # UUID string ref to Employee
    query_text = StringField(required=True, max_length=2000)
    response_text = StringField(required=True, max_length=5000)
    resolved = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'chat_logs',
        'indexes': ['employee_id', '-created_at'],
        'ordering': ['-created_at'],
    }
