from django.urls import path
from . import views

urlpatterns = [
    path('active/', views.get_active_studies, name='get_active_studies'),
    path('my-sessions/', views.get_my_sessions, name='get_my_sessions'),
    path('join/<str:study_id>/', views.join_study, name='join_study'),
    path('session/create/', views.create_session, name='create_session'),
    path('session/current/', views.get_current_session, name='get_current_session'),
    path('session/<uuid:session_id>/', views.get_session, name='get_session'),
    path('session/<uuid:session_id>/phase/', views.update_phase, name='update_phase'),
    path('session/<uuid:session_id>/end/', views.end_session, name='end_session'),
    path('session/<uuid:session_id>/complete/', views.complete_session, name='complete_session'),
    path('session/<uuid:session_id>/time/', views.update_session_time, name='update_session_time'),
    path('session/<uuid:session_id>/logs/', views.get_session_logs, name='get_session_logs'),
    path('log-event/', views.log_event, name='log_event'),
]