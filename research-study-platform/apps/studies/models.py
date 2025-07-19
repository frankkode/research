from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel, User


class StudySession(BaseModel):
    PHASE_CHOICES = [
        ('consent', 'Consent'),
        ('pre_quiz', 'Pre-Quiz'),
        ('interaction', 'Interaction'),
        ('post_quiz', 'Post-Quiz'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    current_phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='consent')
    
    # Timing and duration tracking
    session_started_at = models.DateTimeField(default=timezone.now)
    session_ended_at = models.DateTimeField(null=True, blank=True)
    
    # Phase timings
    consent_started_at = models.DateTimeField(null=True, blank=True)
    consent_ended_at = models.DateTimeField(null=True, blank=True)
    pre_quiz_started_at = models.DateTimeField(null=True, blank=True)
    pre_quiz_ended_at = models.DateTimeField(null=True, blank=True)
    interaction_started_at = models.DateTimeField(null=True, blank=True)
    interaction_ended_at = models.DateTimeField(null=True, blank=True)
    post_quiz_started_at = models.DateTimeField(null=True, blank=True)
    post_quiz_ended_at = models.DateTimeField(null=True, blank=True)
    
    # Duration tracking in seconds
    consent_duration = models.IntegerField(default=0)
    pre_quiz_duration = models.IntegerField(default=0)
    interaction_duration = models.IntegerField(default=0)
    post_quiz_duration = models.IntegerField(default=0)
    total_duration = models.IntegerField(default=0)
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    
    # Additional metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-session_started_at']
    
    def __str__(self):
        return f"{self.user.participant_id} - Session {self.session_id}"
    
    def calculate_total_duration(self):
        """Calculate total session duration"""
        if self.session_ended_at and self.session_started_at:
            delta = self.session_ended_at - self.session_started_at
            self.total_duration = int(delta.total_seconds())
            return self.total_duration
        return 0
    
    def get_phase_duration(self, phase):
        """Get duration for a specific phase"""
        duration_field = f"{phase}_duration"
        return getattr(self, duration_field, 0)
    
    def set_phase_duration(self, phase, duration):
        """Set duration for a specific phase"""
        duration_field = f"{phase}_duration"
        if hasattr(self, duration_field):
            setattr(self, duration_field, duration)
            self.save()


class StudyLog(BaseModel):
    LOG_TYPES = [
        ('session_start', 'Session Start'),
        ('session_end', 'Session End'),
        ('study_joined', 'Study Joined'),
        ('phase_start', 'Phase Start'),
        ('phase_end', 'Phase End'),
        ('page_view', 'Page View'),
        ('button_click', 'Button Click'),
        ('form_submit', 'Form Submit'),
        ('chat_message', 'Chat Message'),
        ('quiz_answer', 'Quiz Answer'),
        ('quiz_start', 'Quiz Start'),
        ('quiz_submit', 'Quiz Submit'),
        ('pdf_view', 'PDF View'),
        ('pdf_scroll', 'PDF Scroll'),
        ('pdf_interaction', 'PDF Interaction'),
        ('time_spent', 'Time Spent'),
        ('system_event', 'System Event'),
        ('error', 'Error'),
    ]
    
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='logs')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    event_data = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session', 'log_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.session.user.participant_id} - {self.log_type} - {self.timestamp}"