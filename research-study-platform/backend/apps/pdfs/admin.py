from django.contrib import admin
from .models import PDFDocument, PDFInteraction, PDFSession


@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'study_group', 'page_count', 'file_size_bytes', 'is_active', 'display_order')
    list_filter = ('study_group', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('display_order', 'is_active')
    ordering = ('display_order', 'title')
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'description', 'file_path', 'file_size_bytes', 'page_count')
        }),
        ('Study Configuration', {
            'fields': ('study_group', 'display_order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PDFInteraction)
class PDFInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'document', 'interaction_type', 'page_number', 'timestamp', 'time_on_page_seconds')
    list_filter = ('interaction_type', 'timestamp', 'document')
    search_fields = ('user__username', 'user__participant_id', 'document__title', 'search_query')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('session', 'user', 'document', 'interaction_type', 'timestamp')
        }),
        ('Page Information', {
            'fields': ('page_number', 'total_pages', 'time_on_page_seconds', 'cumulative_time_seconds')
        }),
        ('Viewport Information', {
            'fields': ('viewport_width', 'viewport_height', 'scroll_x', 'scroll_y', 'zoom_level'),
            'classes': ('collapse',)
        }),
        ('Interaction Data', {
            'fields': ('search_query', 'highlighted_text', 'annotation_text', 'copied_text'),
            'classes': ('collapse',)
        }),
        ('Reading Analysis', {
            'fields': ('reading_speed_wpm', 'dwell_time_ms'),
            'classes': ('collapse',)
        }),
        ('Technical Info', {
            'fields': ('user_agent', 'screen_resolution'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'document', 'session')


@admin.register(PDFSession)
class PDFSessionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'document', 'pdf_started_at', 'pdf_ended_at', 
        'total_session_duration_seconds', 'reading_completion_percentage', 
        'total_interactions'
    )
    list_filter = ('pdf_started_at', 'document', 'user__study_group')
    search_fields = ('user__username', 'user__participant_id', 'document__title')
    date_hierarchy = 'pdf_started_at'
    ordering = ('-pdf_started_at',)
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session', 'user', 'document')
        }),
        ('Timing', {
            'fields': (
                'pdf_started_at', 'pdf_ended_at', 'total_session_duration_seconds',
                'active_reading_time_seconds', 'idle_time_seconds'
            )
        }),
        ('Reading Progress', {
            'fields': (
                'pages_visited', 'unique_pages_visited', 'total_page_views',
                'reading_completion_percentage'
            )
        }),
        ('Interactions', {
            'fields': (
                'total_interactions', 'scroll_interactions', 'zoom_interactions',
                'search_interactions'
            )
        }),
        ('Reading Behavior', {
            'fields': (
                'average_time_per_page_seconds', 'longest_page_time_seconds',
                'shortest_page_time_seconds'
            ),
            'classes': ('collapse',)
        }),
        ('Content Engagement', {
            'fields': (
                'text_selections', 'annotations_made', 'searches_performed'
            ),
            'classes': ('collapse',)
        }),
        ('Navigation Patterns', {
            'fields': (
                'forward_navigation_count', 'backward_navigation_count',
                'jump_navigation_count'
            ),
            'classes': ('collapse',)
        }),
        ('Focus and Attention', {
            'fields': ('focus_changes', 'times_returned_to_pdf'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('pdf_started_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'document', 'session')
    
    actions = ['recalculate_statistics']
    
    def recalculate_statistics(self, request, queryset):
        """Recalculate statistics for selected PDF sessions"""
        for session in queryset:
            session.calculate_statistics()
        self.message_user(request, f'Statistics recalculated for {queryset.count()} sessions.')
    recalculate_statistics.short_description = 'Recalculate statistics'