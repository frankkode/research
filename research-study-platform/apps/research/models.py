from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
import uuid
import secrets
import string

User = get_user_model()


class ResearchStudy(BaseModel):
    """Main research study configuration"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=100)
    estimated_duration_minutes = models.IntegerField(default=60)
    
    # Study configuration
    requires_consent = models.BooleanField(default=True)
    has_pre_quiz = models.BooleanField(default=True)
    has_post_quiz = models.BooleanField(default=True)
    
    # Randomization settings
    auto_assign_groups = models.BooleanField(default=True)
    group_balance_ratio = models.JSONField(default=dict)  # e.g., {"PDF": 0.5, "CHATGPT": 0.5}
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_studies')
    
    class Meta:
        verbose_name_plural = "Research Studies"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def participant_count(self):
        return self.participants.count()
    
    @property
    def completion_rate(self):
        total = self.participant_count
        if total == 0:
            return 0
        # FIXED: Using user__study_completed instead of study_completed
        completed = self.participants.filter(user__study_completed=True).count()
        return (completed / total) * 100


class ParticipantProfile(BaseModel):
    """Extended participant information for research purposes"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='research_profile')
    study = models.ForeignKey(ResearchStudy, on_delete=models.CASCADE, related_name='participants')
    
    # Demographics (optional, anonymized)
    age_range = models.CharField(max_length=20, blank=True)
    education_level = models.CharField(max_length=50, blank=True)
    technical_background = models.CharField(max_length=100, blank=True)
    
    # Research metadata
    assigned_group = models.CharField(max_length=20)  # PDF, CHATGPT, etc.
    assignment_timestamp = models.DateTimeField(auto_now_add=True)
    randomization_seed = models.CharField(max_length=32)
    
    # Consent and compliance
    consent_given = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(null=True, blank=True)
    gdpr_consent = models.BooleanField(default=False)
    data_processing_consent = models.BooleanField(default=False)
    
    # Withdrawal tracking
    withdrawn = models.BooleanField(default=False)
    withdrawal_timestamp = models.DateTimeField(null=True, blank=True)
    withdrawal_reason = models.TextField(blank=True)
    
    # Data anonymization
    anonymized_id = models.CharField(max_length=50, unique=True)
    is_anonymized = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'study']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.participant_id} - {self.study.name}"
    
    def save(self, *args, **kwargs):
        if not self.anonymized_id:
            self.anonymized_id = self.generate_anonymized_id()
        if not self.randomization_seed:
            self.randomization_seed = secrets.token_hex(16)
        super().save(*args, **kwargs)
    
    def generate_anonymized_id(self):
        """Generate a unique anonymized ID for the participant"""
        prefix = "P"
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        return f"{prefix}{random_part}"


class InteractionLog(BaseModel):
    """Detailed logging of all participant interactions"""
    LOG_TYPES = [
        ('session_start', 'Session Start'),
        ('session_end', 'Session End'),
        ('phase_transition', 'Phase Transition'),
        ('chat_message_sent', 'Chat Message Sent'),
        ('chat_message_received', 'Chat Message Received'),
        ('pdf_opened', 'PDF Opened'),
        ('pdf_page_viewed', 'PDF Page Viewed'),
        ('pdf_scroll', 'PDF Scroll'),
        ('pdf_zoom', 'PDF Zoom'),
        ('pdf_search', 'PDF Search'),
        ('quiz_question_viewed', 'Quiz Question Viewed'),
        ('quiz_answer_submitted', 'Quiz Answer Submitted'),
        ('quiz_answer_changed', 'Quiz Answer Changed'),
        ('button_click', 'Button Click'),
        ('form_submit', 'Form Submit'),
        ('navigation', 'Navigation'),
        ('focus_change', 'Focus Change'),
        ('error_occurred', 'Error Occurred'),
    ]
    
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE, related_name='interaction_logs')
    session_id = models.CharField(max_length=100)
    log_type = models.CharField(max_length=30, choices=LOG_TYPES)
    
    # Event details
    event_data = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Context information
    page_url = models.URLField(blank=True)
    user_agent = models.TextField(blank=True)
    screen_resolution = models.CharField(max_length=20, blank=True)
    
    # Timing data
    reaction_time_ms = models.IntegerField(null=True, blank=True)
    time_since_last_action_ms = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['participant', 'log_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.participant.anonymized_id} - {self.log_type} - {self.timestamp}"


class ChatInteraction(BaseModel):
    """Specific logging for ChatGPT interactions"""
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE, related_name='chat_interactions')
    session_id = models.CharField(max_length=100)
    
    # Message details
    message_type = models.CharField(max_length=20, choices=[
        ('user_message', 'User Message'),
        ('assistant_response', 'Assistant Response'),
        ('system_message', 'System Message'),
    ])
    
    content = models.TextField()
    content_hash = models.CharField(max_length=64)  # For deduplication
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    
    # Metadata
    token_count = models.IntegerField(null=True, blank=True)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['participant', 'timestamp']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.participant.anonymized_id} - {self.message_type} - {self.timestamp}"


