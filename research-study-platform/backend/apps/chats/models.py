from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel, User
from apps.studies.models import StudySession


class ChatInteraction(BaseModel):
    """Model for logging chat interactions during study sessions"""
    
    MESSAGE_TYPES = [
        ('user_message', 'User Message'),
        ('assistant_response', 'Assistant Response'),
        ('system_message', 'System Message'),
        ('error', 'Error'),
    ]
    
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='chat_interactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_interactions')
    
    # Message details
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    user_message = models.TextField(blank=True)
    assistant_response = models.TextField(blank=True)
    
    # Timing information
    message_timestamp = models.DateTimeField(default=timezone.now)
    response_time_ms = models.IntegerField(null=True, blank=True)
    
    # OpenAI API information
    openai_model = models.CharField(max_length=50, default='gpt-3.5-turbo')
    prompt_tokens = models.IntegerField(null=True, blank=True)
    completion_tokens = models.IntegerField(null=True, blank=True)
    total_tokens = models.IntegerField(null=True, blank=True)
    
    # Conversation context
    conversation_turn = models.IntegerField(default=1)  # Turn number in conversation
    conversation_history = models.JSONField(default=list)  # Full conversation history
    
    # Additional metadata
    user_input_length = models.IntegerField(default=0)
    response_length = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    # Research-specific fields
    interaction_quality_score = models.FloatField(null=True, blank=True)  # For analysis
    contains_question = models.BooleanField(default=False)
    contains_code = models.BooleanField(default=False)
    contains_linux_command = models.BooleanField(default=False)
    topic_category = models.CharField(max_length=100, blank=True)
    
    # Rate limiting and error tracking
    api_request_id = models.CharField(max_length=100, blank=True)
    rate_limit_hit = models.BooleanField(default=False)
    retry_count = models.IntegerField(default=0)
    
    # Cost tracking
    estimated_cost_usd = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    
    class Meta:
        ordering = ['message_timestamp']
        indexes = [
            models.Index(fields=['session', 'message_timestamp']),
            models.Index(fields=['user', 'message_timestamp']),
            models.Index(fields=['message_type']),
        ]
    
    def __str__(self):
        return f"{self.user.participant_id} - Turn {self.conversation_turn} - {self.message_type}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate lengths
        self.user_input_length = len(self.user_message) if self.user_message else 0
        self.response_length = len(self.assistant_response) if self.assistant_response else 0
        
        # Auto-detect patterns
        if self.user_message:
            self.contains_question = '?' in self.user_message
            self.contains_code = any(keyword in self.user_message.lower() 
                                   for keyword in ['code', 'function', 'def ', 'class ', 'import'])
            
            # Detect Linux commands
            linux_commands = ['ls', 'cd', 'pwd', 'cat', 'cp', 'mv', 'chmod', 'chown', 'grep', 'find']
            self.contains_linux_command = any(cmd in self.user_message.lower() 
                                            for cmd in linux_commands)
        
        super().save(*args, **kwargs)


class ChatSession(BaseModel):
    """Model for tracking overall chat session statistics"""
    
    session = models.OneToOneField(StudySession, on_delete=models.CASCADE, related_name='chat_session')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    
    # Session timing
    chat_started_at = models.DateTimeField(default=timezone.now)
    chat_ended_at = models.DateTimeField(null=True, blank=True)
    total_chat_duration_seconds = models.IntegerField(default=0)
    
    # Interaction statistics
    total_messages = models.IntegerField(default=0)
    total_user_messages = models.IntegerField(default=0)
    total_assistant_responses = models.IntegerField(default=0)
    
    # Token usage
    total_tokens_used = models.IntegerField(default=0)
    total_prompt_tokens = models.IntegerField(default=0)
    total_completion_tokens = models.IntegerField(default=0)
    
    # Performance metrics
    average_response_time_ms = models.FloatField(default=0.0)
    longest_response_time_ms = models.IntegerField(default=0)
    shortest_response_time_ms = models.IntegerField(default=0)
    
    # Content analysis
    total_user_characters = models.IntegerField(default=0)
    total_assistant_characters = models.IntegerField(default=0)
    average_message_length = models.FloatField(default=0.0)
    
    # Engagement metrics
    questions_asked = models.IntegerField(default=0)
    code_discussions = models.IntegerField(default=0)
    linux_command_queries = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    # Cost tracking
    total_estimated_cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    
    # Rate limiting tracking
    rate_limit_hits = models.IntegerField(default=0)
    total_retries = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-chat_started_at']
    
    def __str__(self):
        return f"{self.user.participant_id} - Chat Session"
    
    def calculate_statistics(self):
        """Calculate and update session statistics from interactions"""
        interactions = self.session.chat_interactions.all()
        
        self.total_messages = interactions.count()
        self.total_user_messages = interactions.filter(message_type='user_message').count()
        self.total_assistant_responses = interactions.filter(message_type='assistant_response').count()
        
        # Token calculations
        self.total_tokens_used = sum(i.total_tokens or 0 for i in interactions)
        self.total_prompt_tokens = sum(i.prompt_tokens or 0 for i in interactions)
        self.total_completion_tokens = sum(i.completion_tokens or 0 for i in interactions)
        
        # Response time calculations
        response_times = [i.response_time_ms for i in interactions if i.response_time_ms]
        if response_times:
            self.average_response_time_ms = sum(response_times) / len(response_times)
            self.longest_response_time_ms = max(response_times)
            self.shortest_response_time_ms = min(response_times)
        
        # Content analysis
        self.total_user_characters = sum(i.user_input_length for i in interactions)
        self.total_assistant_characters = sum(i.response_length for i in interactions)
        
        if self.total_messages > 0:
            self.average_message_length = (self.total_user_characters + self.total_assistant_characters) / self.total_messages
        
        # Engagement metrics
        self.questions_asked = interactions.filter(contains_question=True).count()
        self.code_discussions = interactions.filter(contains_code=True).count()
        self.linux_command_queries = interactions.filter(contains_linux_command=True).count()
        self.error_count = interactions.filter(message_type='error').count()
        
        # Cost tracking
        costs = [i.estimated_cost_usd for i in interactions if i.estimated_cost_usd]
        self.total_estimated_cost_usd = sum(costs) if costs else 0.0
        
        # Rate limiting tracking
        self.rate_limit_hits = interactions.filter(rate_limit_hit=True).count()
        self.total_retries = sum(i.retry_count for i in interactions)
        
        self.save()