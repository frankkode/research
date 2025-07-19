from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatInteraction, ChatSession
from .serializers import ChatInteractionSerializer, ChatSessionSerializer, ChatMessageSerializer, ChatResponseSerializer
from .services import OpenAIService
from .cost_management import CostManagementService
from apps.studies.models import StudySession, StudyLog
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """Send a chat message and get response"""
    try:
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get study session
        session = StudySession.objects.get(
            session_id=serializer.validated_data['session_id'],
            user=request.user
        )
        
        # Verify user is in CHATGPT group
        if session.user.study_group != 'CHATGPT':
            return Response({
                'error': 'Chat functionality is only available for CHATGPT group'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check user cost limits
        user_limits = CostManagementService.check_user_limits(request.user.id)
        if user_limits['daily_limit_exceeded']:
            return Response({
                'error': 'Daily cost limit exceeded. Please try again tomorrow.',
                'daily_cost': float(user_limits['daily_cost']),
                'daily_remaining': float(user_limits['daily_remaining'])
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        if user_limits['weekly_limit_exceeded']:
            return Response({
                'error': 'Weekly cost limit exceeded. Please try again next week.',
                'weekly_cost': float(user_limits['weekly_cost']),
                'weekly_remaining': float(user_limits['weekly_remaining'])
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Check system limits
        system_limits = CostManagementService.get_system_limits()
        if system_limits['daily_limit_exceeded']:
            return Response({
                'error': 'System daily cost limit exceeded. Please try again tomorrow.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Initialize OpenAI service
        try:
            openai_service = OpenAIService()
            logger.debug(f"OpenAI service initialized for user {request.user.id}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI service: {str(e)}")
            return Response({'error': f'Failed to initialize chat service: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get or create chat session
        try:
            chat_session, created = openai_service.get_or_create_chat_session(session)
            logger.debug(f"Chat session {'created' if created else 'retrieved'}: {chat_session.id}")
        except Exception as e:
            logger.error(f"Failed to get/create chat session: {str(e)}")
            return Response({'error': f'Failed to initialize chat session: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create chat interaction
        try:
            logger.debug(f"Creating chat interaction for message: {serializer.validated_data['message'][:50]}...")
            result = openai_service.create_chat_interaction(
                session=session,
                user_message=serializer.validated_data['message'],
                conversation_turn=serializer.validated_data['conversation_turn']
            )
            logger.debug(f"Chat interaction result: success={result.get('success', False)}")
        except Exception as e:
            logger.error(f"Failed to create chat interaction: {str(e)}")
            return Response({'error': f'Failed to process message: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if result['success']:
            # Update chat session statistics
            chat_session.calculate_statistics()
            
            # Create response
            response_data = {
                'user_message': result['user_interaction'].user_message,
                'assistant_response': result['assistant_interaction'].assistant_response,
                'response_time_ms': result['assistant_interaction'].response_time_ms,
                'total_tokens': result['assistant_interaction'].total_tokens,
                'conversation_turn': result['assistant_interaction'].conversation_turn,
                'interaction_id': result['assistant_interaction'].id
            }
            
            response_serializer = ChatResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request, session_id):
    """Get chat history for a session"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        
        interactions = ChatInteraction.objects.filter(
            session=session
        ).order_by('conversation_turn', 'message_timestamp')
        
        serializer = ChatInteractionSerializer(interactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_session(request, session_id):
    """Get chat session statistics"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        
        try:
            chat_session = ChatSession.objects.get(session=session)
            serializer = ChatSessionSerializer(chat_session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_chat_session(request, session_id):
    """Initialize chat session for a study session"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        
        # Verify user is in CHATGPT group
        if session.user.study_group != 'CHATGPT':
            return Response({
                'error': 'Chat functionality is only available for CHATGPT group'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get or create chat session
        try:
            openai_service = OpenAIService()
            chat_session, created = openai_service.get_or_create_chat_session(session)
        except Exception as openai_error:
            logger.error(f"OpenAI service error: {str(openai_error)}")
            # Try direct database creation as fallback
            try:
                chat_session, created = ChatSession.objects.get_or_create(
                    session=session,
                    defaults={'user': session.user}
                )
                logger.info(f"Fallback chat session creation successful: {created}")
            except Exception as db_error:
                logger.error(f"Fallback chat session creation failed: {str(db_error)}")
                return Response({'error': f'Failed to initialize chat service: {str(openai_error)}. Fallback also failed: {str(db_error)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Log chat session start
        try:
            StudyLog.objects.create(
                session=session,
                log_type='chat_message',
                event_data={'action': 'start_chat_session', 'created': created}
            )
        except Exception as log_error:
            logger.warning(f"Failed to log chat session start: {str(log_error)}")
            # Continue anyway, logging failure shouldn't stop the process
        
        serializer = ChatSessionSerializer(chat_session)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in start_chat_session: {str(e)}")
        return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_chat_session(request, session_id):
    """End chat session"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        
        try:
            chat_session = ChatSession.objects.get(session=session)
            
            if not chat_session.chat_ended_at:
                from django.utils import timezone
                chat_session.chat_ended_at = timezone.now()
                
                # Calculate final duration
                if chat_session.chat_started_at:
                    duration = (chat_session.chat_ended_at - chat_session.chat_started_at).total_seconds()
                    chat_session.total_chat_duration_seconds = int(duration)
                
                chat_session.save()
                
                # Final statistics calculation
                chat_session.calculate_statistics()
                
                # Log chat session end
                StudyLog.objects.create(
                    session=session,
                    log_type='chat_message',
                    event_data={
                        'action': 'end_chat_session',
                        'duration_seconds': chat_session.total_chat_duration_seconds,
                        'total_messages': chat_session.total_messages
                    }
                )
            
            serializer = ChatSessionSerializer(chat_session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ChatSession.DoesNotExist:
            return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)