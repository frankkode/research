from django.urls import path
from . import views, cost_views

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('history/<uuid:session_id>/', views.get_chat_history, name='get_chat_history'),
    path('session/<uuid:session_id>/', views.get_chat_session, name='get_chat_session'),
    path('session/<uuid:session_id>/start/', views.start_chat_session, name='start_chat_session'),
    path('session/<uuid:session_id>/end/', views.end_chat_session, name='end_chat_session'),
    
    # Cost management endpoints
    path('costs/overview/', cost_views.get_cost_overview, name='get_cost_overview'),
    path('costs/users/', cost_views.get_user_costs, name='get_user_costs'),
    path('costs/export/', cost_views.export_cost_report, name='export_cost_report'),
    path('costs/my-limits/', cost_views.check_user_limits, name='check_user_limits'),
]