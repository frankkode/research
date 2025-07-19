from django.urls import path
from . import views

urlpatterns = [
    path('type/<str:quiz_type>/', views.get_quiz_by_type, name='get_quiz_by_type'),
    path('<uuid:quiz_id>/', views.get_quiz, name='get_quiz'),
    path('<uuid:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('attempt/<uuid:attempt_id>/answer/', views.submit_answer, name='submit_answer'),
    path('attempt/<uuid:attempt_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('submit-results/', views.submit_quiz_results, name='submit_quiz_results'),
    path('my-attempts/', views.my_attempts, name='my_attempts'),
]