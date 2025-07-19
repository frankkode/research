from django.contrib import admin
from .models import StudySession, StudyLog


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'participant_id', 'study_group', 'session_id', 
        'current_phase', 'is_active', 'is_completed', 'total_duration_minutes',
        'session_started_at'
    )
    list_filter = (
        'current_phase', 'is_active', 'is_completed', 'user__study_group',
        'session_started_at'
    )
    search_fields = ('user__username', 'user__email', 'user__participant_id', 'session_id')
    readonly_fields = ('session_id', 'total_duration', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Session Info', {
            'fields': ('user', 'session_id', 'current_phase', 'is_active', 'is_completed')
        }),
        ('Timing', {
            'fields': (
                'session_started_at', 'session_ended_at', 'total_duration',
                'consent_started_at', 'consent_ended_at', 'consent_duration',
                'pre_quiz_started_at', 'pre_quiz_ended_at', 'pre_quiz_duration',
                'interaction_started_at', 'interaction_ended_at', 'interaction_duration',
                'post_quiz_started_at', 'post_quiz_ended_at', 'post_quiz_duration'
            )
        }),
        ('Metadata', {
            'fields': ('user_agent', 'ip_address', 'created_at', 'updated_at')
        })
    )
    
    def participant_id(self, obj):
        return obj.user.participant_id
    participant_id.short_description = 'Participant ID'
    
    def study_group(self, obj):
        return obj.user.study_group
    study_group.short_description = 'Study Group'
    
    def total_duration_minutes(self, obj):
        return f"{obj.total_duration / 60:.1f} min" if obj.total_duration else "0 min"
    total_duration_minutes.short_description = 'Total Duration'


@admin.register(StudyLog)
class StudyLogAdmin(admin.ModelAdmin):
    list_display = ('session', 'participant_id', 'log_type', 'timestamp')
    list_filter = ('log_type', 'timestamp', 'session__user__study_group')
    search_fields = ('session__user__username', 'session__user__participant_id')
    readonly_fields = ('timestamp',)
    
    def participant_id(self, obj):
        return obj.session.user.participant_id
    participant_id.short_description = 'Participant ID'