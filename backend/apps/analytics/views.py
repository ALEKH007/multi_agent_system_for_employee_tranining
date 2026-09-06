from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Report
from .serializers import ReportSerializer
from apps.employees.models import Department, Employee


def manages_department(user, department_id):
    return bool(
        user.role == 'manager' and Department.objects(
            department_id=department_id,
            manager_employee_id=str(user.employee_id),
        ).first()
    )


class DashboardMetricsView(APIView):
    """
    GET /analytics/dashboard/ — Org-wide metrics (HR/admin only)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role not in ('hr_admin', 'system_admin'):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        # Get the latest org report
        report = Report.objects(report_type='org').order_by('-generated_at').first()
        if not report:
            # Fallback if no report exists yet
            return Response({
                'performance_score': 0,
                'completion_percentage': 0,
                'metrics': {
                    'total_employees': 0,
                    'onboarding_in_progress': 0,
                    'chatbot_queries': 0
                },
                'feedback': 'No data available yet.'
            })
            
        serializer = ReportSerializer(report)
        return Response(serializer.data)


class DepartmentMetricsView(APIView):
    """
    GET /analytics/department/<id>/ — Department metrics (manager/HR)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, department_id):
        if request.user.role not in ('hr_admin', 'system_admin', 'manager'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.user.role == 'manager':
            if department_id == 'me':
                department = Department.objects(
                    manager_employee_id=str(request.user.employee_id)
                ).first()
                if not department:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                department_id = str(department.department_id)
            elif not manages_department(request.user, department_id):
                return Response(status=status.HTTP_403_FORBIDDEN)
            
        report = Report.objects(report_type='department', department_id=department_id).order_by('-generated_at').first()
        if not report:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        serializer = ReportSerializer(report)
        return Response(serializer.data)


class EmployeeReportView(APIView):
    """
    GET /analytics/employee/<id>/ — Individual report
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, employee_id):
        if request.user.role == 'manager':
            employee = Employee.objects(employee_id=employee_id).first()
            if not employee or not manages_department(request.user, employee.department_id):
                return Response(status=status.HTTP_403_FORBIDDEN)
        elif request.user.role not in ('hr_admin', 'system_admin'):
            if str(request.user.employee_id) != str(employee_id):
                return Response(status=status.HTTP_403_FORBIDDEN)
                
        report = Report.objects(report_type='individual', employee_id=employee_id).order_by('-generated_at').first()
        if not report:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        serializer = ReportSerializer(report)
        return Response(serializer.data)


class ReportListView(APIView):
    """
    GET /analytics/reports/ — List generated reports
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role not in ('hr_admin', 'system_admin'):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        reports = Report.objects().order_by('-generated_at')[:50]
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)
