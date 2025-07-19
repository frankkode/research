from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'education_level', 'consent_given', 'created_at')
    list_filter = ('consent_given', 'gender', 'education_level', 'created_at')
    search_fields = ('user__username', 'user__email')