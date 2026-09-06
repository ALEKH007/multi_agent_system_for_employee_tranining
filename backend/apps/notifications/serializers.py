from rest_framework import serializers

class NotificationSerializer(serializers.Serializer):
    notification_id = serializers.UUIDField(read_only=True)
    employee_id = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    read_status = serializers.BooleanField(read_only=True)
    sent_at = serializers.DateTimeField(read_only=True)
