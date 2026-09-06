from rest_framework import serializers

class ReportSerializer(serializers.Serializer):
    report_id = serializers.UUIDField(read_only=True)
    report_type = serializers.CharField(read_only=True)
    employee_id = serializers.CharField(read_only=True, required=False, allow_null=True)
    department_id = serializers.CharField(read_only=True, required=False, allow_null=True)
    performance_score = serializers.FloatField(read_only=True)
    completion_percentage = serializers.FloatField(read_only=True)
    metrics = serializers.DictField(read_only=True)
    feedback = serializers.CharField(read_only=True)
    generated_at = serializers.DateTimeField(read_only=True)
