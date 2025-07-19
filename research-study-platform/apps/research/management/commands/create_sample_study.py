from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.research.models import ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction, PDFViewingBehavior, QuizResponse
from apps.core.models import User
import random
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a sample research study with test data'

    def add_arguments(self, parser):
        parser.add_argument('--participants', type=int, default=50, help='Number of participants to create')

    def handle(self, *args, **options):
        num_participants = options['participants']
        
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'study_group': 'ADMIN'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / admin123'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create research study
        study, created = ResearchStudy.objects.get_or_create(
            name='Evaluating ChatGPT vs. Static Materials for Learning Basic Linux Commands',
            defaults={
                'description': 'A short-term knowledge transfer study comparing ChatGPT and static PDF materials for learning Linux commands',
                'is_active': True,
                'max_participants': 100,
                'estimated_duration_minutes': 60,
                'requires_consent': True,
                'has_pre_quiz': True,
                'has_post_quiz': True,
                'auto_assign_groups': True,
                'group_balance_ratio': {'PDF': 0.5, 'CHATGPT': 0.5},
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created research study: {study.name}'))
        else:
            self.stdout.write(self.style.WARNING('Research study already exists'))

        # Create sample participants
        groups = ['PDF', 'CHATGPT']
        for i in range(1, num_participants + 1):
            # Create user
            username = f'participant_{i:03d}'
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'participant_id': f'P{i:03d}',
                    'study_group': random.choice(groups),
                    'consent_completed': random.choice([True, False]),
                    'pre_quiz_completed': random.choice([True, False]),
                    'interaction_completed': random.choice([True, False]),
                    'post_quiz_completed': random.choice([True, False]),
                    'study_completed': random.choice([True, False]),
                }
            )
            
            if user_created:
                user.set_password('password123')
                user.save()
                
                # Create participant profile
                profile, profile_created = ParticipantProfile.objects.get_or_create(
                    user=user,
                    study=study,
                    defaults={
                        'assigned_group': user.study_group,
                        'consent_given': user.consent_completed,
                        'age_range': random.choice(['18-24', '25-34', '35-44', '45-54', '55+']),
                        'education_level': random.choice(['High School', 'Bachelor', 'Master', 'PhD']),
                        'technical_background': random.choice(['Beginner', 'Intermediate', 'Advanced']),
                    }
                )
                
                if profile_created:
                    # Create sample interaction logs
                    base_time = timezone.now() - timedelta(days=random.randint(1, 30))
                    for j in range(random.randint(5, 20)):
                        InteractionLog.objects.create(
                            participant=profile,
                            session_id=f'session_{i}_{j}',
                            log_type=random.choice(['page_view', 'button_click', 'scroll', 'text_selection', 'chat_message', 'quiz_answer']),
                            event_data={'action': f'sample_action_{j}'},
                            timestamp=base_time + timedelta(minutes=j * 5)
                        )
                    
                    # Create sample chat interactions for ChatGPT group
                    if user.study_group == 'CHATGPT':
                        for j in range(random.randint(10, 25)):
                            ChatInteraction.objects.create(
                                participant=profile,
                                session_id=f'chat_session_{i}',
                                message_type=random.choice(['user_message', 'assistant_response']),
                                content=f'Sample message {j}',
                                content_hash=f'hash_{i}_{j}',
                                timestamp=base_time + timedelta(minutes=j * 2),
                                token_count=random.randint(50, 200),
                                cost_usd=random.uniform(0.01, 0.05)
                            )
                    
                    # Create sample PDF viewing behaviors for PDF group
                    if user.study_group == 'PDF':
                        for j in range(random.randint(5, 15)):
                            pdf_name = random.choice(['linux_basics.pdf', 'advanced_commands.pdf', 'file_system.pdf'])
                            page_number = random.randint(1, 20)
                            PDFViewingBehavior.objects.get_or_create(
                                participant=profile,
                                session_id=f'pdf_session_{i}',
                                pdf_name=pdf_name,
                                page_number=page_number,
                                defaults={
                                    'pdf_hash': f'pdf_hash_{j}',
                                    'time_spent_seconds': random.randint(30, 300),
                                    'first_viewed_at': base_time + timedelta(minutes=j * 3)
                                }
                            )
                    
                    # Create sample quiz responses
                    for quiz_type in ['pre_quiz', 'post_quiz']:
                        for q in range(random.randint(5, 10)):
                            QuizResponse.objects.create(
                                participant=profile,
                                session_id=f'quiz_session_{i}',
                                quiz_type=quiz_type,
                                question_id=f'q_{q}',
                                question_text=f'Sample question {q}',
                                question_type='multiple_choice',
                                response_value={'answer': f'option_{random.randint(1, 4)}'},
                                is_correct=random.choice([True, False]),
                                first_viewed_at=base_time + timedelta(minutes=q * 2),
                                time_spent_seconds=random.randint(10, 60)
                            )

        self.stdout.write(self.style.SUCCESS(f'Created {num_participants} sample participants with data'))
        self.stdout.write(self.style.SUCCESS('Sample research study setup complete!'))
        self.stdout.write(self.style.SUCCESS('You can now view real data in the analytics dashboard'))