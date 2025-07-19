from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Study Information', {'fields': ('participant_id', 'study_group')}),
        ('Completion Tracking', {'fields': (
            'consent_completed', 'consent_completed_at',
            'pre_quiz_completed', 'pre_quiz_completed_at',
            'interaction_completed', 'interaction_completed_at',
            'post_quiz_completed', 'post_quiz_completed_at',
            'study_completed', 'study_completed_at'
        )}),
    )
    list_display = (
        'username', 'email', 'participant_id', 'study_group', 
        'consent_completed', 'pre_quiz_completed', 'interaction_completed',
        'post_quiz_completed', 'study_completed', 'is_active', 'date_joined'
    )
    list_filter = (
        'study_group', 'consent_completed', 'pre_quiz_completed',
        'interaction_completed', 'post_quiz_completed', 'study_completed',
        'is_active', 'date_joined'
    )
    search_fields = ('username', 'email', 'participant_id')
    readonly_fields = ('completion_percentage',)
    
    def completion_percentage(self, obj):
        return f"{obj.completion_percentage:.1f}%"
    completion_percentage.short_description = 'Completion %'