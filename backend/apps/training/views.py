import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.authentication.permissions import IsOwnerOrHRAdmin, IsHRAdmin
from .models import TrainingModule, TrainingProgress
from .serializers import TrainingModuleSerializer, TrainingProgressSerializer
from .tasks import process_training_completion


class TrainingModuleListView(APIView):
    """
    GET /training/modules/ — List all modules (filterable by category, difficulty)
    POST /training/modules/ — HR creates new training modules
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        category = request.query_params.get('category')
        difficulty = request.query_params.get('difficulty')
        
        query = {}
        if category:
            query['category'] = category
        if difficulty:
            query['difficulty'] = difficulty
            
        modules = TrainingModule.objects(**query)
        serializer = TrainingModuleSerializer(modules, many=True)
        return Response(serializer.data)
        
    def post(self, request):
        # Only HR admins can create modules
        if request.user.role not in ('hr_admin', 'system_admin'):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        serializer = TrainingModuleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # Manually extract since we used a simple Serializer not ModelSerializer
        module = TrainingModule(**serializer.validated_data)
        
        # Make sure an ID is generated if not provided, for this simple implementation
        # we'll use a UUID if the client didn't provide a module_id
        if 'module_id' not in serializer.validated_data or not serializer.validated_data['module_id']:
            import uuid
            module.module_id = f"m-{uuid.uuid4().hex[:8]}"
            
        module.save()
        
        return Response(
            TrainingModuleSerializer(module).data,
            status=status.HTTP_201_CREATED
        )


class EmployeeTrainingProgressView(APIView):
    """
    GET /training/my-courses/ — Employee's assigned courses with progress
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        employee_id = request.user.employee_id
        if not employee_id:
            return Response(
                {'detail': 'No employee profile linked.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Get progress records
        progress_records = TrainingProgress.objects(employee_id=employee_id).order_by('due_date')
        
        # For a richer API response, we could attach module details here.
        # But for simplicity, we'll return the progress records as they contain module_id.
        serializer = TrainingProgressSerializer(progress_records, many=True)
        return Response(serializer.data)


class UpdateProgressView(APIView):
    """
    PUT /training/progress/<progress_id>/
    Allows employee to mark completion and submit a score.
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, progress_id):
        try:
            progress = TrainingProgress.objects.get(progress_id=progress_id)
        except TrainingProgress.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        # Ownership check
        if str(progress.employee_id) != str(request.user.employee_id):
            return Response(
                {'detail': 'You can only update your own progress.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        if progress.completion_status == 'completed':
            return Response(
                {'detail': 'Training already marked as completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        new_status = request.data.get('completion_status')
        score = request.data.get('score')
        
        if new_status == 'in_progress':
            progress.completion_status = 'in_progress'
            import datetime, uuid
            from agents.event_bus import EventBus
            from agents.event_schemas import ProgressUpdatedV1
            
            progress.updated_at = datetime.datetime.utcnow()
            progress.save()
            
            bus = EventBus()
            event = ProgressUpdatedV1(
                event_id=str(uuid.uuid4()),
                employee_id=progress.employee_id,
                module_id=progress.module_id,
                progress_id=str(progress.progress_id),
                completion_status='in_progress'
            )
            bus.publish('progress.updated', event.model_dump())
            
            return Response(TrainingProgressSerializer(progress).data)
            
        elif new_status == 'completed':
            # Publish event asynchronously via tasks helper
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        loop.run_in_executor(
                            pool,
                            lambda: asyncio.run(process_training_completion(str(progress_id), score))
                        )
                else:
                    loop.run_until_complete(process_training_completion(str(progress_id), score))
            except RuntimeError:
                asyncio.run(process_training_completion(str(progress_id), score))
                
            progress.reload()
            return Response(TrainingProgressSerializer(progress).data)
            
        return Response(
            {'detail': 'Invalid status update.'},
            status=status.HTTP_400_BAD_REQUEST
        )
