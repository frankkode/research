from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.quizzes.tasks import schedule_transfer_quiz_notification
import time


class Command(BaseCommand):
    help = 'Test Celery task execution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test notification to'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='celery_test_user',
            defaults={
                'email': options['email'] or 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created test user: {user.username}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Testing Celery task with user: {user.email}')
        )
        
        # Schedule immediate notification
        try:
            result = schedule_transfer_quiz_notification.delay(
                user_id=user.id,
                scheduled_time=timezone.now().isoformat(),
                user_email=user.email
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Task scheduled successfully!')
            )
            self.stdout.write(f'Task ID: {result.id}')
            self.stdout.write(f'Task State: {result.state}')
            
            # Wait a moment and check status
            time.sleep(2)
            
            self.stdout.write(f'Task State after 2s: {result.state}')
            if result.ready():
                self.stdout.write(f'Task Result: {result.result}')
            else:
                self.stdout.write('Task is still processing...')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error scheduling task: {e}')
            )
            
        self.stdout.write(
            self.style.SUCCESS('Test completed. Check your email and Celery worker logs.')
        )