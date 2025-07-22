#!/bin/bash
# Simple Celery worker startup script (without django-celery-beat)

echo "🚀 Starting Celery worker (simple mode)..."

# Use the same Python that Django uses
PYTHON_PATH=$(which python3)
echo "✅ Using Python: $PYTHON_PATH"

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis first:"
    echo "   brew services start redis"
    exit 1
fi

echo "✅ Redis is running"

# Test imports
echo "🔧 Testing imports..."
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')

import django
django.setup()

from research_platform.celery import app
print('✅ Celery app import successful')

from apps.quizzes.tasks import schedule_transfer_quiz_notification
print('✅ Task import successful')
"

if [ $? -ne 0 ]; then
    echo "❌ Import test failed"
    exit 1
fi

echo "✅ All imports successful"

# Start Celery worker without Beat scheduler requirements
echo "🔄 Starting Celery worker..."
DJANGO_SETTINGS_MODULE=research_platform.settings python3 -m celery -A research_platform worker --loglevel=info --concurrency=2 --without-gossip --without-mingle --without-heartbeat

echo "🛑 Celery worker stopped"