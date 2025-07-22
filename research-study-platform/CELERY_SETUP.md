# Celery Setup Guide

## Local Development

### Prerequisites
1. **Redis Configuration**: You can use either:
   - **Local Redis**:
     ```bash
     brew services start redis
     # or
     redis-server
     ```
   - **Redis Cloud**: Update your `.env` file with your Redis Cloud credentials

2. **Test Redis Connection**:
   ```bash
   # Set your Redis password first
   export REDIS_PASSWORD=your-actual-redis-password
   python3 scripts/test-redis-connection.py
   ```

### Option 1: Using Scripts
```bash
# Terminal 1: Start Django
python manage.py runserver

# Terminal 2: Start Celery Worker
./scripts/start-celery-local.sh

# Terminal 3: Start Celery Beat (scheduler)
./scripts/start-celery-beat-local.sh
```

### Option 2: Using Management Commands
```bash
# Terminal 1: Start Django
python manage.py runserver

# Terminal 2: Start Celery Worker
python manage.py start_celery_worker --concurrency=2

# Terminal 3: Start Celery Beat
python manage.py start_celery_beat
```

### Option 3: Using Procfile (with honcho)
```bash
# Install honcho first
pip install honcho

# Start all services
honcho -f Procfile.dev start
```

## Testing Celery Tasks

### Test Transfer Quiz Notification Task
```python
# In Django shell
python manage.py shell

from apps.quizzes.tasks import schedule_transfer_quiz_notification
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
user = User.objects.first()

# Test the task
result = schedule_transfer_quiz_notification.delay(
    user_id=user.id,
    scheduled_time=timezone.now().isoformat(),
    user_email=user.email
)

print(f"Task ID: {result.id}")
print(f"Task Status: {result.status}")
```

### Monitor Task Status
```python
from celery import current_app

# Check task status
result = current_app.AsyncResult('task-id-here')
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

## Production Setup (Railway)

### 1. Add Redis Service
In Railway dashboard:
1. Add Redis addon to your project
2. Note the `REDIS_URL` environment variable

### 2. Configure Environment Variables
Copy from `.env.production.template` and set:
```env
REDIS_URL=redis://user:password@host:port
CELERY_BROKER_URL=$REDIS_URL/0
CELERY_RESULT_BACKEND=$REDIS_URL/1
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_MAX_TASKS_PER_CHILD=1000
CELERY_TASK_ALWAYS_EAGER=False
```

### 3. Deploy Separate Worker Service
Create a new Railway service for Celery worker:

1. **Create `worker.dockerfile`**:
```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD celery -A research_platform worker --loglevel=info --concurrency=4 --queues=celery,notifications
```

2. **Create `beat.dockerfile`**:
```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD celery -A research_platform beat --loglevel=info --scheduler=django_celery_beat.schedulers:DatabaseScheduler
```

### 4. Alternative: Single Service with Supervisor
Create `supervisord.conf`:
```ini
[supervisord]
nodaemon=true

[program:web]
command=gunicorn research_platform.wsgi:application --bind 0.0.0.0:$PORT
directory=/app
autostart=true
autorestart=true

[program:worker]
command=celery -A research_platform worker --loglevel=info --concurrency=4
directory=/app
autostart=true
autorestart=true

[program:beat]
command=celery -A research_platform beat --loglevel=info --scheduler=django_celery_beat.schedulers:DatabaseScheduler
directory=/app
autostart=true
autorestart=true
```

## Monitoring and Debugging

### Check Celery Worker Status
```bash
celery -A research_platform inspect active
celery -A research_platform inspect registered
celery -A research_platform inspect stats
```

### View Task History
```bash
celery -A research_platform events
```

### Redis Monitoring
```bash
redis-cli monitor
```

## Common Issues

1. **Connection refused**: Check if Redis is running
2. **Import errors**: Ensure DJANGO_SETTINGS_MODULE is set
3. **Task not executing**: Check worker is running and processing correct queue
4. **Email not sending**: Verify email settings in production

## Queues

- `celery`: Default queue for general tasks
- `notifications`: Queue for email notifications and alerts

Tasks are automatically routed based on `CELERY_TASK_ROUTES` in settings.py.