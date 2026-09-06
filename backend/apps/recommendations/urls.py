from django.urls import path
from .views import LearningPlanListView, LearningPlanDetailView

urlpatterns = [
    path('', LearningPlanListView.as_view(), name='learning-plan-list'),
    path('<str:plan_id>/', LearningPlanDetailView.as_view(), name='learning-plan-detail'),
]
