from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel, User
from apps.studies.models import StudySession


class PDFDocument(BaseModel):
    """Model for storing PDF documents used in the study"""
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=500)  # Path to PDF file
    file_size_bytes = models.BigIntegerField(default=0)
    page_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Study configuration
    study_group = models.CharField(max_length=10, default='PDF')
    display_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'title']
    
    def __str__(self):
        return self.title


class PDFInteraction(BaseModel):
    """Model for tracking PDF engagement and interactions"""
    
    INTERACTION_TYPES = [
        ('page_view', 'Page View'),
        ('scroll', 'Scroll'),
        ('zoom', 'Zoom'),
        ('search', 'Search'),
        ('highlight', 'Highlight'),
        ('annotation', 'Annotation'),
        ('download', 'Download'),
        ('print', 'Print'),
        ('navigate', 'Navigate'),
        ('resize', 'Resize'),
        ('fullscreen', 'Fullscreen'),
        ('copy_text', 'Copy Text'),
        ('bookmark', 'Bookmark'),
        ('session_start', 'Session Start'),
        ('session_end', 'Session End'),
        ('idle_detected', 'Idle Detected'),
        ('focus_lost', 'Focus Lost'),
        ('focus_gained', 'Focus Gained'),
    ]
    
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='pdf_interactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_interactions')
    document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='interactions')
    
    # Interaction details
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Page tracking
    page_number = models.IntegerField(null=True, blank=True)
    total_pages = models.IntegerField(null=True, blank=True)
    
    # Viewport and scroll information
    viewport_width = models.IntegerField(null=True, blank=True)
    viewport_height = models.IntegerField(null=True, blank=True)
    scroll_x = models.IntegerField(null=True, blank=True)
    scroll_y = models.IntegerField(null=True, blank=True)
    zoom_level = models.FloatField(null=True, blank=True)
    
    # Time tracking
    time_on_page_seconds = models.FloatField(null=True, blank=True)
    cumulative_time_seconds = models.FloatField(default=0.0)
    
    # Interaction-specific data
    search_query = models.CharField(max_length=200, blank=True)
    highlighted_text = models.TextField(blank=True)
    annotation_text = models.TextField(blank=True)
    copied_text = models.TextField(blank=True)
    
    # Reading behavior analysis
    reading_speed_wpm = models.FloatField(null=True, blank=True)  # Words per minute
    dwell_time_ms = models.IntegerField(null=True, blank=True)  # Time spent on specific area
    
    # Additional metadata
    user_agent = models.TextField(blank=True)
    screen_resolution = models.CharField(max_length=20, blank=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['document', 'timestamp']),
            models.Index(fields=['interaction_type']),
            models.Index(fields=['page_number']),
        ]
    
    def __str__(self):
        return f"{self.user.participant_id} - {self.interaction_type} - Page {self.page_number}"


class PDFSession(BaseModel):
    """Model for tracking overall PDF session statistics"""
    
    session = models.OneToOneField(StudySession, on_delete=models.CASCADE, related_name='pdf_session')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_sessions')
    document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='sessions')
    
    # Session timing
    pdf_started_at = models.DateTimeField(default=timezone.now)
    pdf_ended_at = models.DateTimeField(null=True, blank=True)
    total_session_duration_seconds = models.IntegerField(default=0)
    active_reading_time_seconds = models.IntegerField(default=0)  # Excluding idle time
    idle_time_seconds = models.IntegerField(default=0)
    
    # Reading progress
    pages_visited = models.JSONField(default=list)  # List of page numbers visited
    unique_pages_visited = models.IntegerField(default=0)
    total_page_views = models.IntegerField(default=0)
    reading_completion_percentage = models.FloatField(default=0.0)
    
    # Interaction statistics
    total_interactions = models.IntegerField(default=0)
    scroll_interactions = models.IntegerField(default=0)
    zoom_interactions = models.IntegerField(default=0)
    search_interactions = models.IntegerField(default=0)
    
    # Reading behavior
    average_time_per_page_seconds = models.FloatField(default=0.0)
    longest_page_time_seconds = models.FloatField(default=0.0)
    shortest_page_time_seconds = models.FloatField(default=0.0)
    
    # Content engagement
    text_selections = models.IntegerField(default=0)
    annotations_made = models.IntegerField(default=0)
    searches_performed = models.IntegerField(default=0)
    
    # Navigation patterns
    forward_navigation_count = models.IntegerField(default=0)
    backward_navigation_count = models.IntegerField(default=0)
    jump_navigation_count = models.IntegerField(default=0)  # Non-sequential page jumps
    
    # Focus and attention
    focus_changes = models.IntegerField(default=0)
    times_returned_to_pdf = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-pdf_started_at']
    
    def __str__(self):
        return f"{self.user.participant_id} - PDF Session - {self.document.title}"
    
    def calculate_statistics(self):
        """Calculate and update session statistics from interactions"""
        interactions = self.session.pdf_interactions.filter(document=self.document)
        
        self.total_interactions = interactions.count()
        self.scroll_interactions = interactions.filter(interaction_type='scroll').count()
        self.zoom_interactions = interactions.filter(interaction_type='zoom').count()
        self.search_interactions = interactions.filter(interaction_type='search').count()
        
        # Calculate reading progress
        page_views = interactions.filter(interaction_type='page_view')
        if page_views.exists():
            pages_visited = list(page_views.values_list('page_number', flat=True))
            self.pages_visited = pages_visited
            self.unique_pages_visited = len(set(pages_visited))
            self.total_page_views = len(pages_visited)
            
            if self.document.page_count > 0:
                self.reading_completion_percentage = (self.unique_pages_visited / self.document.page_count) * 100
        
        # Calculate time statistics
        page_times = [i.time_on_page_seconds for i in interactions if i.time_on_page_seconds]
        if page_times:
            self.average_time_per_page_seconds = sum(page_times) / len(page_times)
            self.longest_page_time_seconds = max(page_times)
            self.shortest_page_time_seconds = min(page_times)
        
        # Content engagement
        self.text_selections = interactions.filter(interaction_type='copy_text').count()
        self.annotations_made = interactions.filter(interaction_type='annotation').count()
        self.searches_performed = interactions.filter(interaction_type='search').count()
        
        # Focus tracking
        self.focus_changes = interactions.filter(interaction_type__in=['focus_lost', 'focus_gained']).count()
        
        self.save()
    
    def get_reading_pattern(self):
        """Analyze reading pattern (sequential vs. jumping)"""
        page_views = self.session.pdf_interactions.filter(
            document=self.document,
            interaction_type='page_view'
        ).order_by('timestamp')
        
        if page_views.count() < 2:
            return 'insufficient_data'
        
        sequential_count = 0
        jump_count = 0
        
        previous_page = None
        for interaction in page_views:
            if previous_page is not None:
                page_diff = abs(interaction.page_number - previous_page)
                if page_diff == 1:
                    sequential_count += 1
                elif page_diff > 1:
                    jump_count += 1
            previous_page = interaction.page_number
        
        total_transitions = sequential_count + jump_count
        if total_transitions == 0:
            return 'single_page'
        
        sequential_percentage = (sequential_count / total_transitions) * 100
        
        if sequential_percentage > 70:
            return 'sequential'
        elif sequential_percentage < 30:
            return 'jumping'
        else:
            return 'mixed'