#!/usr/bin/env python3
"""
Simple script to create 4 test users directly in Django
Run this from the backend directory after activating virtual environment
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append('/Users/masabosimplicefrank/linux-learning-study/research-study-platform/backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')

try:
    django.setup()
    
    from django.utils import timezone
    from apps.core.models import User
    from apps.studies.models import StudySession
    from apps.research.models import ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction, PDFViewingBehavior, QuizResponse
    from apps.chats.models import ChatSession
    from apps.pdfs.models import PDFSession
    from apps.quizzes.models import Quiz, QuizAttempt, Question, Choice

    print("🚀 Creating 4 test users for dashboard testing...")

    # Clear existing test users
    User.objects.filter(username__startswith='testuser').delete()
    print("✅ Cleared existing test users")

    # Create or get research study
    study, created = ResearchStudy.objects.get_or_create(
        name='Linux Learning Study - Test',
        defaults={
            'description': 'Test study for dashboard testing',
            'is_active': True,
            'created_by_id': 1  # Assuming admin user with id=1 exists
        }
    )
    print(f"✅ {'Created' if created else 'Found'} research study")

    # Test users data
    users_data = [
        {
            'username': 'testuser1',
            'email': 'test1@example.com',
            'group': 'CHATGPT',
            'completed': True,
            'pre_score': 45.0,
            'post_score': 85.0
        },
        {
            'username': 'testuser2', 
            'email': 'test2@example.com',
            'group': 'CHATGPT',
            'completed': True,
            'pre_score': 50.0,
            'post_score': 90.0
        },
        {
            'username': 'testuser3',
            'email': 'test3@example.com', 
            'group': 'PDF',
            'completed': True,
            'pre_score': 40.0,
            'post_score': 75.0
        },
        {
            'username': 'testuser4',
            'email': 'test4@example.com',
            'group': 'PDF', 
            'completed': False,
            'pre_score': 55.0,
            'post_score': None
        }
    ]

    for i, user_data in enumerate(users_data):
        print(f"👤 Creating user {i+1}: {user_data['username']} ({user_data['group']})")
        
        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password='testpass123',
            study_group=user_data['group'],
            consent_completed=True,
            pre_quiz_completed=True,
            interaction_completed=user_data['completed'],
            post_quiz_completed=user_data['completed'],
            study_completed=user_data['completed'],
            participant_id=f'TEST{i+1:03d}',
            study_completed_at=timezone.now() - timedelta(days=i+1) if user_data['completed'] else None
        )

        # Create participant profile
        participant = ParticipantProfile.objects.create(
            user=user,
            study=study,
            assigned_group=user_data['group'],
            consent_given=True,
            created_at=timezone.now() - timedelta(days=10+i)
        )

        # Create study session
        session_duration = 3600 + (i * 300)  # 1 hour + i*5 minutes
        session = StudySession.objects.create(
            user=user,
            session_id=f'session_{user_data["username"]}',
            session_started_at=timezone.now() - timedelta(days=5+i),
            session_ended_at=timezone.now() - timedelta(days=5+i, hours=-1) if user_data['completed'] else None,
            total_duration=session_duration,
            interaction_duration=session_duration - 600,
            is_active=not user_data['completed']
        )

        # Create interaction logs
        for j in range(10):
            InteractionLog.objects.create(
                participant=participant,
                log_type=['page_view', 'click', 'scroll', 'chat_message', 'quiz_answer'][j % 5],
                event_data={'action': f'test_action_{j}', 'user_id': user.id},
                timestamp=timezone.now() - timedelta(hours=j)
            )

        # Create group-specific data
        if user_data['group'] == 'CHATGPT':
            # Create chat session
            chat_session = ChatSession.objects.create(
                session=session,
                total_messages=10 + i*3,
                total_tokens_used=1000 + i*500,
                total_cost=0.05 + i*0.02,
                session_started_at=session.session_started_at,
                session_ended_at=session.session_ended_at
            )

            # Create chat interactions
            for k in range(6):
                ChatInteraction.objects.create(
                    participant=participant,
                    message_type='user' if k % 2 == 0 else 'assistant',
                    user_message=f'How do I use the ls command?' if k % 2 == 0 else '',
                    assistant_response=f'The ls command lists directory contents. Use ls -la for detailed view.' if k % 2 == 1 else '',
                    response_time_ms=1000 + k*200,
                    token_count=50 + k*10,
                    cost_usd=0.005 + k*0.001,
                    message_timestamp=timezone.now() - timedelta(hours=k),
                    conversation_turn=k + 1
                )

        else:  # PDF group
            # Create PDF session
            pdf_session = PDFSession.objects.create(
                session=session,
                unique_pages_visited=8 + i*2,
                total_time_spent=2400 + i*300,
                session_started_at=session.session_started_at,
                session_ended_at=session.session_ended_at
            )

            # Create PDF interactions
            for k in range(10):
                PDFViewingBehavior.objects.create(
                    participant=participant,
                    pdf_name='linux-commands-reference.pdf',
                    page_number=(k % 15) + 1,
                    time_spent_seconds=120 + k*30,
                    timestamp=timezone.now() - timedelta(hours=k)
                )

        # Create quiz responses
        for quiz_type in ['pre', 'post']:
            if quiz_type == 'post' and not user_data['completed']:
                continue
                
            score = user_data[f'{quiz_type}_score']
            if score is None:
                continue
                
            # Create quiz responses for research models
            for q_num in range(3):  # 3 questions per quiz
                is_correct = (q_num * 25 + 25) <= score
                QuizResponse.objects.create(
                    participant=participant,
                    quiz_type=quiz_type,
                    question_text=f'{quiz_type.title()}-quiz question {q_num+1}: Linux command knowledge',
                    selected_answer='Option 1' if is_correct else 'Option 2',
                    correct_answer='Option 1',
                    is_correct=is_correct,
                    time_spent_seconds=60 + q_num*15,
                    answered_at=timezone.now() - timedelta(days=6+i if quiz_type=='pre' else 1+i, minutes=q_num*2)
                )

    print("\n✅ Successfully created 4 test users!")
    
    # Print summary
    print('\n📊 DATA SUMMARY:')
    print(f'   Total Users: {User.objects.count()}')
    print(f'   ChatGPT Group: {User.objects.filter(study_group="CHATGPT").count()}')
    print(f'   PDF Group: {User.objects.filter(study_group="PDF").count()}')
    print(f'   Completed Studies: {User.objects.filter(study_completed=True).count()}')
    print(f'   Study Sessions: {StudySession.objects.count()}')
    print(f'   Chat Interactions: {ChatInteraction.objects.count()}')
    print(f'   PDF Interactions: {PDFViewingBehavior.objects.count()}')
    print(f'   Quiz Responses: {QuizResponse.objects.count()}')
    
    print('\n👥 USER DETAILS:')
    for user in User.objects.filter(username__startswith='testuser'):
        print(f'   {user.username}: {user.study_group} group, completed: {user.study_completed}')
    
    print('\n🎯 NEXT STEPS:')
    print('1. Make sure Django server is running: python manage.py runserver 8000')
    print('2. Go to Admin Dashboard → "Debug Data" tab')
    print('3. Click "Run Diagnostics" to verify data')
    print('4. Check other dashboard tabs for visualizations')

except ImportError as e:
    print(f"❌ Django import error: {e}")
    print("💡 Make sure you're in the backend directory and Django is installed")
    print("Run: pip install django")
except Exception as e:
    print(f"❌ Error creating test data: {e}")
    print("💡 Make sure Django server can connect to database")