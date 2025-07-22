from django.core.management.base import BaseCommand
import subprocess
import sys
import os


class Command(BaseCommand):
    help = 'Start Celery worker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--concurrency',
            type=int,
            default=2,
            help='Number of concurrent worker processes'
        )
        parser.add_argument(
            '--loglevel',
            type=str,
            default='info',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            help='Log level for Celery worker'
        )
        parser.add_argument(
            '--queues',
            type=str,
            default='celery,notifications',
            help='Comma-separated list of queues to process'
        )

    def handle(self, *args, **options):
        concurrency = options['concurrency']
        loglevel = options['loglevel']
        queues = options['queues']

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting Celery worker with concurrency={concurrency}, '
                f'loglevel={loglevel}, queues={queues}'
            )
        )

        cmd = [
            'celery',
            '-A', 'research_platform',
            'worker',
            f'--loglevel={loglevel}',
            f'--concurrency={concurrency}',
            f'--queues={queues}',
        ]

        try:
            subprocess.run(cmd, cwd=os.getcwd())
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Celery worker stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting Celery worker: {e}')
            )