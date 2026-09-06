from django.urls import path
from .views import EmployeeListView, EmployeeDetailView, DepartmentListView

urlpatterns = [
    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path('', EmployeeListView.as_view(), name='employee-list'),
    path('<str:employee_id>/', EmployeeDetailView.as_view(), name='employee-detail'),
]
