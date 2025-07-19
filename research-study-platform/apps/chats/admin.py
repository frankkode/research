from django.contrib import admin
from .models import ChatInteraction, ChatSession


@admin.register(ChatInteraction)
class ChatInteractionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'participant_id', 'conversation_turn', 'message_type', 
        'message_preview', 'response_time_ms', 'total_tokens', 'estimated_cost_usd',
        'contains_linux_command', 'rate_limit_hit', 'message_timestamp'
    )
    list_filter = (
        'message_type', 'message_timestamp', 'user__study_group',
        'contains_question', 'contains_code', 'contains_linux_command',
        'rate_limit_hit', 'openai_model'
    )
    search_fields = ('user__username', 'user__participant_id', 'user_message', 'assistant_response')
    readonly_fields = ('message_timestamp', 'user_input_length', 'response_length')
    
    fieldsets = (
        ('Interaction Info', {
            'fields': ('session', 'user', 'message_type', 'conversation_turn', 'message_timestamp')
        }),
        ('Message Content', {
            'fields': ('user_message', 'assistant_response', 'error_message')
        }),
        ('Performance Metrics', {
            'fields': ('response_time_ms', 'openai_model', 'prompt_tokens', 'completion_tokens', 'total_tokens')
        }),
        ('Analysis', {
            'fields': (
                'user_input_length', 'response_length', 'contains_question', 
                'contains_code', 'contains_linux_command', 'topic_category', 
                'interaction_quality_score'
            )
        }),
        ('Cost & Rate Limiting', {
            'fields': (
                'estimated_cost_usd', 'api_request_id', 'rate_limit_hit', 'retry_count'
            )
        })
    )
    
    def participant_id(self, obj):
        return obj.user.participant_id
    participant_id.short_description = 'Participant ID'
    
    def message_preview(self, obj):
        if obj.user_message:
            return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message
        return obj.assistant_response[:50] + '...' if obj.assistant_response and len(obj.assistant_response) > 50 else obj.assistant_response
    message_preview.short_description = 'Message Preview'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'participant_id', 'total_messages', 'total_tokens_used',
        'total_estimated_cost_usd', 'linux_command_queries', 'average_response_time_ms', 
        'rate_limit_hits', 'chat_started_at'
    )
    list_filter = ('chat_started_at', 'user__study_group')
    search_fields = ('user__username', 'user__participant_id')
    readonly_fields = ('chat_started_at', 'total_chat_duration_seconds')
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session', 'user', 'chat_started_at', 'chat_ended_at', 'total_chat_duration_seconds')
        }),
        ('Message Statistics', {
            'fields': ('total_messages', 'total_user_messages', 'total_assistant_responses')
        }),
        ('Token Usage', {
            'fields': ('total_tokens_used', 'total_prompt_tokens', 'total_completion_tokens')
        }),
        ('Performance', {
            'fields': ('average_response_time_ms', 'longest_response_time_ms', 'shortest_response_time_ms')
        }),
        ('Engagement', {
            'fields': ('questions_asked', 'code_discussions', 'error_count')
        })
    )
    
    def participant_id(self, obj):
        return obj.user.participant_id
    participant_id.short_description = 'Participant ID'