class PDFViewingBehavior(BaseModel):
    """Tracking PDF viewing patterns and behavior"""
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE, related_name='pdf_behaviors')
    session_id = models.CharField(max_length=100)
    
    # PDF details
    pdf_name = models.CharField(max_length=200)
    pdf_hash = models.CharField(max_length=64)
    
    # Viewing behavior
    page_number = models.IntegerField()
    time_spent_seconds = models.IntegerField(default=0)
    
    # Interaction details
    scroll_events = models.JSONField(default=list)
    zoom_events = models.JSONField(default=list)
    search_queries = models.JSONField(default=list)
    
    # Timing
    first_viewed_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['participant', 'session_id', 'pdf_name', 'page_number']
        ordering = ['-last_viewed_at']
    
    def __str__(self):
        return f"{self.participant.anonymized_id} - {self.pdf_name} - Page {self.page_number}"


class QuizResponse(BaseModel):
    """Enhanced quiz response tracking"""
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE, related_name='quiz_responses')
    session_id = models.CharField(max_length=100)
    
    # Quiz details
    quiz_type = models.CharField(max_length=20, choices=[
        ('pre_quiz', 'Pre-Quiz'),
        ('post_quiz', 'Post-Quiz'),
    ])
    
    question_id = models.CharField(max_length=100)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20)  # multiple_choice, text, rating, etc.
    
    # Response details
    response_value = models.JSONField()  # Can store various response types
    response_text = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    
    # Timing and behavior
    first_viewed_at = models.DateTimeField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    time_spent_seconds = models.IntegerField(default=0)
    changes_made = models.IntegerField(default=0)  # Number of times answer was changed
    
    class Meta:
        unique_together = ['participant', 'session_id', 'quiz_type', 'question_id']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.participant.anonymized_id} - {self.quiz_type} - Q{self.question_id}"


class DataExport(BaseModel):
    """Track data export requests and provide audit trail"""
    EXPORT_TYPES = [
        ('full_dataset', 'Full Dataset'),
        ('participant_data', 'Participant Data'),
        ('interaction_logs', 'Interaction Logs'),
        ('quiz_responses', 'Quiz Responses'),
        ('chat_interactions', 'Chat Interactions'),
        ('pdf_behaviors', 'PDF Viewing Behaviors'),
    ]
    
    EXPORT_FORMATS = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('excel', 'Excel'),
    ]
    
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_requests')
    study = models.ForeignKey(ResearchStudy, on_delete=models.CASCADE, related_name='exports')
    
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPES)
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMATS)
    
    # Filters and parameters
    filters = models.JSONField(default=dict)
    date_range_start = models.DateTimeField(null=True, blank=True)
    date_range_end = models.DateTimeField(null=True, blank=True)
    
    # Export status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    
    # File details
    file_path = models.CharField(max_length=500, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    record_count = models.IntegerField(null=True, blank=True)
    
    # Audit trail
    exported_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    download_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.study.name} - {self.export_type} - {self.requested_by.username}"


class ResearcherAccess(BaseModel):
    """Track researcher access and permissions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='researcher_access')
    study = models.ForeignKey(ResearchStudy, on_delete=models.CASCADE, related_name='researcher_access')
    
    PERMISSION_LEVELS = [
        ('view', 'View Only'),
        ('export', 'View and Export'),
        ('manage', 'Full Management'),
    ]
    
    permission_level = models.CharField(max_length=20, choices=PERMISSION_LEVELS)
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_access')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    # Access tracking
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'study']
        ordering = ['-granted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.study.name} - {self.permission_level}"