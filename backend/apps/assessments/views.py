import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.authentication.permissions import IsOwnerOrHRAdmin, IsHRAdmin
from .models import SkillAssessment, AssessmentTemplate
from .serializers import (
    SkillAssessmentListSerializer,
    SkillAssessmentDetailSerializer,
    SubmitAssessmentSerializer,
    AssessmentTemplateSerializer,
)
from .tasks import process_assessment_submission
import logging

logger = logging.getLogger(__name__)


class AssessmentListView(APIView):
    """
    GET  /assessments/?employee_id=<uuid>  — List assessments.
    Employees see only their own; HR sees all or filters by employee_id.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        employee_id = request.query_params.get('employee_id')
        
        if request.user.role == 'hr_admin':
            # HR can list all or filter
            if employee_id:
                assessments = SkillAssessment.objects(employee_id=employee_id)
            else:
                assessments = SkillAssessment.objects.all()
        else:
            # Employees see only their own
            own_employee_id = request.user.employee_id
            if not own_employee_id:
                return Response(
                    {'detail': 'No employee profile linked.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            assessments = SkillAssessment.objects(employee_id=own_employee_id)
        
        serializer = SkillAssessmentListSerializer(assessments, many=True)
        return Response(serializer.data)


class AssessmentDetailView(APIView):
    """
    GET /assessments/<assessment_id>/  — View assessment detail (questions + results).
    Questions are returned WITHOUT correct answers (handled by serializer).
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, assessment_id):
        try:
            assessment = SkillAssessment.objects.get(assessment_id=assessment_id)
        except SkillAssessment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Ownership check: employees can only view their own assessments
        if request.user.role not in ('hr_admin', 'system_admin'):
            if str(assessment.employee_id) != str(request.user.employee_id):
                return Response(
                    {'detail': 'You do not have permission to view this assessment.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = SkillAssessmentDetailSerializer(assessment)
        return Response(serializer.data)


class SubmitAssessmentView(APIView):
    """
    POST /assessments/<assessment_id>/submit/  — Submit answers for an assessment.
    Only the owning employee can submit. Assessment must be in 'pending' or 'in_progress' status.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, assessment_id):
        try:
            assessment = SkillAssessment.objects.get(assessment_id=assessment_id)
        except SkillAssessment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Only the owning employee can submit
        if str(assessment.employee_id) != str(request.user.employee_id):
            return Response(
                {'detail': 'You can only submit your own assessments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check status
        if assessment.status not in ('pending', 'in_progress'):
            return Response(
                {'detail': f'Assessment is already {assessment.status}. Cannot resubmit.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubmitAssessmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Save answers
        assessment.answers = serializer.validated_data['answers']
        assessment.status = 'in_progress'
        assessment.save()
        
        # Score and publish event (runs the scoring engine + event bus publish)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    results = loop.run_in_executor(
                        pool,
                        lambda: asyncio.run(process_assessment_submission(str(assessment.assessment_id)))
                    )
            else:
                results = loop.run_until_complete(
                    process_assessment_submission(str(assessment.assessment_id))
                )
        except RuntimeError:
            # No event loop — create one
            results = asyncio.run(
                process_assessment_submission(str(assessment.assessment_id))
            )
        
        # Re-fetch the updated assessment
        assessment.reload()
        detail_serializer = SkillAssessmentDetailSerializer(assessment)
        return Response(detail_serializer.data, status=status.HTTP_200_OK)


class AssessmentResultView(APIView):
    """
    GET /assessments/<assessment_id>/result/  — View the gap analysis report.
    Only for completed assessments.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, assessment_id):
        try:
            assessment = SkillAssessment.objects.get(assessment_id=assessment_id)
        except SkillAssessment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Ownership check
        if request.user.role not in ('hr_admin', 'system_admin', 'manager'):
            if str(assessment.employee_id) != str(request.user.employee_id):
                return Response(
                    {'detail': 'Permission denied.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if assessment.status != 'completed':
            return Response(
                {'detail': 'Assessment has not been completed yet.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'assessment_id': str(assessment.assessment_id),
            'employee_id': assessment.employee_id,
            'title': assessment.title,
            'skill_score': assessment.skill_score,
            'max_score': assessment.max_score,
            'weak_areas': assessment.weak_areas,
            'strong_areas': assessment.strong_areas,
            'category_scores': assessment.category_scores,
            'completed_at': assessment.completed_at,
        })


class AssessmentTemplateListView(APIView):
    """
    GET  /assessments/templates/         — List templates (HR only).
    POST /assessments/templates/         — Create a template (HR only).
    """
    permission_classes = [IsAuthenticated, IsHRAdmin]
    
    def get(self, request):
        templates = AssessmentTemplate.objects.all()
        serializer = AssessmentTemplateSerializer(templates, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AssessmentTemplateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        template = AssessmentTemplate(**serializer.validated_data)
        template.save()
        return Response(
            AssessmentTemplateSerializer(template).data,
            status=status.HTTP_201_CREATED
        )
