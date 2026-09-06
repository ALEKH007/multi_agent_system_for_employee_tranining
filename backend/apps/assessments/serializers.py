from rest_framework import serializers


class QuestionSerializer(serializers.Serializer):
    """Serializer for individual assessment questions."""
    question_id = serializers.CharField(max_length=50)
    text = serializers.CharField(max_length=1000)
    options = serializers.ListField(child=serializers.CharField(max_length=500))
    # correct_answer is NEVER returned to the client
    category = serializers.CharField(max_length=100)


class AnswerSerializer(serializers.Serializer):
    """Serializer for submitted answers."""
    question_id = serializers.CharField(max_length=50)
    selected_answer = serializers.CharField(max_length=500)


class SkillAssessmentListSerializer(serializers.Serializer):
    """Lightweight serializer for listing assessments."""
    assessment_id = serializers.UUIDField(read_only=True)
    employee_id = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    skill_score = serializers.FloatField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)


class SkillAssessmentDetailSerializer(serializers.Serializer):
    """Full serializer for assessment detail (includes questions, but NOT correct answers)."""
    assessment_id = serializers.UUIDField(read_only=True)
    employee_id = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    skill_score = serializers.FloatField(read_only=True)
    max_score = serializers.FloatField(read_only=True)
    weak_areas = serializers.ListField(child=serializers.CharField(), read_only=True)
    strong_areas = serializers.ListField(child=serializers.CharField(), read_only=True)
    category_scores = serializers.DictField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)


class SubmitAssessmentSerializer(serializers.Serializer):
    """Serializer for submitting assessment answers."""
    answers = AnswerSerializer(many=True)


class AssessmentTemplateSerializer(serializers.Serializer):
    """Serializer for assessment templates."""
    template_id = serializers.UUIDField(read_only=True)
    role = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    questions = QuestionSerializer(many=True, required=False)
    difficulty = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced'],
        default='intermediate'
    )
    time_limit_minutes = serializers.IntegerField(default=30)
    categories = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
