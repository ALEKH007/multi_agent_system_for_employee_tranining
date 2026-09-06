from rest_framework import serializers

class RecommendedModuleSerializer(serializers.Serializer):
    module_id = serializers.CharField()
    reasoning = serializers.CharField()

class LearningPlanSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField(read_only=True)
    employee_id = serializers.CharField(read_only=True)
    assessment_id = serializers.CharField(read_only=True)
    recommended_modules = RecommendedModuleSerializer(many=True, read_only=True)
    created_by_model = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
