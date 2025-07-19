from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Quiz, QuizAttempt, QuizResponse, Question
from .serializers import QuizSerializer, QuizAttemptSerializer, QuizResponseSerializer
from apps.studies.models import StudySession, StudyLog
from apps.authentication.serializers import UserSerializer
from django.utils import timezone


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, is_active=True)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_by_type(request, quiz_type):
    """Get quiz by type (immediate_recall, transfer, pre_assessment)"""
    try:
        # Map frontend quiz types to backend quiz types
        type_mapping = {
            'immediate_recall': 'post',
            'transfer': 'post',  # For now, both use post type
            'pre_assessment': 'pre'
        }
        
        backend_type = type_mapping.get(quiz_type)
        if not backend_type:
            return Response({'error': 'Invalid quiz type'}, status=status.HTTP_400_BAD_REQUEST)
            
        # For now, return the hardcoded quiz structure from JSON
        import json
        import os
        from django.conf import settings
        
        # Map quiz types to JSON files
        json_files = {
            'immediate_recall': 'immediate-recall-quiz.json',
            'transfer': 'transfer-application-quiz.json',
            'pre_assessment': 'pre-assessment-quiz.json'
        }
        
        json_file = json_files.get(quiz_type)
        if not json_file:
            return Response({'error': 'Quiz type not found'}, status=status.HTTP_404_NOT_FOUND)
            
        json_path = os.path.join(settings.MEDIA_ROOT, json_file)
        
        if not os.path.exists(json_path):
            return Response({'error': 'Quiz file not found'}, status=status.HTTP_404_NOT_FOUND)
            
        with open(json_path, 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
            
        return Response(quiz_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, is_active=True)
        session = StudySession.objects.get(
            id=request.data.get('session_id'),
            user=request.user
        )
        
        attempt, created = QuizAttempt.objects.get_or_create(
            quiz=quiz,
            user=request.user,
            session=session,
            defaults={'started_at': timezone.now()}
        )
        
        if created:
            StudyLog.objects.create(
                session=session,
                log_type='quiz_answer',
                event_data={'action': 'start_quiz', 'quiz_id': str(quiz_id)}
            )
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except (Quiz.DoesNotExist, StudySession.DoesNotExist):
        return Response({'error': 'Quiz or session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request, attempt_id):
    try:
        attempt = QuizAttempt.objects.get(id=attempt_id, user=request.user)
        question = Question.objects.get(id=request.data.get('question_id'))
        
        answer_data = {
            'attempt': attempt.id,
            'question': question.id,
            'selected_choice': request.data.get('selected_choice'),
            'text_answer': request.data.get('text_answer', '')
        }
        
        answer, created = QuizResponse.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults=answer_data
        )
        
        if question.question_type == 'multiple_choice' and answer.selected_choice:
            answer.is_correct = answer.selected_choice.is_correct
            answer.save()
        
        StudyLog.objects.create(
            session=attempt.session,
            log_type='quiz_answer',
            event_data={
                'action': 'submit_answer',
                'question_id': str(question.id),
                'answer_id': str(answer.id),
                'is_correct': answer.is_correct
            }
        )
        
        serializer = QuizResponseSerializer(answer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except (QuizAttempt.DoesNotExist, Question.DoesNotExist):
        return Response({'error': 'Attempt or question not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, attempt_id):
    try:
        attempt = QuizAttempt.objects.get(id=attempt_id, user=request.user)
        
        if not attempt.is_completed:
            attempt.completed_at = timezone.now()
            attempt.is_completed = True
            
            time_taken = (attempt.completed_at - attempt.started_at).total_seconds()
            attempt.time_taken_seconds = int(time_taken)
            
            correct_answers = attempt.responses.filter(is_correct=True).count()
            total_questions = attempt.quiz.questions.count()
            attempt.score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            
            attempt.save()
            
            StudyLog.objects.create(
                session=attempt.session,
                log_type='quiz_answer',
                event_data={
                    'action': 'submit_quiz',
                    'score': attempt.score,
                    'time_taken_seconds': attempt.time_taken_seconds
                }
            )
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except QuizAttempt.DoesNotExist:
        return Response({'error': 'Attempt not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_attempts(request):
    attempts = QuizAttempt.objects.filter(user=request.user)
    serializer = QuizAttemptSerializer(attempts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz_results(request):
    """Submit quiz results and update user completion status"""
    try:
        quiz_type = request.data.get('quiz_type')
        score = request.data.get('score', 0)
        total_questions = request.data.get('total_questions', 0)
        correct_answers = request.data.get('correct_answers', 0)
        time_taken_seconds = request.data.get('time_taken_seconds', 0)
        answers = request.data.get('answers', [])
        
        if not quiz_type:
            return Response({
                'error': 'quiz_type is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Update user completion status based on quiz type
        if quiz_type == 'pre_assessment':
            user.pre_quiz_completed = True
            user.pre_quiz_completed_at = timezone.now()
        elif quiz_type == 'immediate_recall':
            user.post_quiz_completed = True
            user.post_quiz_completed_at = timezone.now()
        elif quiz_type == 'transfer':
            user.study_completed = True
            user.study_completed_at = timezone.now()
        
        user.save()
        
        # TODO: Save quiz attempt data to database if needed
        # For now, just update the user status
        
        return Response({
            'message': 'Quiz results submitted successfully',
            'user': UserSerializer(user).data,
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_answers
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to submit quiz results',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)