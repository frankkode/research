from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.core.models import User
from apps.studies.models import StudySession, StudyLog
from apps.research.models import ResearchStudy, ParticipantProfile, InteractionLog, QuizResponse
from apps.chats.models import ChatSession, ChatInteraction
from apps.pdfs.models import PDFSession, PDFInteraction, PDFDocument
from apps.quizzes.models import Quiz, QuizAttempt, QuizResponse as OldQuizResponse, Question, QuestionChoice


class Command(BaseCommand):
    help = 'Create 5 test users with realistic data for dashboard testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before creating new data'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing test data...')
            User.objects.filter(username__startswith='testuser').delete()
            # Clear quiz data to avoid conflicts
            Quiz.objects.filter(title__startswith='Pre-Assessment').delete()
            Quiz.objects.filter(title__startswith='Post-Assessment').delete()

        self.stdout.write('Creating 5 test users with realistic data...')

        # Create or get admin user for study creation
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'participant_id': 'ADMIN001',
                'study_group': 'PDF',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user')

        # Create or get research study
        study, created = ResearchStudy.objects.get_or_create(
            name='Linux Learning Study - Test',
            defaults={
                'description': 'Test study for dashboard testing',
                'is_active': True,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write('Created research study')

        # Create 5 test users
        users_data = [
            {
                'username': 'testuser1',
                'email': 'test1@example.com',
                'group': 'CHATGPT',
                'completed': True,
                'pre_score': 45,
                'post_score': 85
            },
            {
                'username': 'testuser2', 
                'email': 'test2@example.com',
                'group': 'CHATGPT',
                'completed': True,
                'pre_score': 50,
                'post_score': 90
            },
            {
                'username': 'testuser3',
                'email': 'test3@example.com', 
                'group': 'PDF',
                'completed': True,
                'pre_score': 40,
                'post_score': 75
            },
            {
                'username': 'testuser4',
                'email': 'test4@example.com',
                'group': 'PDF', 
                'completed': False,
                'pre_score': 55,
                'post_score': None
            },
            {
                'username': 'testuser5',
                'email': 'test5@example.com',
                'group': 'CHATGPT',
                'completed': True,
                'pre_score': 38,
                'post_score': 82
            }
        ]

        for i, user_data in enumerate(users_data):
            self.stdout.write(f'Creating user {i+1}: {user_data["username"]}')
            
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
            for j in range(10 + i*5):
                InteractionLog.objects.create(
                    participant=participant,
                    log_type=['page_view', 'click', 'scroll', 'chat_message', 'quiz_answer'][j % 5],
                    event_data={'action': f'test_action_{j}', 'user_id': str(user.id)},
                    timestamp=timezone.now() - timedelta(hours=j)
                )

            # Create group-specific data
            if user_data['group'] == 'CHATGPT':
                # Create chat session
                chat_session = ChatSession.objects.create(
                    session=session,
                    user=user,
                    total_messages=10 + i*3,
                    total_tokens_used=1000 + i*500,
                    total_estimated_cost_usd=0.05 + i*0.02,
                    chat_started_at=session.session_started_at,
                    chat_ended_at=session.session_ended_at
                )

                # Create chat interactions
                for k in range(5 + i*2):
                    ChatInteraction.objects.create(
                        session=session,
                        user=user,
                        message_type='user_message' if k % 2 == 0 else 'assistant_response',
                        user_message=f'Test question {k+1} about Linux commands' if k % 2 == 0 else '',
                        assistant_response=f'Test answer {k+1} about Linux usage' if k % 2 == 1 else '',
                        response_time_ms=1000 + k*200,
                        total_tokens=50 + k*10,
                        estimated_cost_usd=0.005 + k*0.001,
                        message_timestamp=timezone.now() - timedelta(hours=k),
                        conversation_turn=k + 1
                    )

            else:  # PDF group
                # Create or get PDF document
                pdf_doc, created = PDFDocument.objects.get_or_create(
                    title='Linux Commands Reference',
                    defaults={
                        'description': 'Comprehensive guide to Linux commands',
                        'file_path': 'media/linux-commands-reference.md',
                        'page_count': 15,
                        'study_group': 'PDF'
                    }
                )
                
                # Create PDF session
                pdf_session = PDFSession.objects.create(
                    session=session,
                    user=user,
                    document=pdf_doc,
                    unique_pages_visited=8 + i*2,
                    total_session_duration_seconds=2400 + i*300,
                    pdf_started_at=session.session_started_at,
                    pdf_ended_at=session.session_ended_at
                )

                # Create PDF interactions
                for k in range(8 + i*2):
                    PDFInteraction.objects.create(
                        session=session,
                        user=user,
                        document=pdf_doc,
                        interaction_type='page_view',
                        page_number=(k % 15) + 1,
                        time_on_page_seconds=120 + k*30,
                        timestamp=timezone.now() - timedelta(hours=k)
                    )

            # Create quiz data
            # Create quizzes if they don't exist
            pre_quiz, _ = Quiz.objects.get_or_create(
                quiz_type='pre',
                defaults={
                    'title': 'Pre-Assessment Quiz',
                    'description': 'Test your initial knowledge'
                }
            )
            
            post_quiz, _ = Quiz.objects.get_or_create(
                quiz_type='post', 
                defaults={
                    'title': 'Post-Assessment Quiz',
                    'description': 'Test your learned knowledge'
                }
            )

            # Create questions if they don't exist
            if not pre_quiz.questions.exists():
                for q in range(3):
                    question = Question.objects.create(
                        quiz=pre_quiz,
                        question_text=f'Pre-quiz question {q+1}: Basic Linux command knowledge',
                        question_type='multiple_choice',
                        order=q+1
                    )
                    
                    for c in range(4):
                        QuestionChoice.objects.create(
                            question=question,
                            choice_text=f'Option {c+1}',
                            is_correct=(c == 0),
                            order=c+1
                        )

            if not post_quiz.questions.exists():
                for q in range(3):
                    question = Question.objects.create(
                        quiz=post_quiz,
                        question_text=f'Post-quiz question {q+1}: Advanced Linux command usage',
                        question_type='multiple_choice',
                        order=q+1
                    )
                    
                    for c in range(4):
                        QuestionChoice.objects.create(
                            question=question,
                            choice_text=f'Option {c+1}',
                            is_correct=(c == 0),
                            order=c+1
                        )

            # Create pre-quiz attempt
            pre_attempt = QuizAttempt.objects.create(
                user=user,
                quiz=pre_quiz,
                session=session,
                score=user_data['pre_score'],
                percentage_score=user_data['pre_score'],
                is_completed=True,
                started_at=timezone.now() - timedelta(days=6+i),
                completed_at=timezone.now() - timedelta(days=6+i, hours=-1)
            )

            # Create pre-quiz responses  
            for q_num, question in enumerate(pre_quiz.questions.all()):
                is_correct = (q_num * 20 + 20) <= user_data['pre_score']  # Distribute correctness
                QuizResponse.objects.create(
                    participant=participant,
                    session_id=session.session_id,
                    quiz_type='pre_quiz',
                    question_id=str(question.id),
                    question_text=question.question_text,
                    question_type=question.question_type,
                    response_value={'selected': 'Option 1' if is_correct else 'Option 2'},
                    response_text='Option 1' if is_correct else 'Option 2',
                    is_correct=is_correct,
                    time_spent_seconds=60 + q_num*15,
                    first_viewed_at=timezone.now() - timedelta(days=6+i, hours=-1, minutes=q_num*2+1),
                    submitted_at=timezone.now() - timedelta(days=6+i, hours=-1, minutes=q_num*2)
                )

            # Create post-quiz if completed
            if user_data['completed'] and user_data['post_score']:
                post_attempt = QuizAttempt.objects.create(
                    user=user,
                    quiz=post_quiz,
                    session=session,
                    score=user_data['post_score'],
                    percentage_score=user_data['post_score'],
                    is_completed=True,
                    started_at=timezone.now() - timedelta(days=1+i),
                    completed_at=timezone.now() - timedelta(days=1+i, hours=-1)
                )

                # Create post-quiz responses
                for q_num, question in enumerate(post_quiz.questions.all()):
                    is_correct = (q_num * 25 + 25) <= user_data['post_score']  # Distribute correctness
                    QuizResponse.objects.create(
                        participant=participant,
                        session_id=session.session_id,
                        quiz_type='post_quiz',
                        question_id=str(question.id),
                        question_text=question.question_text,
                        question_type=question.question_type,
                        response_value={'selected': 'Option 1' if is_correct else 'Option 2'},
                        response_text='Option 1' if is_correct else 'Option 2',
                        is_correct=is_correct,
                        time_spent_seconds=45 + q_num*10,
                        first_viewed_at=timezone.now() - timedelta(days=1+i, hours=-1, minutes=q_num*2+1),
                        submitted_at=timezone.now() - timedelta(days=1+i, hours=-1, minutes=q_num*2)
                    )

        self.stdout.write(self.style.SUCCESS('Successfully created 5 test users!'))
        
        # Print summary
        self.stdout.write('\n=== TEST DATA SUMMARY ===')
        self.stdout.write(f'Total Users: {User.objects.count()}')
        self.stdout.write(f'ChatGPT Group: {User.objects.filter(study_group="CHATGPT").count()}')
        self.stdout.write(f'PDF Group: {User.objects.filter(study_group="PDF").count()}')
        self.stdout.write(f'Completed Studies: {User.objects.filter(study_completed=True).count()}')
        self.stdout.write(f'Total Sessions: {StudySession.objects.count()}')
        self.stdout.write(f'Total Chat Interactions: {ChatInteraction.objects.count()}')
        self.stdout.write(f'Total PDF Interactions: {PDFInteraction.objects.count()}')
        self.stdout.write(f'Total Quiz Responses: {QuizResponse.objects.count()}')
        
        self.stdout.write('\n=== USER DETAILS ===')
        for user in User.objects.filter(username__startswith='testuser'):
            self.stdout.write(f'{user.username}: {user.study_group} group, completed: {user.study_completed}')
        
        self.stdout.write('\n✅ Ready to test dashboards!')
        self.stdout.write('Go to Admin Dashboard and check the "Debug Data" tab first.')