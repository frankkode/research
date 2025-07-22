from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    STUDY_GROUP_CHOICES = [
        ('PDF', 'PDF Group'),
        ('CHATGPT', 'ChatGPT Group'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    participant_id = models.CharField(max_length=50, unique=True)
    study_group = models.CharField(max_length=10, choices=STUDY_GROUP_CHOICES)
    
    # Completion tracking booleans
    consent_completed = models.BooleanField(default=False)
    pre_quiz_completed = models.BooleanField(default=False)
    interaction_completed = models.BooleanField(default=False)
    post_quiz_completed = models.BooleanField(default=False)
    study_completed = models.BooleanField(default=False)
    
    # Timestamps
    consent_completed_at = models.DateTimeField(null=True, blank=True)
    pre_quiz_completed_at = models.DateTimeField(null=True, blank=True)
    interaction_completed_at = models.DateTimeField(null=True, blank=True)
    post_quiz_completed_at = models.DateTimeField(null=True, blank=True)
    study_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Transfer quiz notification tracking
    transfer_quiz_notification_sent = models.BooleanField(default=False)
    transfer_quiz_notification_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'participant_id', 'study_group']
    
    def __str__(self):
        return f"{self.participant_id} - {self.study_group}"
    
    @property
    def completion_percentage(self):
        completed_stages = sum([
            self.consent_completed,
            self.pre_quiz_completed,
            self.interaction_completed,
            self.post_quiz_completed
        ])
        return (completed_stages / 4) * 100


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True