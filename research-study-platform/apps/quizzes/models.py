from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel, User
from apps.studies.models import StudySession


class Quiz(BaseModel):
    QUIZ_TYPES = [
        ('pre', 'Pre-Quiz'),
        ('post', 'Post-Quiz'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quiz_type = models.CharField(max_length=10, choices=QUIZ_TYPES)
    time_limit_minutes = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    # Study configuration
    study_group = models.CharField(max_length=10, blank=True)  # Can be assigned to specific groups
    display_order = models.IntegerField(default=0)
    
    # Quiz settings
    randomize_questions = models.BooleanField(default=False)
    show_results_immediately = models.BooleanField(default=False)
    allow_retakes = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['quiz_type', 'display_order']
    
    def __str__(self):
        return f"{self.title} ({self.get_quiz_type_display()})"


class Question(BaseModel):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('text', 'Text Input'),
        ('scale', 'Scale (1-5)'),
        ('likert', 'Likert Scale'),
        ('ranking', 'Ranking'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=True)
    
    # Question settings
    points = models.IntegerField(default=1)
    explanation = models.TextField(blank=True)  # Explanation for correct answer
    
    class Meta:
        ordering = ['order']
        unique_together = ['quiz', 'order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}: {self.question_text[:50]}..."


class QuestionChoice(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['question', 'order']
    
    def __str__(self):
        return f"{self.question} - {self.choice_text[:30]}..."


class QuizAttempt(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='quiz_attempts')
    
    # Timing information
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.IntegerField(null=True, blank=True)
    
    # Status tracking
    is_completed = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)
    is_timed_out = models.BooleanField(default=False)
    
    # Scoring
    score = models.FloatField(null=True, blank=True)
    max_score = models.FloatField(null=True, blank=True)
    percentage_score = models.FloatField(null=True, blank=True)
    
    # Question randomization
    question_order = models.JSONField(default=list)  # Store randomized question order
    
    # Additional metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        unique_together = ['quiz', 'user', 'session']
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.participant_id} - {self.quiz.title} - {self.started_at}"
    
    def calculate_score(self):
        """Calculate the score for this attempt"""
        responses = self.responses.all()
        total_points = 0
        earned_points = 0
        
        for response in responses:
            total_points += response.question.points
            if response.is_correct:
                earned_points += response.question.points
        
        if total_points > 0:
            self.score = earned_points
            self.max_score = total_points
            self.percentage_score = (earned_points / total_points) * 100
        else:
            self.score = 0
            self.max_score = 0
            self.percentage_score = 0
        
        self.save()
        return self.percentage_score
    
    def get_time_remaining(self):
        """Get remaining time in seconds"""
        if self.is_completed or not self.quiz.time_limit_minutes:
            return 0
        
        elapsed = timezone.now() - self.started_at
        elapsed_seconds = elapsed.total_seconds()
        total_seconds = self.quiz.time_limit_minutes * 60
        
        return max(0, total_seconds - elapsed_seconds)
    
    def is_time_expired(self):
        """Check if time limit has been exceeded"""
        if not self.quiz.time_limit_minutes:
            return False
        
        return self.get_time_remaining() <= 0


class QuizResponse(BaseModel):
    """Model for storing individual question responses"""
    
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    
    # Response data
    selected_choice = models.ForeignKey(QuestionChoice, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    numeric_answer = models.FloatField(null=True, blank=True)
    
    # Response metadata
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    answered_at = models.DateTimeField(default=timezone.now)
    time_to_answer_seconds = models.IntegerField(null=True, blank=True)
    
    # Interaction tracking
    question_viewed_at = models.DateTimeField(null=True, blank=True)
    times_changed = models.IntegerField(default=0)  # How many times answer was changed
    
    class Meta:
        unique_together = ['attempt', 'question']
        ordering = ['answered_at']
    
    def __str__(self):
        return f"{self.attempt.user.participant_id} - Q{self.question.order}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate correctness for multiple choice questions
        if self.question.question_type == 'multiple_choice' and self.selected_choice:
            self.is_correct = self.selected_choice.is_correct
            self.points_earned = self.question.points if self.is_correct else 0
        elif self.question.question_type == 'true_false' and self.selected_choice:
            self.is_correct = self.selected_choice.is_correct
            self.points_earned = self.question.points if self.is_correct else 0
        
        # Calculate time to answer
        if self.question_viewed_at and self.answered_at:
            delta = self.answered_at - self.question_viewed_at
            self.time_to_answer_seconds = int(delta.total_seconds())
        
        super().save(*args, **kwargs)


class QuizAnalytics(BaseModel):
    """Model for storing quiz analytics and statistics"""
    
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, related_name='analytics')
    
    # Participation statistics
    total_attempts = models.IntegerField(default=0)
    completed_attempts = models.IntegerField(default=0)
    abandoned_attempts = models.IntegerField(default=0)
    
    # Score statistics
    average_score = models.FloatField(default=0.0)
    highest_score = models.FloatField(default=0.0)
    lowest_score = models.FloatField(default=0.0)
    median_score = models.FloatField(default=0.0)
    
    # Time statistics
    average_completion_time_seconds = models.FloatField(default=0.0)
    fastest_completion_time_seconds = models.IntegerField(default=0)
    slowest_completion_time_seconds = models.IntegerField(default=0)
    
    # Question-level statistics
    question_statistics = models.JSONField(default=dict)  # Per-question analytics
    
    # Group comparisons
    group_performance = models.JSONField(default=dict)  # Performance by study group
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.quiz.title}"
    
    def update_statistics(self):
        """Update all statistics from quiz attempts"""
        attempts = self.quiz.attempts.filter(is_completed=True)
        
        self.total_attempts = self.quiz.attempts.count()
        self.completed_attempts = attempts.count()
        self.abandoned_attempts = self.total_attempts - self.completed_attempts
        
        if attempts.exists():
            scores = [a.percentage_score for a in attempts if a.percentage_score is not None]
            if scores:
                self.average_score = sum(scores) / len(scores)
                self.highest_score = max(scores)
                self.lowest_score = min(scores)
                self.median_score = sorted(scores)[len(scores) // 2]
            
            # Time statistics
            times = [a.time_taken_seconds for a in attempts if a.time_taken_seconds is not None]
            if times:
                self.average_completion_time_seconds = sum(times) / len(times)
                self.fastest_completion_time_seconds = min(times)
                self.slowest_completion_time_seconds = max(times)
        
        self.save()