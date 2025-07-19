from rest_framework import serializers
from .models import StudySession, StudyLog


class StudySessionSerializer(serializers.ModelSerializer):
    user_participant_id = serializers.CharField(source='user.participant_id', read_only=True)
    user_study_group = serializers.CharField(source='user.study_group', read_only=True)
    
    class Meta:
        model = StudySession
        fields = [
            'id', 'user', 'user_participant_id', 'user_study_group', 'session_id', 
            'current_phase', 'session_started_at', 'session_ended_at',
            'consent_started_at', 'consent_ended_at', 'consent_duration',
            'pre_quiz_started_at', 'pre_quiz_ended_at', 'pre_quiz_duration',
            'interaction_started_at', 'interaction_ended_at', 'interaction_duration',
            'post_quiz_started_at', 'post_quiz_ended_at', 'post_quiz_duration',
            'total_duration', 'is_active', 'is_completed'
        ]
        read_only_fields = ['user', 'session_id', 'total_duration']


class StudyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyLog
        fields = ['id', 'session', 'log_type', 'event_data', 'timestamp']
        read_only_fields = ['timestamp']


class PhaseUpdateSerializer(serializers.Serializer):
    phase = serializers.ChoiceField(choices=StudySession.PHASE_CHOICES)
    timestamp = serializers.DateTimeField(required=False)


class SessionCreateSerializer(serializers.Serializer):
    user_agent = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.IPAddressField(required=False, allow_null=True)