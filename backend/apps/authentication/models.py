import uuid
from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, UUIDField
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

class User(Document):
    """
    User model for authentication and RBAC.
    Separate from Employee profile to allow HR/Admin accounts without employee records.
    """
    ROLE_CHOICES = ('employee', 'hr_admin', 'manager', 'system_admin')
    
    user_id = UUIDField(primary_key=True, default=uuid.uuid4)
    email = StringField(required=True, unique=True, max_length=255)
    password_hash = StringField(required=True)
    role = StringField(required=True, choices=ROLE_CHOICES, default='employee')
    
    # Store employee_id as a string/uuid representation instead of direct reference 
    # to avoid circular imports. It links to the Employee document.
    employee_id = StringField(null=True)
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'users',
        'indexes': ['email']
    }

    def set_password(self, raw_password: str):
        """Hashes password using Argon2 memory-hard algorithm."""
        self.password_hash = ph.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verifies an Argon2 hashed password."""
        try:
            return ph.verify(self.password_hash, raw_password)
        except VerifyMismatchError:
            return False
