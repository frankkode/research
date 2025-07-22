from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, logging_views, export_views, privacy_views, utility_views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'studies', views.ResearchStudyViewSet)
router.register(r'participants', views.ParticipantProfileViewSet)
router.register(r'exports', views.DataExportViewSet)
router.register(r'interactions', views.InteractionLogViewSet)
router.register(r'dashboard', views.ResearchDashboardView, basename='dashboard')

urlpatterns = [
    # Function-based endpoints (must come before router to avoid conflicts)
    path('participants/all/', views.get_all_participants, name='get_all_participants'),
    path('participants/<str:participant_id>/delete/', views.delete_participant, name='delete_participant'),
    path('export/all/', views.export_all_data, name='export_all_data'),
    path('export/chat/', views.export_chat_interactions, name='export_chat_interactions'),
    path('export/pdf/', views.export_pdf_interactions, name='export_pdf_interactions'),
    path('export/quiz/', views.export_quiz_responses, name='export_quiz_responses'),
    path('statistics/', views.get_study_statistics, name='get_study_statistics'),
    
    # New API endpoints
    path('', include(router.urls)),
    
    # Logging endpoints
    path('logging/interaction/', logging_views.log_interaction, name='log_interaction'),
    path('logging/chat/', logging_views.log_chat_interaction, name='log_chat_interaction'),
    path('logging/pdf/', logging_views.log_pdf_viewing, name='log_pdf_viewing'),
    path('logging/quiz/', logging_views.log_quiz_response, name='log_quiz_response'),
    path('logging/session/', logging_views.log_session_event, name='log_session_event'),
    path('logging/navigation/', logging_views.log_navigation_event, name='log_navigation_event'),
    path('logging/error/', logging_views.log_error_event, name='log_error_event'),
    path('logging/bulk/', logging_views.bulk_log_interactions, name='bulk_log_interactions'),
    path('logging/summary/', logging_views.get_session_summary, name='get_session_summary'),
    path('logging/participant/', logging_views.get_participant_logs, name='get_participant_logs'),
    
    # Enhanced export endpoints
    path('export/v2/participants/', export_views.export_participants_enhanced, name='export_participants_enhanced'),
    path('export/v2/interactions/', export_views.export_interactions_enhanced, name='export_interactions_enhanced'),
    path('export/v2/chat/', export_views.export_chat_interactions_enhanced, name='export_chat_interactions_enhanced'),
    path('export/v2/pdf/', export_views.export_pdf_behaviors_enhanced, name='export_pdf_behaviors_enhanced'),
    path('export/v2/quiz/', export_views.export_quiz_responses_enhanced, name='export_quiz_responses_enhanced'),
    path('export/v2/full/', export_views.export_full_dataset, name='export_full_dataset'),
    path('export/v2/history/', export_views.get_export_history, name='get_export_history'),
    path('export/v2/stats/', export_views.get_export_stats, name='get_export_stats'),
    
    # Privacy and GDPR compliance endpoints
    path('privacy/anonymize/', privacy_views.anonymize_participant, name='anonymize_participant'),
    path('privacy/delete/', privacy_views.delete_participant_data, name='delete_participant_data'),
    path('privacy/export/', privacy_views.export_participant_data, name='export_participant_data'),
    path('privacy/retention/', privacy_views.process_data_retention, name='process_data_retention'),
    path('privacy/report/', privacy_views.generate_privacy_report, name='generate_privacy_report'),
    path('privacy/compliance/', privacy_views.get_gdpr_compliance_status, name='get_gdpr_compliance_status'),
    path('privacy/participant/', privacy_views.get_participant_privacy_status, name='get_participant_privacy_status'),
    path('privacy/bulk-anonymize/', privacy_views.bulk_anonymize_participants, name='bulk_anonymize_participants'),
    path('privacy/retention-candidates/', privacy_views.get_data_retention_candidates, name='get_data_retention_candidates'),
    
    # Research utilities endpoints
    path('utilities/generate-ids/', utility_views.generate_participant_ids, name='generate_participant_ids'),
    path('utilities/assign-groups/', utility_views.assign_groups, name='assign_groups'),
    path('utilities/bulk-generate/', utility_views.bulk_generate_participants, name='bulk_generate_participants'),
    path('utilities/validate-integrity/', utility_views.validate_data_integrity, name='validate_data_integrity'),
    path('utilities/sample-size/', utility_views.calculate_sample_size, name='calculate_sample_size'),
    path('utilities/study-duration/', utility_views.estimate_study_duration, name='estimate_study_duration'),
    path('utilities/study-summary/', utility_views.generate_study_summary, name='generate_study_summary'),
    path('utilities/randomization-seed/', utility_views.generate_randomization_seed, name='generate_randomization_seed'),
    path('utilities/study-stats/', utility_views.get_study_statistics, name='get_study_statistics'),
    path('utilities/available-groups/', utility_views.get_available_groups, name='get_available_groups'),
    
    # Legacy endpoints (moved to top of file to avoid router conflicts)
]