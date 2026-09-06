from rest_framework import serializers

class TrainingModuleSerializer(serializers.Serializer):
    module_id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=100)
    difficulty = serializers.ChoiceField(choices=['beginner', 'intermediate', 'advanced'])
    duration_minutes = serializers.FloatField()
    content_url = serializers.URLField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

class TrainingProgressSerializer(serializers.Serializer):
    progress_id = serializers.UUIDField(read_only=True)
    employee_id = serializers.CharField(read_only=True)
    module_id = serializers.CharField(read_only=True)
    plan_id = serializers.CharField(read_only=True)
    completion_status = serializers.ChoiceField(choices=['not_started', 'in_progress', 'completed', 'overdue'])
    score = serializers.FloatField(required=False, allow_null=True)
    assigned_at = serializers.DateTimeField(read_only=True)
    due_date = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
