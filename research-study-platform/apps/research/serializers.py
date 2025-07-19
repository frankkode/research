from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction,
    PDFViewingBehavior, QuizResponse, DataExport, ResearcherAccess
)
from apps.core.models import User
from apps.studies.models import StudySession
import random

User = get_user_model()


class ResearchStudySerializer(serializers.ModelSerializer):
    participant_count = serializers.ReadOnlyField()
    completion_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = ResearchStudy
        fields = '__all__'
        read_only_fields = ['created_by']


class ParticipantProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_participant_id = serializers.CharField(source='user.participant_id', read_only=True)
    completion_percentage = serializers.CharField(source='user.completion_percentage', read_only=True)
    
    class Meta:
        model = ParticipantProfile
        fields = [
            'id', 'user', 'user_email', 'user_participant_id', 'study',
            'age_range', 'education_level', 'technical_background',
            'assigned_group', 'assignment_timestamp', 'randomization_seed',
            'consent_given', 'consent_timestamp', 'gdpr_consent',
            'data_processing_consent', 'withdrawn', 'withdrawal_timestamp',
            'withdrawal_reason', 'anonymized_id', 'is_anonymized',
            'completion_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['anonymized_id', 'assignment_timestamp', 'randomization_seed']


class ParticipantCreateSerializer(serializers.Serializer):
    """Serializer for creating new participants"""
    email = serializers.EmailField()
    participant_id = serializers.CharField(max_length=50)
    study_id = serializers.UUIDField()
    assigned_group = serializers.CharField(max_length=20, required=False)
    
    # Optional demographic data
    age_range = serializers.CharField(max_length=20, required=False)
    education_level = serializers.CharField(max_length=50, required=False)
    technical_background = serializers.CharField(max_length=100, required=False)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def validate_participant_id(self, value):
        if User.objects.filter(participant_id=value).exists():
            raise serializers.ValidationError("Participant ID already exists")
        return value
    
    def validate_study_id(self, value):
        try:
            study = ResearchStudy.objects.get(id=value)
            if not study.is_active:
                raise serializers.ValidationError("Study is not active")
            return value
        except ResearchStudy.DoesNotExist:
            raise serializers.ValidationError("Study not found")
    
    def create(self, validated_data):
        study_id = validated_data.pop('study_id')
        study = ResearchStudy.objects.get(id=study_id)
        
        # Create user
        user_data = {
            'email': validated_data['email'],
            'username': validated_data['participant_id'],
            'participant_id': validated_data['participant_id'],
            'study_group': validated_data.get('assigned_group', self._assign_group(study))
        }
        
        user = User.objects.create_user(**user_data)
        
        # Create participant profile
        profile_data = {
            'user': user,
            'study': study,
            'assigned_group': user.study_group,
            'age_range': validated_data.get('age_range', ''),
            'education_level': validated_data.get('education_level', ''),
            'technical_background': validated_data.get('technical_background', ''),
        }
        
        profile = ParticipantProfile.objects.create(**profile_data)
        return profile
    
    def _assign_group(self, study):
        """Auto-assign group based on study configuration"""
        if not study.auto_assign_groups:
            return 'PDF'  # Default group
        
        # Get current distribution
        current_counts = {}
        for group in study.group_balance_ratio.keys():
            current_counts[group] = ParticipantProfile.objects.filter(
                study=study, assigned_group=group
            ).count()
        
        # Calculate target distribution
        total_participants = sum(current_counts.values())
        target_ratios = study.group_balance_ratio
        
        # Find the group that needs more participants
        min_ratio = float('inf')
        selected_group = 'PDF'
        
        for group, target_ratio in target_ratios.items():
            current_ratio = current_counts.get(group, 0) / max(total_participants, 1)
            if current_ratio < target_ratio and current_ratio < min_ratio:
                min_ratio = current_ratio
                selected_group = group
        
        return selected_group


class InteractionLogSerializer(serializers.ModelSerializer):
    participant_id = serializers.CharField(source='participant.anonymized_id', read_only=True)
    
    class Meta:
        model = InteractionLog
        fields = '__all__'


class ChatInteractionSerializer(serializers.ModelSerializer):
    participant_id = serializers.CharField(source='participant.anonymized_id', read_only=True)
    
    class Meta:
        model = ChatInteraction
        fields = '__all__'


class PDFViewingBehaviorSerializer(serializers.ModelSerializer):
    participant_id = serializers.CharField(source='participant.anonymized_id', read_only=True)
    
    class Meta:
        model = PDFViewingBehavior
        fields = '__all__'


class QuizResponseSerializer(serializers.ModelSerializer):
    participant_id = serializers.CharField(source='participant.anonymized_id', read_only=True)
    
    class Meta:
        model = QuizResponse
        fields = '__all__'


class DataExportSerializer(serializers.ModelSerializer):
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    study_name = serializers.CharField(source='study.name', read_only=True)
    
    class Meta:
        model = DataExport
        fields = '__all__'
        read_only_fields = ['requested_by', 'file_path', 'file_size_bytes', 'record_count']


class ResearcherAccessSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    study_name = serializers.CharField(source='study.name', read_only=True)
    granted_by_username = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = ResearcherAccess
        fields = '__all__'
        read_only_fields = ['granted_by', 'granted_at']


class ParticipantStatsSerializer(serializers.Serializer):
    """Serializer for participant statistics"""
    total_participants = serializers.IntegerField()
    completed_participants = serializers.IntegerField()
    active_participants = serializers.IntegerField()
    withdrawn_participants = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    
    # Group distribution
    group_distribution = serializers.DictField()
    
    # Phase completion stats
    consent_completion_rate = serializers.FloatField()
    pre_quiz_completion_rate = serializers.FloatField()
    interaction_completion_rate = serializers.FloatField()
    post_quiz_completion_rate = serializers.FloatField()
    
    # Timing stats
    average_session_duration = serializers.FloatField()
    average_interaction_duration = serializers.FloatField()


class StudyAnalyticsSerializer(serializers.Serializer):
    """Comprehensive study analytics"""
    study_overview = serializers.DictField()
    participant_stats = ParticipantStatsSerializer()
    interaction_stats = serializers.DictField()
    chat_stats = serializers.DictField()
    pdf_stats = serializers.DictField()
    quiz_stats = serializers.DictField()
    timeline_data = serializers.ListField()


class BulkParticipantCreateSerializer(serializers.Serializer):
    """Serializer for bulk participant creation"""
    study_id = serializers.UUIDField()
    participant_count = serializers.IntegerField(min_value=1, max_value=1000)
    group_distribution = serializers.DictField(required=False)
    id_prefix = serializers.CharField(max_length=10, default='P')
    
    def validate_study_id(self, value):
        try:
            study = ResearchStudy.objects.get(id=value)
            if not study.is_active:
                raise serializers.ValidationError("Study is not active")
            return value
        except ResearchStudy.DoesNotExist:
            raise serializers.ValidationError("Study not found")
    
    def create(self, validated_data):
        study_id = validated_data['study_id']
        study = ResearchStudy.objects.get(id=study_id)
        participant_count = validated_data['participant_count']
        id_prefix = validated_data.get('id_prefix', 'P')
        
        # Generate participant IDs
        existing_ids = set(User.objects.values_list('participant_id', flat=True))
        
        participants = []
        for i in range(participant_count):
            # Generate unique participant ID
            participant_id = None
            attempts = 0
            while participant_id is None or participant_id in existing_ids:
                participant_id = f"{id_prefix}{random.randint(10000, 99999)}"
                attempts += 1
                if attempts > 100:
                    raise serializers.ValidationError("Unable to generate unique participant IDs")
            
            existing_ids.add(participant_id)
            
            # Assign group
            assigned_group = self._assign_group(study, len(participants))
            
            # Create user
            user = User.objects.create_user(
                username=participant_id,
                email=f"{participant_id}@study.local",
                participant_id=participant_id,
                study_group=assigned_group
            )
            
            # Create participant profile
            profile = ParticipantProfile.objects.create(
                user=user,
                study=study,
                assigned_group=assigned_group
            )
            
            participants.append(profile)
        
        return participants
    
    def _assign_group(self, study, current_index):
        """Assign group based on study configuration and current index"""
        if not study.auto_assign_groups:
            return 'PDF'
        
        groups = list(study.group_balance_ratio.keys())
        if not groups:
            return 'PDF'
        
        # Simple round-robin assignment
        return groups[current_index % len(groups)]