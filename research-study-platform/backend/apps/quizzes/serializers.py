from rest_framework import serializers
from .models import Quiz, Question, QuestionChoice, QuizAttempt, QuizResponse


class QuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = ['id', 'choice_text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    choices = QuestionChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'order', 'is_required', 'choices', 'points', 'explanation']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'quiz_type', 'time_limit_minutes', 'questions', 'randomize_questions']


class QuizResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResponse
        fields = ['question', 'selected_choice', 'text_answer', 'numeric_answer']


class QuizAttemptSerializer(serializers.ModelSerializer):
    responses = QuizResponseSerializer(many=True, read_only=True)
    user_participant_id = serializers.CharField(source='user.participant_id', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'user', 'user_participant_id', 'session',
            'started_at', 'completed_at', 'submitted_at', 'time_taken_seconds',
            'is_completed', 'is_submitted', 'is_timed_out', 'score', 'max_score',
            'percentage_score', 'question_order', 'time_remaining', 'responses'
        ]
        read_only_fields = ['user', 'started_at', 'score', 'max_score', 'percentage_score']
    
    def get_time_remaining(self, obj):
        return obj.get_time_remaining()


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for quiz submission"""
    responses = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )


class QuizStartSerializer(serializers.Serializer):
    """Serializer for starting a quiz"""
    session_id = serializers.UUIDField()