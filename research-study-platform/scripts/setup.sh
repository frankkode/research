#!/bin/bash

# Research Study Platform Setup Script
# This script sets up the development environment for the research study platform

set -e

echo "🚀 Setting up Research Study Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your configuration values"
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p media
mkdir -p static

# Generate Django secret key
echo "🔑 Generating Django secret key..."
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
sed -i.bak "s/SECRET_KEY=your-secret-key-here-change-in-production/SECRET_KEY=$SECRET_KEY/" .env

# Build and start services
echo "🐳 Building Docker containers..."
docker-compose -f docker-compose.dev.yml build

echo "🎯 Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

# Create superuser (optional)
echo "👤 Creating superuser..."
echo "You can create a superuser now or skip this step:"
read -p "Create superuser? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
docker-compose -f docker-compose.dev.yml exec frontend npm install

# Run tests
echo "🧪 Running tests..."
docker-compose -f docker-compose.dev.yml exec backend python manage.py test
docker-compose -f docker-compose.dev.yml exec frontend npm test -- --watchAll=false

echo "✅ Setup complete!"
echo ""
echo "🌐 Access points:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - Admin Panel: http://localhost:8000/admin"
echo "  - API Documentation: http://localhost:8000/api/"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  - Stop services: docker-compose -f docker-compose.dev.yml down"
echo "  - Restart services: docker-compose -f docker-compose.dev.yml restart"
echo "  - Run backend shell: docker-compose -f docker-compose.dev.yml exec backend python manage.py shell"
echo ""
echo "📖 For more information, see the SETUP_GUIDE.md file."