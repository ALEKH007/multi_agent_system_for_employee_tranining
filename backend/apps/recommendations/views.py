from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.authentication.permissions import IsOwnerOrHRAdmin, IsHRAdmin
from .models import LearningPlan
from .serializers import LearningPlanSerializer
from apps.employees.models import Department, Employee


def managed_employee_ids(manager_employee_id):
    managed_department_ids = [
        str(department.department_id)
        for department in Department.objects(manager_employee_id=str(manager_employee_id))
    ]
    return [
        str(employee.employee_id)
        for employee in Employee.objects(department_id__in=managed_department_ids)
    ]

class LearningPlanListView(APIView):
    """
    GET /recommendations/?employee_id=<uuid>
    Returns all learning plans for the given employee.
    Employees can only see their own. HR/Managers can see any.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        employee_id = request.query_params.get('employee_id')
        
        if request.user.role in ('hr_admin', 'system_admin'):
            if employee_id:
                plans = LearningPlan.objects(employee_id=employee_id)
            else:
                plans = LearningPlan.objects.all()
        elif request.user.role == 'manager':
            plans = LearningPlan.objects(
                employee_id__in=managed_employee_ids(request.user.employee_id)
            )
        else:
            own_employee_id = request.user.employee_id
            if not own_employee_id:
                return Response(
                    {'detail': 'No employee profile linked.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            # Override to only show their own
            plans = LearningPlan.objects(employee_id=own_employee_id)
            
        serializer = LearningPlanSerializer(plans, many=True)
        return Response(serializer.data)

class LearningPlanDetailView(APIView):
    """
    GET /recommendations/<plan_id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, plan_id):
        try:
            plan = LearningPlan.objects.get(plan_id=plan_id)
        except LearningPlan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        # Ownership check
        if request.user.role == 'manager':
            if str(plan.employee_id) not in managed_employee_ids(request.user.employee_id):
                return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role not in ('hr_admin', 'system_admin'):
            if str(plan.employee_id) != str(request.user.employee_id):
                return Response(
                    {'detail': 'Permission denied.'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
        serializer = LearningPlanSerializer(plan)
        return Response(serializer.data)
