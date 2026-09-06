from django.urls import path
from .views import (
    AssessmentListView,
    AssessmentDetailView,
    SubmitAssessmentView,
    AssessmentResultView,
    AssessmentTemplateListView,
)

urlpatterns = [
    path('', AssessmentListView.as_view(), name='assessment-list'),
    path('templates/', AssessmentTemplateListView.as_view(), name='assessment-template-list'),
    path('<str:assessment_id>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('<str:assessment_id>/submit/', SubmitAssessmentView.as_view(), name='assessment-submit'),
    path('<str:assessment_id>/result/', AssessmentResultView.as_view(), name='assessment-result'),
]
