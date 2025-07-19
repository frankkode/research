#!/bin/bash

# Research Study Platform - Production Deployment Script
# This script helps deploy the application to production

set -e  # Exit on any error

echo "🚀 Starting Research Study Platform deployment..."

# Check if we're in the right directory
if [ ! -f "deploy.sh" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Configuration
FRONTEND_DIR="frontend"
BACKEND_DIR="backend"
ENV_FILE="${BACKEND_DIR}/.env"

echo "📋 Pre-deployment checklist..."

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found in $BACKEND_DIR"
    echo "💡 Please copy .env.template to .env and configure it for production"
    exit 1
fi

# Check if DEBUG is set to False
if grep -q "DEBUG=True" "$ENV_FILE"; then
    echo "⚠️  Warning: DEBUG is set to True in .env file"
    echo "💡 For production, please set DEBUG=False"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if SECRET_KEY is changed from default
if grep -q "your-very-secure-secret-key-here" "$ENV_FILE"; then
    echo "❌ Error: SECRET_KEY is still set to default value"
    echo "💡 Please generate a secure SECRET_KEY for production"
    exit 1
fi

echo "✅ Pre-deployment checks passed"

echo "📦 Building frontend..."
cd "$FRONTEND_DIR"

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

# Build frontend for production
echo "🔨 Building frontend..."
npm run build

echo "✅ Frontend build completed"
cd ..

echo "📦 Preparing backend..."
cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📥 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one manually using: python manage.py createsuperuser')
else:
    print('Superuser already exists')
"

echo "✅ Backend preparation completed"

# Security checks
echo "🔒 Running security checks..."
python manage.py check --deploy

echo "✅ Security checks passed"

cd ..

echo "🎉 Deployment preparation completed successfully!"
echo ""
echo "📝 Next steps for production deployment:"
echo "1. Configure your web server (nginx, Apache, etc.)"
echo "2. Set up SSL certificates"
echo "3. Configure your database (PostgreSQL recommended)"
echo "4. Set up Redis for caching and Celery"
echo "5. Configure monitoring and logging"
echo "6. Set up backup procedures"
echo ""
echo "🔧 Production server commands:"
echo "Backend: cd backend && source venv/bin/activate && gunicorn research_platform.wsgi:application"
echo "Frontend: Serve the built files from frontend/build/"
echo ""
echo "📚 For detailed deployment instructions, see the documentation."

# Deactivate virtual environment
deactivate 2>/dev/null || true

echo "✨ Deployment script completed!"