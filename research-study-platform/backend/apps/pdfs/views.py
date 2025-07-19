from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import json

from .models import PDFDocument, PDFInteraction, PDFSession
from apps.studies.models import StudySession
from apps.core.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_documents(request):
    """Get available PDF documents for the current user's study group"""
    try:
        # Get user's study group
        user_group = request.user.study_group
        
        # Filter documents by study group
        documents = PDFDocument.objects.filter(
            study_group=user_group,
            is_active=True
        ).order_by('display_order')
        
        # Serialize document data
        documents_data = []
        for doc in documents:
            documents_data.append({
                'id': doc.id,
                'title': doc.title,
                'description': doc.description,
                'file_path': doc.file_path,
                'file_size_bytes': doc.file_size_bytes,
                'page_count': doc.page_count,
                'display_order': doc.display_order,
                'created_at': doc.created_at,
            })
        
        return Response({
            'documents': documents_data,
            'count': len(documents_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve documents',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_pdf_interaction(request):
    """Log a PDF interaction event"""
    try:
        # Get required data from request
        session_id = request.data.get('session_id')
        document_id = request.data.get('document_id')
        interaction_type = request.data.get('interaction_type')
        
        # Validate required fields
        if not all([session_id, document_id, interaction_type]):
            return Response({
                'error': 'Missing required fields: session_id, document_id, interaction_type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get related objects
        session = get_object_or_404(StudySession, session_id=session_id, user=request.user)
        document = get_object_or_404(PDFDocument, id=document_id, is_active=True)
        
        # Create interaction record
        interaction = PDFInteraction.objects.create(
            session=session,
            user=request.user,
            document=document,
            interaction_type=interaction_type,
            page_number=request.data.get('page_number'),
            total_pages=request.data.get('total_pages'),
            viewport_width=request.data.get('viewport_width'),
            viewport_height=request.data.get('viewport_height'),
            scroll_x=request.data.get('scroll_x'),
            scroll_y=request.data.get('scroll_y'),
            zoom_level=request.data.get('zoom_level'),
            time_on_page_seconds=request.data.get('time_on_page_seconds'),
            cumulative_time_seconds=request.data.get('cumulative_time_seconds', 0.0),
            search_query=request.data.get('search_query', ''),
            highlighted_text=request.data.get('highlighted_text', ''),
            annotation_text=request.data.get('annotation_text', ''),
            copied_text=request.data.get('copied_text', ''),
            reading_speed_wpm=request.data.get('reading_speed_wpm'),
            dwell_time_ms=request.data.get('dwell_time_ms'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            screen_resolution=request.data.get('screen_resolution', ''),
        )
        
        # Update PDF session statistics if exists
        try:
            pdf_session = PDFSession.objects.get(session=session, document=document)
            pdf_session.calculate_statistics()
        except PDFSession.DoesNotExist:
            pass
        
        return Response({
            'success': True,
            'interaction_id': interaction.id,
            'timestamp': interaction.timestamp
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Failed to log interaction',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pdf_session(request, session_id):
    """Get PDF session information"""
    try:
        # Get study session
        session = get_object_or_404(StudySession, session_id=session_id, user=request.user)
        
        # Get PDF sessions for this study session
        pdf_sessions = PDFSession.objects.filter(session=session)
        
        sessions_data = []
        for pdf_session in pdf_sessions:
            sessions_data.append({
                'id': pdf_session.id,
                'document_id': pdf_session.document.id,
                'document_title': pdf_session.document.title,
                'pdf_started_at': pdf_session.pdf_started_at,
                'pdf_ended_at': pdf_session.pdf_ended_at,
                'total_session_duration_seconds': pdf_session.total_session_duration_seconds,
                'active_reading_time_seconds': pdf_session.active_reading_time_seconds,
                'idle_time_seconds': pdf_session.idle_time_seconds,
                'pages_visited': pdf_session.pages_visited,
                'unique_pages_visited': pdf_session.unique_pages_visited,
                'total_page_views': pdf_session.total_page_views,
                'reading_completion_percentage': pdf_session.reading_completion_percentage,
                'total_interactions': pdf_session.total_interactions,
                'average_time_per_page_seconds': pdf_session.average_time_per_page_seconds,
                'reading_pattern': pdf_session.get_reading_pattern(),
            })
        
        return Response({
            'session_id': session_id,
            'pdf_sessions': sessions_data,
            'count': len(sessions_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve PDF session',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_pdf_session(request, session_id):
    """Start a new PDF session"""
    try:
        # Get required data
        document_id = request.data.get('document_id')
        
        if not document_id:
            return Response({
                'error': 'document_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get related objects
        session = get_object_or_404(StudySession, session_id=session_id, user=request.user)
        document = get_object_or_404(PDFDocument, id=document_id, is_active=True)
        
        # Create or get PDF session
        pdf_session, created = PDFSession.objects.get_or_create(
            session=session,
            document=document,
            defaults={
                'user': request.user,
                'pdf_started_at': timezone.now(),
            }
        )
        
        # If session already exists, update start time
        if not created:
            pdf_session.pdf_started_at = timezone.now()
            pdf_session.save()
        
        # Log session start interaction
        PDFInteraction.objects.create(
            session=session,
            user=request.user,
            document=document,
            interaction_type='session_start',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            screen_resolution=request.data.get('screen_resolution', ''),
        )
        
        return Response({
            'success': True,
            'pdf_session_id': pdf_session.id,
            'started_at': pdf_session.pdf_started_at,
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to start PDF session',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_pdf_session(request, session_id):
    """End a PDF session"""
    try:
        # Get required data
        document_id = request.data.get('document_id')
        
        if not document_id:
            return Response({
                'error': 'document_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get related objects
        session = get_object_or_404(StudySession, session_id=session_id, user=request.user)
        document = get_object_or_404(PDFDocument, id=document_id, is_active=True)
        
        # Get PDF session
        pdf_session = get_object_or_404(
            PDFSession,
            session=session,
            document=document,
            user=request.user
        )
        
        # Update session end time
        pdf_session.pdf_ended_at = timezone.now()
        
        # Calculate total session duration
        if pdf_session.pdf_started_at:
            duration = pdf_session.pdf_ended_at - pdf_session.pdf_started_at
            pdf_session.total_session_duration_seconds = int(duration.total_seconds())
        
        # Calculate active reading time from interactions
        interactions = PDFInteraction.objects.filter(
            session=session,
            document=document,
            interaction_type='page_view'
        )
        
        active_time = sum(
            interaction.time_on_page_seconds or 0 
            for interaction in interactions
        )
        pdf_session.active_reading_time_seconds = int(active_time)
        
        # Calculate idle time
        pdf_session.idle_time_seconds = (
            pdf_session.total_session_duration_seconds - 
            pdf_session.active_reading_time_seconds
        )
        
        # Update statistics
        pdf_session.calculate_statistics()
        pdf_session.save()
        
        # Log session end interaction
        PDFInteraction.objects.create(
            session=session,
            user=request.user,
            document=document,
            interaction_type='session_end',
            cumulative_time_seconds=pdf_session.total_session_duration_seconds,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        return Response({
            'success': True,
            'pdf_session_id': pdf_session.id,
            'ended_at': pdf_session.pdf_ended_at,
            'total_duration_seconds': pdf_session.total_session_duration_seconds,
            'active_reading_time_seconds': pdf_session.active_reading_time_seconds,
            'idle_time_seconds': pdf_session.idle_time_seconds,
            'reading_completion_percentage': pdf_session.reading_completion_percentage,
            'total_interactions': pdf_session.total_interactions,
            'reading_pattern': pdf_session.get_reading_pattern(),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to end PDF session',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pdf_analytics(request):
    """Get PDF analytics for the current user"""
    try:
        # Get user's PDF sessions
        pdf_sessions = PDFSession.objects.filter(user=request.user)
        
        # Calculate overall statistics
        total_sessions = pdf_sessions.count()
        completed_sessions = pdf_sessions.filter(pdf_ended_at__isnull=False).count()
        
        total_reading_time = sum(
            session.active_reading_time_seconds or 0 
            for session in pdf_sessions
        )
        
        # Document-level statistics
        document_stats = {}
        for session in pdf_sessions:
            doc_id = session.document.id
            doc_title = session.document.title
            
            if doc_id not in document_stats:
                document_stats[doc_id] = {
                    'title': doc_title,
                    'sessions': 0,
                    'total_time': 0,
                    'completion_percentage': 0,
                    'interactions': 0,
                }
            
            document_stats[doc_id]['sessions'] += 1
            document_stats[doc_id]['total_time'] += session.active_reading_time_seconds or 0
            document_stats[doc_id]['completion_percentage'] = max(
                document_stats[doc_id]['completion_percentage'],
                session.reading_completion_percentage
            )
            document_stats[doc_id]['interactions'] += session.total_interactions
        
        return Response({
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_reading_time_seconds': total_reading_time,
            'document_statistics': document_stats,
            'average_reading_time_per_session': (
                total_reading_time / total_sessions if total_sessions > 0 else 0
            ),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve PDF analytics',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)