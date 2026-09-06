import uuid
from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, UUIDField

class Department(Document):
    department_id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = StringField(required=True, unique=True, max_length=100)
    manager_employee_id = StringField(null=True) # Reference to Employee.employee_id
    
    meta = {
        'collection': 'departments',
    }

class Employee(Document):
    employee_id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = StringField(required=True, max_length=255)
    email = StringField(required=True, unique=True, max_length=255)
    
    # Store references as strings (UUID strings) to avoid tight coupling/circular deps in some cases
    department_id = StringField(required=True)
    role = StringField(required=True, max_length=100)
    joining_date = DateTimeField(required=True)
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'employees',
        'indexes': ['email', 'department_id']
    }
