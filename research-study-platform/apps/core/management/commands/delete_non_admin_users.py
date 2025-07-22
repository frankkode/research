from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.quizzes.models import QuizResponse, QuizAttempt
from apps.chats.models import ChatSession, ChatMessage
from apps.studies.models import StudySession
from apps.research.models import ResearchData
from django.contrib.admin.models import LogEntry

User = get_user_model()

class Command(BaseCommand):
    help = 'Delete all users and their activities except admin users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion (required for actual deletion)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        confirm = options['confirm']
        
        if not dry_run and not confirm:
            self.stdout.write(
                self.style.ERROR(
                    'This command will permanently delete user data. '
                    'Use --dry-run to see what would be deleted, '
                    'or --confirm to actually delete.'
                )
            )
            return
        
        # Get non-admin users (admin users have is_staff=True or is_superuser=True)
        non_admin_users = User.objects.filter(
            is_staff=False,
            is_superuser=False
        )
        
        user_count = non_admin_users.count()
        
        if user_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No non-admin users found to delete.')
            )
            return
        
        # Get user IDs for related data deletion
        user_ids = list(non_admin_users.values_list('id', flat=True))
        
        # Count related objects
        quiz_responses = QuizResponse.objects.filter(user_id__in=user_ids)
        quiz_attempts = QuizAttempt.objects.filter(user_id__in=user_ids)
        chat_sessions = ChatSession.objects.filter(user_id__in=user_ids)
        chat_messages = ChatMessage.objects.filter(session__user_id__in=user_ids)
        study_sessions = StudySession.objects.filter(user_id__in=user_ids)
        
        # Count research data if it exists
        try:
            research_data = ResearchData.objects.filter(user_id__in=user_ids)
            research_count = research_data.count()
        except:
            research_count = 0
        
        # Display what will be deleted
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.WARNING('DELETION SUMMARY'))
        self.stdout.write('='*50)
        self.stdout.write(f'Users to delete: {user_count}')
        self.stdout.write(f'Quiz responses: {quiz_responses.count()}')
        self.stdout.write(f'Quiz attempts: {quiz_attempts.count()}')
        self.stdout.write(f'Chat sessions: {chat_sessions.count()}')
        self.stdout.write(f'Chat messages: {chat_messages.count()}')
        self.stdout.write(f'Study sessions: {study_sessions.count()}')
        if research_count > 0:
            self.stdout.write(f'Research data: {research_count}')
        self.stdout.write('='*50)
        
        # Show some example users
        self.stdout.write('\nUsers to be deleted:')
        for user in non_admin_users[:10]:  # Show first 10
            self.stdout.write(f'  - {user.email} ({user.participant_id})')
        if user_count > 10:
            self.stdout.write(f'  ... and {user_count - 10} more users')
        
        # Show admin users that will be preserved
        from django.db import models
        admin_users = User.objects.filter(
            models.Q(is_staff=True) | models.Q(is_superuser=True)
        )
        self.stdout.write(f'\nAdmin users to be PRESERVED ({admin_users.count()}):')
        for user in admin_users:
            self.stdout.write(f'  - {user.email} (admin)')
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS('\n✓ DRY RUN - No data was deleted')
            )
            return
        
        # Confirm deletion
        self.stdout.write(
            self.style.ERROR(
                f'\n⚠️  This will permanently delete {user_count} users and all their data!'
            )
        )
        
        # Perform deletion
        try:
            with transaction.atomic():
                # Delete related data first (Django will handle cascading)
                deleted_counts = {}
                
                # Delete quiz data
                deleted_counts['quiz_responses'] = quiz_responses.count()
                quiz_responses.delete()
                
                deleted_counts['quiz_attempts'] = quiz_attempts.count()
                quiz_attempts.delete()
                
                # Delete chat data
                deleted_counts['chat_messages'] = chat_messages.count()
                chat_messages.delete()
                
                deleted_counts['chat_sessions'] = chat_sessions.count()
                chat_sessions.delete()
                
                # Delete study sessions
                deleted_counts['study_sessions'] = study_sessions.count()
                study_sessions.delete()
                
                # Delete research data if it exists
                if research_count > 0:
                    deleted_counts['research_data'] = research_count
                    research_data.delete()
                
                # Delete log entries for these users
                LogEntry.objects.filter(user_id__in=user_ids).delete()
                
                # Finally, delete the users
                deleted_users = non_admin_users.count()
                non_admin_users.delete()
                
                self.stdout.write('\n' + '='*50)
                self.stdout.write(self.style.SUCCESS('✅ DELETION COMPLETED'))
                self.stdout.write('='*50)
                self.stdout.write(f'Deleted users: {deleted_users}')
                for key, count in deleted_counts.items():
                    if count > 0:
                        self.stdout.write(f'Deleted {key}: {count}')
                self.stdout.write('='*50)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during deletion: {str(e)}')
            )
            raise