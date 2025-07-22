#!/bin/bash
# Local Celery Beat (scheduler) startup script

echo "🚀 Starting Celery Beat for local development..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis first:"
    echo "   brew services start redis"
    exit 1
fi

echo "✅ Redis is running"

# Start Celery Beat (scheduler)
echo "🔄 Starting Celery Beat..."
celery -A research_platform beat --loglevel=info

echo "🛑 Celery Beat stopped"