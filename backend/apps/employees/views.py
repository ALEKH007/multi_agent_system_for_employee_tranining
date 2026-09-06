from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from .models import Employee, Department
from .serializers import EmployeeSerializer, DepartmentSerializer
from apps.authentication.permissions import IsHRAdmin, IsOwnerOrHRAdmin
from rest_framework.permissions import IsAuthenticated

# Ensure signals are connected
import apps.employees.signals  # noqa

class DepartmentListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)
        
    def post(self, request):
        # Only HR admins can create departments
        if request.user.role != 'hr_admin':
            raise PermissionDenied("Only HR Admins can create departments.")
            
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            if Department.objects(name=name).first():
                return Response({'detail': 'Department already exists.'}, status=status.HTTP_400_BAD_REQUEST)
                
            department = Department(**serializer.validated_data)
            department.save()
            return Response(DepartmentSerializer(department).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # HR Admins see all, Managers see their department (if implemented), Employees see only themselves
        if request.user.role in ('hr_admin', 'system_admin'):
            employees = Employee.objects.all()
        elif request.user.role == 'manager':
            managed_departments = Department.objects(
                manager_employee_id=str(request.user.employee_id)
            )
            employees = Employee.objects(
                department_id__in=[str(department.department_id) for department in managed_departments]
            )
        else:
            if not request.user.employee_id:
                return Response({'detail': 'No employee profile linked to user.'}, status=status.HTTP_404_NOT_FOUND)
            employees = Employee.objects(employee_id=request.user.employee_id)
            
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
        
    def post(self, request):
        # HR Admins register employees
        if request.user.role != 'hr_admin':
            raise PermissionDenied("Only HR Admins can create employees.")
            
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            if Employee.objects(email=email).first():
                return Response({'detail': 'Employee email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Signal post_save will fire and trigger event bus
            employee = Employee(**serializer.validated_data)
            employee.save()
            return Response(EmployeeSerializer(employee).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrHRAdmin]
    
    def get_object(self, employee_id):
        try:
            return Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return None

    def get(self, request, employee_id):
        employee = self.get_object(employee_id)
        if not employee:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        # Check ownership via IsOwnerOrHRAdmin logic natively inside view
        self.check_object_permissions(request, employee)
        
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)
