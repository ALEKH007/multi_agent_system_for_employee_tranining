import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.authentication.models import User

def create_user(email, role):
    if not User.objects(email=email).first():
        user = User(email=email, role=role)
        user.set_password('Admin@12345')
        user.save()
        print(f"Created {email}")
    else:
        print(f"User {email} already exists")

create_user('employee@company.com', 'employee')
create_user('manager@company.com', 'manager')
create_user('hr@company.com', 'hr_admin')
print("Demo users seeded.")
