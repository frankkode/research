from django.contrib import admin
from .models import Quiz, Question, QuestionChoice, QuizAttempt, QuizResponse, QuizAnalytics


class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz_type', 'time_limit_minutes', 'is_active', 'created_at')
    list_filter = ('quiz_type', 'is_active', 'created_at')
    search_fields = ('title', 'description')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text_preview', 'question_type', 'order', 'is_required')
    list_filter = ('question_type', 'is_required')
    search_fields = ('question_text', 'quiz__title')
    inlines = [QuestionChoiceInline]
    
    def question_text_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_preview.short_description = 'Question Text'


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'is_completed', 'score', 'started_at')
    list_filter = ('is_completed', 'started_at')
    search_fields = ('user__username', 'quiz__title')


@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at')
    search_fields = ('attempt__user__username', 'question__question_text')


@admin.register(QuizAnalytics)
class QuizAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'total_attempts', 'completed_attempts', 'average_score', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('quiz__title',)
    readonly_fields = ('last_updated',)