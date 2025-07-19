from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from apps.core.models import User
from apps.studies.models import StudySession, StudyLog
from apps.research.models import ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction, PDFViewingBehavior, QuizResponse
from apps.chats.models import ChatSession, ChatInteraction as OldChatInteraction
from apps.pdfs.models import PDFSession, PDFInteraction
from apps.quizzes.models import Quiz, QuizAttempt, QuizResponse as OldQuizResponse, Question, Choice


class Command(BaseCommand):
    help = 'Populate the database with test data for dashboard analytics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--participants',
            type=int,
            default=50,
            help='Number of participants to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            User.objects.filter(is_staff=False).delete()
            StudySession.objects.all().delete()
            ParticipantProfile.objects.all().delete()
            InteractionLog.objects.all().delete()
            ChatInteraction.objects.all().delete()
            PDFViewingBehavior.objects.all().delete()
            QuizResponse.objects.all().delete()

        participants_count = options['participants']
        self.stdout.write(f'Creating {participants_count} test participants...')

        # Create or get research study
        study, created = ResearchStudy.objects.get_or_create(
            name='Linux Learning Study - Test Data',
            defaults={
                'description': 'Test study for dashboard analytics',
                'is_active': True,
                'created_by_id': 1  # Assuming admin user exists
            }
        )

        # Create test participants
        for i in range(participants_count):
            # Create user
            username = f'participant_{i+1:03d}'
            email = f'participant{i+1}@test.com'
            
            # Assign random group
            study_group = random.choice(['CHATGPT', 'PDF'])
            
            # Random completion status
            consent_completed = True
            pre_quiz_completed = random.choice([True, False]) if consent_completed else False
            interaction_completed = random.choice([True, False]) if pre_quiz_completed else False
            post_quiz_completed = random.choice([True, False]) if interaction_completed else False
            study_completed = post_quiz_completed and random.choice([True, False])

            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',
                study_group=study_group,
                consent_completed=consent_completed,
                pre_quiz_completed=pre_quiz_completed,
                interaction_completed=interaction_completed,
                post_quiz_completed=post_quiz_completed,
                study_completed=study_completed,
                participant_id=f'P{i+1:03d}',
                study_completed_at=timezone.now() - timedelta(days=random.randint(1, 30)) if study_completed else None
            )

            # Create participant profile
            participant = ParticipantProfile.objects.create(
                user=user,
                study=study,
                assigned_group=study_group,
                consent_given=consent_completed,
                created_at=timezone.now() - timedelta(days=random.randint(1, 45))
            )

            # Create study session
            session_duration = random.randint(1800, 7200)  # 30 mins to 2 hours
            interaction_duration = random.randint(900, 3600)  # 15 mins to 1 hour
            
            session = StudySession.objects.create(
                user=user,
                session_id=f'session_{username}',
                session_started_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                session_ended_at=timezone.now() - timedelta(days=random.randint(0, 29)) if study_completed else None,
                total_duration=session_duration,
                interaction_duration=interaction_duration,
                is_active=not study_completed
            )

            # Create interaction logs
            for j in range(random.randint(10, 50)):
                InteractionLog.objects.create(
                    participant=participant,
                    log_type=random.choice(['page_view', 'click', 'scroll', 'chat_message', 'quiz_answer']),
                    event_data={'action': f'test_action_{j}', 'value': random.randint(1, 100)},
                    timestamp=timezone.now() - timedelta(minutes=random.randint(1, 1440))
                )

            # Create group-specific data
            if study_group == 'CHATGPT':
                # Create chat data
                chat_session = ChatSession.objects.create(
                    session=session,
                    total_messages=random.randint(5, 25),
                    total_tokens_used=random.randint(500, 5000),
                    total_cost=random.uniform(0.01, 0.50),
                    session_started_at=session.session_started_at,
                    session_ended_at=session.session_ended_at
                )

                # Create chat interactions
                for k in range(random.randint(5, 20)):
                    ChatInteraction.objects.create(
                        participant=participant,
                        message_type=random.choice(['user', 'assistant']),
                        user_message='Test user message' if k % 2 == 0 else '',
                        assistant_response='Test assistant response' if k % 2 == 1 else '',
                        response_time_ms=random.randint(500, 3000),
                        token_count=random.randint(10, 200),
                        cost_usd=random.uniform(0.001, 0.05),
                        message_timestamp=timezone.now() - timedelta(minutes=random.randint(1, 120)),
                        conversation_turn=k + 1
                    )

            else:  # PDF group
                # Create PDF data
                pdf_session = PDFSession.objects.create(
                    session=session,
                    unique_pages_visited=random.randint(5, 20),
                    total_time_spent=random.randint(1200, 3600),
                    session_started_at=session.session_started_at,
                    session_ended_at=session.session_ended_at
                )

                # Create PDF interactions
                for k in range(random.randint(10, 30)):
                    PDFViewingBehavior.objects.create(
                        participant=participant,
                        pdf_name='linux-commands-reference.pdf',
                        page_number=random.randint(1, 25),
                        time_spent_seconds=random.randint(30, 300),
                        timestamp=timezone.now() - timedelta(minutes=random.randint(1, 120))
                    )

            # Create quiz data if applicable
            if pre_quiz_completed or post_quiz_completed:
                # Create quiz and questions if they don't exist
                if not Quiz.objects.filter(quiz_type='pre').exists():
                    pre_quiz = Quiz.objects.create(
                        title='Pre-Assessment Quiz',
                        quiz_type='pre',
                        description='Test your initial knowledge'
                    )
                    
                    for q in range(5):
                        question = Question.objects.create(
                            quiz=pre_quiz,
                            question_text=f'Test question {q+1} about Linux commands',
                            question_type='multiple_choice',
                            order=q+1
                        )
                        
                        for c in range(4):
                            Choice.objects.create(
                                question=question,
                                choice_text=f'Option {c+1}',
                                is_correct=(c == 0)  # First option is correct
                            )

                if not Quiz.objects.filter(quiz_type='post').exists():
                    post_quiz = Quiz.objects.create(
                        title='Post-Assessment Quiz',
                        quiz_type='post',
                        description='Test your learned knowledge'
                    )
                    
                    for q in range(5):
                        question = Question.objects.create(
                            quiz=post_quiz,
                            question_text=f'Post-test question {q+1} about Linux commands',
                            question_type='multiple_choice',
                            order=q+1
                        )
                        
                        for c in range(4):
                            Choice.objects.create(
                                question=question,
                                choice_text=f'Option {c+1}',
                                is_correct=(c == 0)
                            )

                # Create quiz attempts
                if pre_quiz_completed:
                    pre_quiz = Quiz.objects.get(quiz_type='pre')
                    pre_score = random.randint(30, 70)
                    attempt = QuizAttempt.objects.create(
                        user=user,
                        quiz=pre_quiz,
                        session=session,
                        score=pre_score,
                        percentage_score=pre_score,
                        is_completed=True,
                        started_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                        completed_at=timezone.now() - timedelta(days=random.randint(1, 29))
                    )

                    # Create quiz responses
                    for question in pre_quiz.questions.all():
                        is_correct = random.choice([True, False])
                        QuizResponse.objects.create(
                            participant=participant,
                            quiz_type='pre',
                            question_text=question.question_text,
                            selected_answer='Option 1' if is_correct else 'Option 2',
                            correct_answer='Option 1',
                            is_correct=is_correct,
                            time_spent_seconds=random.randint(30, 180),
                            answered_at=timezone.now() - timedelta(days=random.randint(1, 29))
                        )

                if post_quiz_completed:
                    post_quiz = Quiz.objects.get(quiz_type='post')
                    # Post quiz scores should generally be higher
                    post_score = random.randint(60, 95)
                    attempt = QuizAttempt.objects.create(
                        user=user,
                        quiz=post_quiz,
                        session=session,
                        score=post_score,
                        percentage_score=post_score,
                        is_completed=True,
                        started_at=timezone.now() - timedelta(days=random.randint(1, 15)),
                        completed_at=timezone.now() - timedelta(days=random.randint(1, 14))
                    )

                    # Create quiz responses
                    for question in post_quiz.questions.all():
                        is_correct = random.choice([True, True, True, False])  # Higher chance of correct
                        QuizResponse.objects.create(
                            participant=participant,
                            quiz_type='post',
                            question_text=question.question_text,
                            selected_answer='Option 1' if is_correct else 'Option 2',
                            correct_answer='Option 1',
                            is_correct=is_correct,
                            time_spent_seconds=random.randint(30, 180),
                            answered_at=timezone.now() - timedelta(days=random.randint(1, 14))
                        )

            if (i + 1) % 10 == 0:
                self.stdout.write(f'Created {i + 1} participants...')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {participants_count} test participants with realistic data!'
            )
        )
        
        # Print summary
        self.stdout.write('\n=== DATA SUMMARY ===')
        self.stdout.write(f'Total Users: {User.objects.count()}')
        self.stdout.write(f'ChatGPT Group: {User.objects.filter(study_group="CHATGPT").count()}')
        self.stdout.write(f'PDF Group: {User.objects.filter(study_group="PDF").count()}')
        self.stdout.write(f'Completed Studies: {User.objects.filter(study_completed=True).count()}')
        self.stdout.write(f'Total Sessions: {StudySession.objects.count()}')
        self.stdout.write(f'Total Chat Interactions: {ChatInteraction.objects.count()}')
        self.stdout.write(f'Total PDF Interactions: {PDFViewingBehavior.objects.count()}')
        self.stdout.write(f'Total Quiz Responses: {QuizResponse.objects.count()}')