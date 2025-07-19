from django.urls import path
from . import views

urlpatterns = [
    path('documents/', views.get_documents, name='get_documents'),
    path('log-interaction/', views.log_pdf_interaction, name='log_pdf_interaction'),
    path('session/<uuid:session_id>/', views.get_pdf_session, name='get_pdf_session'),
    path('session/<uuid:session_id>/start/', views.start_pdf_session, name='start_pdf_session'),
    path('session/<uuid:session_id>/end/', views.end_pdf_session, name='end_pdf_session'),
]