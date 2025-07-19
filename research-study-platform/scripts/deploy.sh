#!/bin/bash

# Research Study Platform Production Deployment Script
# This script deploys the application to a production environment

set -e

echo "🚀 Deploying Research Study Platform to Production..."

# Check if required environment variables are set
if [ -z "$SECRET_KEY" ] || [ -z "$DB_PASSWORD" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Required environment variables are not set."
    echo "Please set: SECRET_KEY, DB_PASSWORD, OPENAI_API_KEY"
    exit 1
fi

# Create production environment file
echo "📄 Creating production environment file..."
cat > .env.production << EOF
DEBUG=False
SECRET_KEY=$SECRET_KEY
DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS
DB_ENGINE=django.db.backends.postgresql
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
REDIS_URL=$REDIS_URL
OPENAI_API_KEY=$OPENAI_API_KEY
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
LOG_LEVEL=INFO
CELERY_BROKER_URL=$REDIS_URL
CELERY_RESULT_BACKEND=$REDIS_URL
REACT_APP_API_URL=$REACT_APP_API_URL
REACT_APP_ENVIRONMENT=production
EOF

# Build production containers
echo "🐳 Building production containers..."
docker-compose build --no-cache

# Create necessary directories
echo "📁 Creating production directories..."
mkdir -p /var/www/static
mkdir -p /var/www/media
mkdir -p /var/log/research-platform

# Deploy with Docker Compose
echo "🎯 Deploying services..."
docker-compose --env-file .env.production up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 60

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec backend python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec backend python manage.py collectstatic --noinput

# Create superuser if needed
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Creating superuser..."
    docker-compose exec backend python manage.py createsuperuser --noinput \
        --email=$SUPERUSER_EMAIL \
        --username=$SUPERUSER_USERNAME
fi

# Run health checks
echo "🏥 Running health checks..."
sleep 30

# Check backend health
if curl -f http://localhost:8000/admin/ > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Check frontend health
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

# Check nginx health
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx is healthy"
else
    echo "❌ Nginx health check failed"
    exit 1
fi

echo "✅ Production deployment complete!"
echo ""
echo "🌐 Access points:"
echo "  - Application: http://localhost"
echo "  - Admin Panel: http://localhost/admin"
echo "  - API: http://localhost/api/"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Backup database: docker-compose exec db pg_dump -U postgres research_platform > backup.sql"
echo ""
echo "📊 Monitor the application:"
echo "  - docker-compose ps"
echo "  - docker-compose logs -f [service_name]"