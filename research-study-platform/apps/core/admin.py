from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import transaction
from django.contrib import messages
import logging
from .models import User

logger = logging.getLogger(__name__)


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
    
    def delete_queryset(self, request, queryset):
        """Override bulk delete to ensure proper deletion"""
        count = queryset.count()
        user_emails = list(queryset.values_list('email', flat=True))
        
        logger.info(f"Admin deleting {count} users: {user_emails}")
        
        try:
            with transaction.atomic():
                # Force delete each user individually to handle cascading
                deleted_count = 0
                for user in queryset:
                    user_id = user.id
                    user_email = user.email
                    logger.info(f"Deleting user: {user_email} ({user_id})")
                    
                    # Delete the user
                    user.delete()
                    deleted_count += 1
                    
                    # Verify deletion
                    if User.objects.filter(id=user_id).exists():
                        logger.error(f"Failed to delete user {user_email}")
                        raise Exception(f"Failed to delete user {user_email}")
                    else:
                        logger.info(f"Successfully deleted user {user_email}")
                
                messages.success(request, f'Successfully deleted {deleted_count} users: {", ".join(user_emails)}')
                
        except Exception as e:
            logger.error(f"Error deleting users: {str(e)}")
            messages.error(request, f'Error deleting users: {str(e)}')
            raise
    
    def delete_model(self, request, obj):
        """Override single delete to ensure proper deletion"""
        user_id = obj.id
        user_email = obj.email
        
        logger.info(f"Admin deleting single user: {user_email} ({user_id})")
        
        try:
            with transaction.atomic():
                obj.delete()
                
                # Verify deletion
                if User.objects.filter(id=user_id).exists():
                    logger.error(f"Failed to delete user {user_email}")
                    messages.error(request, f'Failed to delete user {user_email}')
                    raise Exception(f"Failed to delete user {user_email}")
                else:
                    logger.info(f"Successfully deleted user {user_email}")
                    messages.success(request, f'Successfully deleted user {user_email}')
                    
        except Exception as e:
            logger.error(f"Error deleting user {user_email}: {str(e)}")
            messages.error(request, f'Error deleting user {user_email}: {str(e)}')
            raise