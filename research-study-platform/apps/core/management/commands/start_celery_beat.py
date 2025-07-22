from django.core.management.base import BaseCommand
import subprocess
import sys
import os


class Command(BaseCommand):
    help = 'Start Celery Beat scheduler'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loglevel',
            type=str,
            default='info',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            help='Log level for Celery Beat'
        )

    def handle(self, *args, **options):
        loglevel = options['loglevel']

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting Celery Beat scheduler with loglevel={loglevel}'
            )
        )

        cmd = [
            'celery',
            '-A', 'research_platform',
            'beat',
            f'--loglevel={loglevel}',
            '--scheduler=django_celery_beat.schedulers:DatabaseScheduler',
        ]

        try:
            subprocess.run(cmd, cwd=os.getcwd())
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Celery Beat stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting Celery Beat: {e}')
            )