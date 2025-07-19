# Docker Deployment Guide

This guide provides comprehensive instructions for deploying the Research Study Platform using Docker.

## 🐳 Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** (for cloning the repository)

## 📦 Quick Start with Docker

### Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd research-study-platform
   ```

2. **Run the automated setup script**
   ```bash
   ./scripts/setup.sh
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

### Manual Setup

If you prefer manual setup:

1. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Build and start services**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d --build
   ```

3. **Run database migrations**
   ```bash
   docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
   ```

## 🏭 Production Deployment

### Option 1: Automated Production Deployment

1. **Set required environment variables**
   ```bash
   export SECRET_KEY="your-production-secret-key"
   export DB_PASSWORD="your-db-password"
   export OPENAI_API_KEY="your-openai-api-key"
   export ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
   export DB_NAME="research_platform"
   export DB_USER="postgres"
   export DB_HOST="db"
   export DB_PORT="5432"
   export REDIS_URL="redis://redis:6379/0"
   export REACT_APP_API_URL="https://yourdomain.com"
   ```

2. **Run deployment script**
   ```bash
   ./scripts/deploy.sh
   ```

### Option 2: Manual Production Deployment

1. **Create production environment file**
   ```bash
   cp .env.example .env.production
   # Configure with production values
   ```

2. **Build and deploy**
   ```bash
   docker-compose --env-file .env.production up -d --build
   ```

3. **Run migrations and collect static files**
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py collectstatic --noinput
   ```

## 🔧 Docker Services

### Service Architecture

The application consists of the following services:

| Service | Description | Port | Dependencies |
|---------|-------------|------|--------------|
| **backend** | Django API server | 8000 | db, redis |
| **frontend** | React application | 3000 | backend |
| **db** | PostgreSQL database | 5432 | None |
| **redis** | Redis cache/broker | 6379 | None |
| **celery** | Background task worker | - | db, redis |
| **celery-beat** | Task scheduler | - | db, redis |
| **nginx** | Reverse proxy | 80, 443 | backend, frontend |

### Health Checks

All services include health checks:
- **Database**: `pg_isready` command
- **Redis**: `redis-cli ping` command
- **Backend**: HTTP request to `/admin/`
- **Frontend**: HTTP request to root path
- **Nginx**: HTTP request to `/health`

## 🌐 Configuration

### Environment Variables

#### Essential Variables

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,yourdomain.com

# Database
DB_NAME=research_platform
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=your-openai-api-key
```

#### Security Variables (Production)

```env
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Volume Management

#### Development Volumes
- `./backend:/app` - Live code reloading
- `./frontend:/app` - Live code reloading
- `postgres_data:/var/lib/postgresql/data` - Database persistence

#### Production Volumes
- `static_files:/var/www/static` - Static file serving
- `media_files:/var/www/media` - User uploaded files
- `postgres_data:/var/lib/postgresql/data` - Database persistence

## 📊 Monitoring and Logging

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Service Status

```bash
# Check running services
docker-compose ps

# Check resource usage
docker stats

# Check service health
docker-compose exec backend python manage.py check
```

### Database Operations

```bash
# Access database shell
docker-compose exec db psql -U postgres -d research_platform

# Create database backup
docker-compose exec db pg_dump -U postgres research_platform > backup.sql

# Restore from backup
docker-compose exec -T db psql -U postgres -d research_platform < backup.sql
```

## 🔄 Development Workflow

### Common Commands

```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# Stop services
docker-compose -f docker-compose.dev.yml down

# Restart a service
docker-compose -f docker-compose.dev.yml restart backend

# View real-time logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Execute commands in containers
docker-compose -f docker-compose.dev.yml exec backend python manage.py shell
docker-compose -f docker-compose.dev.yml exec frontend npm test

# Rebuild containers
docker-compose -f docker-compose.dev.yml build --no-cache
```

### Running Tests

```bash
# Backend tests
docker-compose -f docker-compose.dev.yml exec backend python manage.py test

# Frontend tests
docker-compose -f docker-compose.dev.yml exec frontend npm test -- --watchAll=false

# Tests with coverage
docker-compose -f docker-compose.dev.yml exec backend coverage run --source='.' manage.py test
docker-compose -f docker-compose.dev.yml exec backend coverage report
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or use different ports in docker-compose.yml
```

#### 2. Database Connection Issues

```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Reset database
docker-compose down -v
docker-compose up -d
```

#### 3. Permission Issues

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker permission (Linux)
sudo usermod -aG docker $USER
```

#### 4. Container Build Issues

```bash
# Clean build
docker-compose down
docker system prune -a
docker-compose build --no-cache
```

#### 5. Static Files Not Loading

```bash
# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Check nginx configuration
docker-compose exec nginx nginx -t
```

### Service-Specific Issues

#### Backend Issues

```bash
# Check Django configuration
docker-compose exec backend python manage.py check

# Check database migrations
docker-compose exec backend python manage.py showmigrations

# Run migrations
docker-compose exec backend python manage.py migrate
```

#### Frontend Issues

```bash
# Clear npm cache
docker-compose exec frontend npm cache clean --force

# Reinstall dependencies
docker-compose exec frontend rm -rf node_modules package-lock.json
docker-compose exec frontend npm install
```

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  backend:
    scale: 3
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=False
```

### Load Balancing

```yaml
# Add to docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/load-balancer.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

## 🔒 Security Best Practices

### Production Security

1. **Use secrets management**
   ```bash
   # Docker secrets
   docker secret create db_password db_password.txt
   ```

2. **Enable HTTPS**
   ```yaml
   # Add SSL certificates to nginx
   volumes:
     - ./certs:/etc/nginx/certs
   ```

3. **Regular updates**
   ```bash
   # Update base images
   docker-compose pull
   docker-compose up -d --build
   ```

### Network Security

```yaml
# docker-compose.yml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

## 🎯 Performance Optimization

### Resource Limits

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Caching

```yaml
# Add Redis caching
services:
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## 📋 Maintenance

### Regular Tasks

```bash
# Weekly maintenance script
#!/bin/bash
docker-compose exec backend python manage.py clearsessions
docker-compose exec db vacuumdb -U postgres research_platform
docker system prune -f
```

### Backup Strategy

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U postgres research_platform > "backup_$DATE.sql"
```

---

For additional help or questions, please refer to the main SETUP_GUIDE.md or contact the development team.