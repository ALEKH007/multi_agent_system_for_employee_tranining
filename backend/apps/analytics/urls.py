from django.urls import path
from .views import DashboardMetricsView, DepartmentMetricsView, EmployeeReportView, ReportListView

urlpatterns = [
    path('dashboard/', DashboardMetricsView.as_view(), name='analytics-dashboard'),
    path('department/<str:department_id>/', DepartmentMetricsView.as_view(), name='analytics-department'),
    path('employee/<str:employee_id>/', EmployeeReportView.as_view(), name='analytics-employee'),
    path('reports/', ReportListView.as_view(), name='analytics-reports'),
]
