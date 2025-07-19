from rest_framework import serializers
from .models import PDFDocument, PDFInteraction, PDFSession


class PDFDocumentSerializer(serializers.ModelSerializer):
    """Serializer for PDF documents"""
    
    class Meta:
        model = PDFDocument
        fields = [
            'id', 'title', 'description', 'file_path', 'file_size_bytes',
            'page_count', 'is_active', 'study_group', 'display_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PDFInteractionSerializer(serializers.ModelSerializer):
    """Serializer for PDF interactions"""
    
    user_participant_id = serializers.CharField(source='user.participant_id', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    session_id = serializers.CharField(source='session.session_id', read_only=True)
    
    class Meta:
        model = PDFInteraction
        fields = [
            'id', 'session', 'session_id', 'user', 'user_participant_id',
            'document', 'document_title', 'interaction_type', 'timestamp',
            'page_number', 'total_pages', 'viewport_width', 'viewport_height',
            'scroll_x', 'scroll_y', 'zoom_level', 'time_on_page_seconds',
            'cumulative_time_seconds', 'search_query', 'highlighted_text',
            'annotation_text', 'copied_text', 'reading_speed_wpm',
            'dwell_time_ms', 'user_agent', 'screen_resolution'
        ]
        read_only_fields = ['timestamp', 'user']


class PDFSessionSerializer(serializers.ModelSerializer):
    """Serializer for PDF sessions"""
    
    user_participant_id = serializers.CharField(source='user.participant_id', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    session_id = serializers.CharField(source='session.session_id', read_only=True)
    reading_pattern = serializers.SerializerMethodField()
    session_duration_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = PDFSession
        fields = [
            'id', 'session', 'session_id', 'user', 'user_participant_id',
            'document', 'document_title', 'pdf_started_at', 'pdf_ended_at',
            'total_session_duration_seconds', 'session_duration_formatted',
            'active_reading_time_seconds', 'idle_time_seconds',
            'pages_visited', 'unique_pages_visited', 'total_page_views',
            'reading_completion_percentage', 'total_interactions',
            'scroll_interactions', 'zoom_interactions', 'search_interactions',
            'average_time_per_page_seconds', 'longest_page_time_seconds',
            'shortest_page_time_seconds', 'text_selections', 'annotations_made',
            'searches_performed', 'forward_navigation_count',
            'backward_navigation_count', 'jump_navigation_count',
            'focus_changes', 'times_returned_to_pdf', 'reading_pattern'
        ]
        read_only_fields = ['pdf_started_at', 'user']
    
    def get_reading_pattern(self, obj):
        """Get reading pattern analysis"""
        return obj.get_reading_pattern()
    
    def get_session_duration_formatted(self, obj):
        """Get formatted session duration"""
        if obj.total_session_duration_seconds:
            minutes = obj.total_session_duration_seconds // 60
            seconds = obj.total_session_duration_seconds % 60
            return f"{minutes}m {seconds}s"
        return "0m 0s"


class PDFInteractionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PDF interactions"""
    
    session_id = serializers.CharField()
    document_id = serializers.IntegerField()
    
    class Meta:
        model = PDFInteraction
        fields = [
            'session_id', 'document_id', 'interaction_type', 'page_number',
            'total_pages', 'viewport_width', 'viewport_height', 'scroll_x',
            'scroll_y', 'zoom_level', 'time_on_page_seconds',
            'cumulative_time_seconds', 'search_query', 'highlighted_text',
            'annotation_text', 'copied_text', 'reading_speed_wpm',
            'dwell_time_ms', 'screen_resolution'
        ]
    
    def validate_interaction_type(self, value):
        """Validate interaction type"""
        valid_types = [choice[0] for choice in PDFInteraction.INTERACTION_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid interaction type. Must be one of: {', '.join(valid_types)}"
            )
        return value


class PDFSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PDF sessions"""
    
    session_id = serializers.CharField()
    document_id = serializers.IntegerField()
    
    class Meta:
        model = PDFSession
        fields = ['session_id', 'document_id', 'screen_resolution']


class PDFAnalyticsSerializer(serializers.Serializer):
    """Serializer for PDF analytics data"""
    
    total_sessions = serializers.IntegerField()
    completed_sessions = serializers.IntegerField()
    total_reading_time_seconds = serializers.IntegerField()
    average_reading_time_per_session = serializers.FloatField()
    document_statistics = serializers.DictField()
    
    # Reading behavior metrics
    average_completion_percentage = serializers.FloatField(required=False)
    total_interactions = serializers.IntegerField(required=False)
    most_common_interaction_types = serializers.ListField(required=False)
    
    # Navigation patterns
    sequential_readers = serializers.IntegerField(required=False)
    jumping_readers = serializers.IntegerField(required=False)
    mixed_readers = serializers.IntegerField(required=False)
    
    # Engagement metrics
    total_annotations = serializers.IntegerField(required=False)
    total_searches = serializers.IntegerField(required=False)
    total_text_selections = serializers.IntegerField(required=False)


class PDFDocumentStatisticsSerializer(serializers.Serializer):
    """Serializer for document-level statistics"""
    
    document_id = serializers.IntegerField()
    document_title = serializers.CharField()
    total_sessions = serializers.IntegerField()
    unique_users = serializers.IntegerField()
    average_completion_percentage = serializers.FloatField()
    average_reading_time_seconds = serializers.FloatField()
    total_interactions = serializers.IntegerField()
    most_visited_pages = serializers.ListField()
    average_time_per_page = serializers.FloatField()
    
    # Engagement metrics
    total_annotations = serializers.IntegerField()
    total_searches = serializers.IntegerField()
    total_text_selections = serializers.IntegerField()
    
    # Reading patterns
    reading_pattern_distribution = serializers.DictField()
    navigation_pattern_distribution = serializers.DictField()