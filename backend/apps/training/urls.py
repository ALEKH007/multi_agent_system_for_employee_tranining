from django.urls import path
from .views import TrainingModuleListView, EmployeeTrainingProgressView, UpdateProgressView

urlpatterns = [
    path('modules/', TrainingModuleListView.as_view(), name='training-module-list'),
    path('my-courses/', EmployeeTrainingProgressView.as_view(), name='employee-training-progress'),
    path('progress/<str:progress_id>/', UpdateProgressView.as_view(), name='update-training-progress'),
]
