from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import StudySession, StudyLog
from .serializers import StudySessionSerializer, StudyLogSerializer, PhaseUpdateSerializer, SessionCreateSerializer
import uuid


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_session(request):
    """Create or retrieve current study session for user"""
    try:
        # Check if user already has an active session
        session = StudySession.objects.filter(user=request.user, is_active=True).first()
        
        if session:
            serializer = StudySessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new session
        session_data = SessionCreateSerializer(data=request.data)
        if session_data.is_valid():
            session = StudySession.objects.create(
                user=request.user,
                session_id=str(uuid.uuid4()),
                current_phase='consent',
                user_agent=session_data.validated_data.get('user_agent', ''),
                ip_address=get_client_ip(request)
            )
            
            # Log session creation
            StudyLog.objects.create(
                session=session,
                log_type='session_start',
                event_data={'user_agent': session.user_agent, 'ip_address': str(session.ip_address)}
            )
            
            serializer = StudySessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(session_data.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session(request, session_id):
    """Get specific study session"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        serializer = StudySessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_session(request):
    """Get current active session for user"""
    try:
        session = StudySession.objects.filter(user=request.user, is_active=True).first()
        if session:
            serializer = StudySessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'No active session found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_phase(request, session_id):
    """Update current phase of study session"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        serializer = PhaseUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            new_phase = serializer.validated_data['phase']
            old_phase = session.current_phase
            timestamp = serializer.validated_data.get('timestamp', timezone.now())
            
            # Update phase timing
            if new_phase != old_phase:
                # End previous phase
                if old_phase:
                    end_field = f"{old_phase}_ended_at"
                    if hasattr(session, end_field):
                        setattr(session, end_field, timestamp)
                        
                        # Calculate duration
                        start_field = f"{old_phase}_started_at"
                        if hasattr(session, start_field):
                            start_time = getattr(session, start_field)
                            if start_time:
                                duration = (timestamp - start_time).total_seconds()
                                session.set_phase_duration(old_phase, int(duration))
                
                # Start new phase
                start_field = f"{new_phase}_started_at"
                if hasattr(session, start_field):
                    setattr(session, start_field, timestamp)
                
                session.current_phase = new_phase
                
                # Update user completion status based on old phase completion
                print(f"DEBUG: Phase transition - old_phase: '{old_phase}', new_phase: '{new_phase}'")
                print(f"DEBUG: Current user completion status BEFORE update:")
                print(f"DEBUG:   - consent_completed: {session.user.consent_completed}")
                print(f"DEBUG:   - pre_quiz_completed: {session.user.pre_quiz_completed}")
                print(f"DEBUG:   - interaction_completed: {session.user.interaction_completed}")
                print(f"DEBUG:   - post_quiz_completed: {session.user.post_quiz_completed}")
                print(f"DEBUG:   - study_completed: {session.user.study_completed}")
                
                if old_phase == 'consent':
                    session.user.consent_completed = True
                    session.user.consent_completed_at = timestamp
                    print(f"DEBUG: Marked consent as completed")
                elif old_phase == 'pre_quiz':
                    session.user.pre_quiz_completed = True
                    session.user.pre_quiz_completed_at = timestamp
                    print(f"DEBUG: Marked pre_quiz as completed")
                elif old_phase == 'interaction':
                    print(f"DEBUG: Marking interaction as completed (leaving interaction phase)")
                    session.user.interaction_completed = True
                    session.user.interaction_completed_at = timestamp
                    print(f"DEBUG: Interaction marked as completed")
                elif old_phase == 'post_quiz':
                    print(f"DEBUG: WARNING! Marking post_quiz as completed (leaving post_quiz phase)")
                    session.user.post_quiz_completed = True
                    session.user.post_quiz_completed_at = timestamp
                    print(f"DEBUG: Post_quiz marked as completed")
                
                # Handle final completion - ONLY when explicitly setting to completed
                if new_phase == 'completed':
                    # Only mark study as completed if we're actually finishing the entire study
                    # This should only happen after all phases are complete
                    if (session.user.consent_completed and 
                        session.user.pre_quiz_completed and 
                        session.user.interaction_completed and 
                        session.user.post_quiz_completed):
                        session.user.study_completed = True
                        session.user.study_completed_at = timestamp
                        session.is_completed = True
                        session.session_ended_at = timestamp
                        session.is_active = False
                        print(f"DEBUG: Study marked as fully completed for user {session.user.participant_id}")
                    else:
                        print(f"DEBUG: Not marking study as completed - missing prerequisites")
                        print(f"DEBUG: consent={session.user.consent_completed}, pre_quiz={session.user.pre_quiz_completed}, interaction={session.user.interaction_completed}, post_quiz={session.user.post_quiz_completed}")
                
                # IMPORTANT: Do NOT mark study as completed when just moving to post_quiz
                # The post_quiz phase should only be accessible, not automatically completed
                elif new_phase == 'post_quiz':
                    print(f"DEBUG: Moving to post_quiz phase - interaction should be marked as completed but study should NOT be fully completed")
                    print(f"DEBUG: Current completion status: consent={session.user.consent_completed}, pre_quiz={session.user.pre_quiz_completed}, interaction={session.user.interaction_completed}, post_quiz={session.user.post_quiz_completed}")
                
                print(f"DEBUG: Current user completion status AFTER update:")
                print(f"DEBUG:   - consent_completed: {session.user.consent_completed}")
                print(f"DEBUG:   - pre_quiz_completed: {session.user.pre_quiz_completed}")
                print(f"DEBUG:   - interaction_completed: {session.user.interaction_completed}")
                print(f"DEBUG:   - post_quiz_completed: {session.user.post_quiz_completed}")
                print(f"DEBUG:   - study_completed: {session.user.study_completed}")
                
                session.user.save()
                print(f"DEBUG: User saved successfully")
                
                # Refresh user from database to ensure we have the latest state
                session.user.refresh_from_db()
                print(f"DEBUG: User refreshed from DB. Final completion status:")
                print(f"DEBUG:   - consent_completed: {session.user.consent_completed}")
                print(f"DEBUG:   - pre_quiz_completed: {session.user.pre_quiz_completed}")
                print(f"DEBUG:   - interaction_completed: {session.user.interaction_completed}")
                print(f"DEBUG:   - post_quiz_completed: {session.user.post_quiz_completed}")
                print(f"DEBUG:   - study_completed: {session.user.study_completed}")
                
                session.save()
                print(f"DEBUG: Session saved. Current phase: {session.current_phase}")
                
                # Log phase change
                StudyLog.objects.create(
                    session=session,
                    log_type='phase_end',
                    event_data={'old_phase': old_phase, 'new_phase': new_phase}
                )
            
            serializer = StudySessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_event(request):
    """Log study events"""
    try:
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        log_type = request.data.get('log_type')
        if not log_type:
            return Response({'error': 'log_type is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        
        log_data = {
            'session': session.id,
            'log_type': log_type,
            'event_data': request.data.get('event_data', {})
        }
        
        serializer = StudyLogSerializer(data=log_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_logs(request, session_id):
    """Get all logs for a specific session"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        logs = StudyLog.objects.filter(session=session)
        serializer = StudyLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request, session_id):
    """End current study session"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        
        if session.is_active:
            session.is_active = False
            session.session_ended_at = timezone.now()
            session.calculate_total_duration()
            session.save()
            
            # Log session end
            StudyLog.objects.create(
                session=session,
                log_type='session_end',
                event_data={'total_duration': session.total_duration}
            )
        
        serializer = StudySessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_studies(request):
    """Get all active studies available for participation"""
    try:
        # For now, return a mock study since we have one main study
        studies = [
            {
                'id': 'linux-learning-study',
                'title': 'Linux Learning Study: PDF vs ChatGPT',
                'description': 'Comparing learning effectiveness between traditional documentation and interactive AI assistance',
                'is_active': True,
                'max_participants': 200,
                'duration_minutes': 50
            }
        ]
        return Response(studies, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_sessions(request):
    """Get all sessions for the current user"""
    try:
        sessions = StudySession.objects.filter(user=request.user).order_by('-created_at')
        serializer = StudySessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_study(request, study_id):
    """Join a study and create a new session"""
    try:
        # Check if user already has an active session
        existing_session = StudySession.objects.filter(user=request.user, is_active=True).first()
        
        if existing_session:
            serializer = StudySessionSerializer(existing_session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new session for the study
        session = StudySession.objects.create(
            user=request.user,
            session_id=str(uuid.uuid4()),
            current_phase='consent',
            user_agent=request.data.get('user_agent', ''),
            ip_address=get_client_ip(request)
        )
        
        # Log session creation
        StudyLog.objects.create(
            session=session,
            log_type='study_joined',
            event_data={'study_id': study_id, 'user_agent': session.user_agent}
        )
        
        serializer = StudySessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_session(request, session_id):
    """Complete a study session - should only be called when the entire study is finished"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        
        print(f"DEBUG: complete_session called for user {session.user.participant_id}")
        print(f"DEBUG: Current phase: {session.current_phase}")
        print(f"DEBUG: WARNING: complete_session should only be called when finishing the entire study, not individual phases")
        print(f"DEBUG: Current completion status before complete_session:")
        print(f"DEBUG:   - consent_completed: {session.user.consent_completed}")
        print(f"DEBUG:   - pre_quiz_completed: {session.user.pre_quiz_completed}")
        print(f"DEBUG:   - interaction_completed: {session.user.interaction_completed}")
        print(f"DEBUG:   - post_quiz_completed: {session.user.post_quiz_completed}")
        print(f"DEBUG:   - study_completed: {session.user.study_completed}")
        
        if not session.is_completed:
            session.is_completed = True
            session.is_active = False
            session.current_phase = 'completed'
            session.session_ended_at = timezone.now()
            session.calculate_total_duration()
            
            # Only mark study as completed if all phases are actually complete
            if (session.user.consent_completed and 
                session.user.pre_quiz_completed and 
                session.user.interaction_completed and 
                session.user.post_quiz_completed):
                session.user.study_completed = True
                session.user.study_completed_at = timezone.now()
                print(f"DEBUG: Study marked as fully completed via complete_session for user {session.user.participant_id}")
            else:
                print(f"DEBUG: Session completed but study not marked as completed - missing prerequisites")
                print(f"DEBUG: consent={session.user.consent_completed}, pre_quiz={session.user.pre_quiz_completed}, interaction={session.user.interaction_completed}, post_quiz={session.user.post_quiz_completed}")
            
            session.user.save()
            session.save()
            
            # Log session completion
            StudyLog.objects.create(
                session=session,
                log_type='session_end',
                event_data={'total_duration': session.total_duration, 'completed': True}
            )
        
        serializer = StudySessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_session_time(request, session_id):
    """Update session time tracking (for pause/resume functionality)"""
    try:
        session = StudySession.objects.get(session_id=session_id, user=request.user)
        
        time_spent = request.data.get('time_spent', 0)  # in seconds
        is_paused = request.data.get('is_paused', False)
        
        # Update interaction duration
        if session.current_phase == 'interaction':
            session.interaction_duration += time_spent
            session.save()
        
        # Log the time update
        StudyLog.objects.create(
            session=session,
            log_type='time_spent',
            event_data={
                'time_spent': time_spent,
                'is_paused': is_paused,
                'current_phase': session.current_phase,
                'total_interaction_time': session.interaction_duration
            }
        )
        
        serializer = StudySessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except StudySession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)