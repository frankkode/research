from rest_framework import serializers
from .models import ChatInteraction, ChatSession


class ChatInteractionSerializer(serializers.ModelSerializer):
    user_participant_id = serializers.CharField(source='user.participant_id', read_only=True)
    
    class Meta:
        model = ChatInteraction
        fields = [
            'id', 'session', 'user', 'user_participant_id', 'message_type',
            'user_message', 'assistant_response', 'message_timestamp',
            'response_time_ms', 'openai_model', 'prompt_tokens', 'completion_tokens',
            'total_tokens', 'conversation_turn', 'user_input_length',
            'response_length', 'contains_question', 'contains_code',
            'topic_category', 'error_message'
        ]
        read_only_fields = [
            'user', 'response_time_ms', 'user_input_length', 'response_length',
            'contains_question', 'contains_code', 'message_timestamp'
        ]


class ChatSessionSerializer(serializers.ModelSerializer):
    user_participant_id = serializers.CharField(source='user.participant_id', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'session', 'user', 'user_participant_id', 'chat_started_at',
            'chat_ended_at', 'total_chat_duration_seconds', 'total_messages',
            'total_user_messages', 'total_assistant_responses', 'total_tokens_used',
            'average_response_time_ms', 'questions_asked', 'code_discussions',
            'error_count'
        ]
        read_only_fields = ['user', 'chat_started_at']


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for sending chat messages"""
    message = serializers.CharField(max_length=5000)
    session_id = serializers.UUIDField()
    conversation_turn = serializers.IntegerField(default=1)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    user_message = serializers.CharField()
    assistant_response = serializers.CharField()
    response_time_ms = serializers.IntegerField()
    total_tokens = serializers.IntegerField()
    conversation_turn = serializers.IntegerField()
    interaction_id = serializers.UUIDField()