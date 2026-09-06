from rest_framework import serializers
from common.validators import validate_department_name

class DepartmentSerializer(serializers.Serializer):
    department_id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    manager_employee_id = serializers.CharField(required=False, allow_null=True)
    
    def validate_name(self, value):
        return validate_department_name(value)

class EmployeeSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    department_id = serializers.CharField(max_length=36)
    role = serializers.CharField(max_length=100)
    joining_date = serializers.DateTimeField()
    created_at = serializers.DateTimeField(read_only=True)
