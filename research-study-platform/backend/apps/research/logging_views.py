"""
API endpoints for research data logging
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .logging_service import research_logger
from .models import ParticipantProfile


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@method_decorator(csrf_exempt)
def log_interaction(request):
    """
    Log a general interaction event
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "session_id": "sess_abc123",
        "log_type": "button_click",
        "event_data": {
            "button_id": "submit_btn",
            "page": "quiz"
        },
        "page_url": "https://example.com/quiz",
        "user_agent": "Mozilla/5.0...",
        "reaction_time_ms": 1500
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['participant_id', 'session_id', 'log_type', 'event_data']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Log the interaction
        success = research_logger.log_interaction(
            participant_id=data['participant_id'],
            session_id=data['session_id'],
            log_type=data['log_type'],
            event_data=data['event_data'],
            page_url=data.get('page_url'),
            user_agent=data.get('user_agent'),
            reaction_time_ms=data.get('reaction_time_ms')
        )
        
        if success:
            return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to log interaction'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@method_decorator(csrf_exempt)
def log_chat_interaction(request):
    """
    Log a ChatGPT interaction
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "session_id": "sess_abc123",
        "message_type": "user_message",
        "content": "What is machine learning?",
        "response_time_ms": 2000,
        "token_count": 150,
        "cost_usd": 0.003
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['participant_id', 'session_id', 'message_type', 'content']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Log the chat interaction
        success = research_logger.log_chat_interaction(
            participant_id=data['participant_id'],
            session_id=data['session_id'],
            message_type=data['message_type'],
            content=data['content'],
            response_time_ms=data.get('response_time_ms'),
            token_count=data.get('token_count'),
            cost_usd=data.get('cost_usd')
        )
        
        if success:
            return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to log chat interaction'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@method_decorator(csrf_exempt)
def log_pdf_viewing(request):
    """
    Log PDF viewing behavior
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "session_id": "sess_abc123",
        "pdf_name": "linux_tutorial.pdf",
        "pdf_hash": "abc123...",
        "page_number": 5,
        "time_spent_seconds": 45,
        "scroll_events": [
            {"timestamp": "2024-01-01T10:00:00Z", "scroll_y": 100},
            {"timestamp": "2024-01-01T10:00:05Z", "scroll_y": 200}
        ],
        "zoom_events": [
            {"timestamp": "2024-01-01T10:00:10Z", "zoom_level": 1.5}
        ],
        "search_queries": ["linux commands", "file permissions"]
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['participant_id', 'session_id', 'pdf_name', 'pdf_hash', 'page_number']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Log the PDF viewing
        success = research_logger.log_pdf_viewing(
            participant_id=data['participant_id'],
            session_id=data['session_id'],
            pdf_name=data['pdf_name'],
            pdf_hash=data['pdf_hash'],
            page_number=data['page_number'],
            time_spent_seconds=data.get('time_spent_seconds', 0),
            scroll_events=data.get('scroll_events', []),
            zoom_events=data.get('zoom_events', []),
            search_queries=data.get('search_queries', [])
        )
        
        if success:
            return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to log PDF viewing'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@method_decorator(csrf_exempt)
def log_quiz_response(request):
    """
    Log quiz response
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "session_id": "sess_abc123",
        "quiz_type": "pre_quiz",
        "question_id": "q1",
        "question_text": "What is the command to list files?",
        "question_type": "multiple_choice",
        "response_value": "ls",
        "response_text": "",
        "is_correct": true,
        "time_spent_seconds": 30,
        "changes_made": 2
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = [
            'participant_id', 'session_id', 'quiz_type', 'question_id',
            'question_text', 'question_type', 'response_value'
        ]
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Log the quiz response
        success = research_logger.log_quiz_response(
            participant_id=data['participant_id'],
            session_id=data['session_id'],
            quiz_type=data['quiz_type'],
            question_id=data['question_id'],
            question_text=data['question_text'],
            question_type=data['question_type'],
            response_value=data['response_value'],
            response_text=data.get('response_text', ''),
            is_correct=data.get('is_correct'),
            time_spent_seconds=data.get('time_spent_seconds', 0),
            changes_made=data.get('changes_made', 0)
        )
        
        if success:
            return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to log quiz response'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@method_decorator(csrf_exempt)
def log_session_event(request):
    """
    Log session-level events
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "session_id": "sess_abc123",
        "event_type": "session_start",
        "event_data": {
            "user_agent": "Mozilla/5.0...",
            "screen_resolution": "1920x1080",
            "timezone": "UTC-5"
        }
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['participant_id', 'session_id', 'event_type']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Log the session event
        success = research_logger.log_session_event(
            participant_id=data['participant_id'],
            session_id=data['session_id'],
            event_type=data['event_type'],
            event_data=data.get('event_data')
        )
        
        if success:
            return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to log session event'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@method_decorator(csrf_exempt)
