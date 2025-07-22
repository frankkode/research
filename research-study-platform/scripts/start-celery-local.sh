#!/bin/bash
# Local Celery worker startup script

echo "🚀 Starting Celery worker for local development..."

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

# Test Django settings first
echo "🔧 Testing Django configuration..."
python3 -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()
print('✅ Django setup successful')
"

# Start Celery worker using python3 module
echo "🔄 Starting Celery worker..."
python3 -m celery -A research_platform worker --loglevel=info --concurrency=2

echo "🛑 Celery worker stopped"