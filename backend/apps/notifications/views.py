from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    """
    GET /notifications/ — List current user's notifications
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        employee_id = request.user.employee_id
        if not employee_id:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        notifications = Notification.objects(employee_id=employee_id)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationUnreadCountView(APIView):
    """
    GET /notifications/unread-count/ — For header badge
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        employee_id = request.user.employee_id
        if not employee_id:
            return Response({'count': 0})
            
        count = Notification.objects(employee_id=employee_id, read_status=False).count()
        return Response({'count': count})


class NotificationMarkReadView(APIView):
    """
    PUT /notifications/<id>/read/ — Mark as read
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, notification_id):
        try:
            notification = Notification.objects.get(notification_id=notification_id)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        if str(notification.employee_id) != str(request.user.employee_id):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        notification.read_status = True
        notification.save()
        
        return Response(NotificationSerializer(notification).data)