def log_navigation_event(request):
    """
    Log navigation events
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "session_id": "sess_abc123",
        "from_page": "/quiz",
        "to_page": "/chat",
        "navigation_type": "click"
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['participant_id', 'session_id', 'from_page', 'to_page']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Log the navigation event
        success = research_logger.log_navigation_event(
            participant_id=data['participant_id'],
            session_id=data['session_id'],
            from_page=data['from_page'],
            to_page=data['to_page'],
            navigation_type=data.get('navigation_type', 'click')
        )
        
        if success:
            return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to log navigation event'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@method_decorator(csrf_exempt)
def log_error_event(request):
    """
    Log error events
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "session_id": "sess_abc123",
        "error_type": "javascript_error",
        "error_message": "TypeError: Cannot read property 'length' of undefined",
        "error_context": {
            "stack_trace": "...",
            "line_number": 42,
            "file": "quiz.js"
        }
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['participant_id', 'session_id', 'error_type', 'error_message']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Log the error event
        success = research_logger.log_error_event(
            participant_id=data['participant_id'],
            session_id=data['session_id'],
            error_type=data['error_type'],
            error_message=data['error_message'],
            error_context=data.get('error_context')
        )
        
        if success:
            return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to log error event'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@method_decorator(csrf_exempt)
def bulk_log_interactions(request):
    """
    Bulk log multiple interactions
    
    Expected payload:
    {
        "interactions": [
            {
                "participant_id": "P12345678",
                "session_id": "sess_abc123",
                "log_type": "button_click",
                "event_data": {"button_id": "submit_btn"}
            },
            {
                "participant_id": "P12345678",
                "session_id": "sess_abc123",
                "log_type": "page_view",
                "event_data": {"page": "quiz"}
            }
        ]
    }
    """
    try:
        data = request.data
        
        if 'interactions' not in data:
            return Response(
                {'error': 'Missing required field: interactions'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Bulk log the interactions
        results = research_logger.bulk_log_interactions(data['interactions'])
        
        return Response(results, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_summary(request):
    """
    Get session summary for a participant
    
    Query parameters:
    - participant_id: Anonymized participant ID
    - session_id: Session identifier
    """
    try:
        participant_id = request.GET.get('participant_id')
        session_id = request.GET.get('session_id')
        
        if not participant_id or not session_id:
            return Response(
                {'error': 'participant_id and session_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        summary = research_logger.get_participant_session_summary(
            participant_id=participant_id,
            session_id=session_id
        )
        
        return Response(summary, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_participant_logs(request):
    """
    Get all logs for a participant
    
    Query parameters:
    - participant_id: Anonymized participant ID
    - session_id: Session identifier (optional)
    - log_type: Filter by log type (optional)
    - limit: Limit number of results (optional, default 100)
    """
    try:
        participant_id = request.GET.get('participant_id')
        session_id = request.GET.get('session_id')
        log_type = request.GET.get('log_type')
        limit = int(request.GET.get('limit', 100))
        
        if not participant_id:
            return Response(
                {'error': 'participant_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get participant
        try:
            participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
        except ParticipantProfile.DoesNotExist:
            return Response(
                {'error': 'Participant not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Build query
        from .models import InteractionLog
        logs = InteractionLog.objects.filter(participant=participant)
        
        if session_id:
            logs = logs.filter(session_id=session_id)
        
        if log_type:
            logs = logs.filter(log_type=log_type)
        
        logs = logs.order_by('-timestamp')[:limit]
        
        # Serialize logs
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': str(log.id),
                'log_type': log.log_type,
                'event_data': log.event_data,
                'timestamp': log.timestamp.isoformat(),
                'session_id': log.session_id,
                'page_url': log.page_url,
                'reaction_time_ms': log.reaction_time_ms,
                'time_since_last_action_ms': log.time_since_last_action_ms
            })
        
        return Response({
            'participant_id': participant_id,
            'logs': logs_data,
            'total_count': logs.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )