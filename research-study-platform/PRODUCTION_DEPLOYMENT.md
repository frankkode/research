# Production Deployment Guide

This guide covers deploying the Research Study Platform to a production environment.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ (recommended) or SQLite for small deployments
- Redis 6+ (for caching and Celery)
- Nginx (recommended web server)
- SSL certificate (Let's Encrypt recommended)

## Quick Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd research-study-platform
   ```

2. **Run the deployment script**
   ```bash
   ./deploy.sh
   ```

3. **Configure environment variables**
   ```bash
   cp backend/.env.template backend/.env
   cp frontend/.env.template frontend/.env
   # Edit both .env files with your production values
   ```

## Detailed Deployment Steps

### 1. Server Setup

**Update system packages:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Install required packages:**
```bash
sudo apt install python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib redis-server nginx certbot python3-certbot-nginx -y
```

### 2. Database Setup (PostgreSQL)

**Create database and user:**
```bash
sudo -u postgres psql
CREATE DATABASE research_study_db;
CREATE USER research_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE research_study_db TO research_user;
ALTER USER research_user CREATEDB;
\q
```

### 3. Application Setup

**Create application directory:**
```bash
sudo mkdir -p /var/www/research-study-platform
sudo chown $USER:$USER /var/www/research-study-platform
cd /var/www/research-study-platform
```

**Clone and setup:**
```bash
git clone <repository-url> .
./deploy.sh
```

### 4. Environment Configuration

**Backend (.env):**
```env
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=research_study_db
DB_USER=research_user
DB_PASSWORD=secure-password
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

**Frontend (.env):**
```env
NODE_ENV=production
REACT_APP_API_BASE_URL=https://api.your-domain.com
GENERATE_SOURCEMAP=false
REACT_APP_ENABLE_DEBUG_MODE=false
```

### 5. Web Server Configuration (Nginx)

**Create Nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/research-study-platform
```

```nginx
# Frontend (React app)
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    root /var/www/research-study-platform/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /static/ {
        alias /var/www/research-study-platform/frontend/build/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Backend API
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/research-study-platform/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/research-study-platform/backend/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/research-study-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Configuration

**Obtain SSL certificates:**
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com -d api.your-domain.com
```

### 7. Application Services

**Create Gunicorn service:**
```bash
sudo nano /etc/systemd/system/research-study-platform.service
```

```ini
[Unit]
Description=Research Study Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/research-study-platform/backend
Environment="PATH=/var/www/research-study-platform/backend/venv/bin"
ExecStart=/var/www/research-study-platform/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 research_platform.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

**Create Celery service (if using background tasks):**
```bash
sudo nano /etc/systemd/system/research-study-celery.service
```

```ini
[Unit]
Description=Research Study Celery
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/research-study-platform/backend
Environment="PATH=/var/www/research-study-platform/backend/venv/bin"
ExecStart=/var/www/research-study-platform/backend/venv/bin/celery -A research_platform worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable research-study-platform
sudo systemctl enable research-study-celery
sudo systemctl start research-study-platform
sudo systemctl start research-study-celery
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 8. Security Hardening

**Firewall configuration:**
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

**Set proper file permissions:**
```bash
sudo chown -R www-data:www-data /var/www/research-study-platform
sudo chmod -R 755 /var/www/research-study-platform
sudo chmod -R 644 /var/www/research-study-platform/backend/media
```

### 9. Monitoring and Logging

**Log files locations:**
- Application logs: `/var/www/research-study-platform/backend/logs/`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`

**Monitor services:**
```bash
# Check application status
sudo systemctl status research-study-platform
sudo systemctl status research-study-celery

# View logs
sudo journalctl -u research-study-platform -f
tail -f /var/www/research-study-platform/backend/logs/django.log
```

### 10. Backup Strategy

**Database backup:**
```bash
# Create backup script
sudo nano /etc/cron.daily/backup-research-db
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/research-study"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump research_study_db > $BACKUP_DIR/db_backup_$DATE.sql
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
```

```bash
sudo chmod +x /etc/cron.daily/backup-research-db
```

**Media files backup:**
```bash
# Backup media files
rsync -av /var/www/research-study-platform/backend/media/ /var/backups/research-study/media/
```

### 11. Updates and Maintenance

**Update application:**
```bash
cd /var/www/research-study-platform
git pull origin main
./deploy.sh
sudo systemctl restart research-study-platform
sudo systemctl restart research-study-celery
```

**Update dependencies:**
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Frontend
cd ../frontend
npm update
npm run build
```

## Production Configuration Checklist

- [ ] SECRET_KEY is unique and secure
- [ ] DEBUG=False
- [ ] Database is PostgreSQL (not SQLite)
- [ ] SSL certificates are configured
- [ ] ALLOWED_HOSTS is properly configured
- [ ] CORS_ALLOWED_ORIGINS is restrictive
- [ ] Environment variables are set
- [ ] File permissions are correct
- [ ] Firewall is configured
- [ ] Backup strategy is implemented
- [ ] Monitoring is set up
- [ ] Log rotation is configured

## Troubleshooting

**Common issues:**

1. **Permission denied errors:**
   ```bash
   sudo chown -R www-data:www-data /var/www/research-study-platform
   ```

2. **Database connection errors:**
   - Check PostgreSQL is running: `sudo systemctl status postgresql`
   - Verify database credentials in .env

3. **Static files not loading:**
   ```bash
   cd backend
   python manage.py collectstatic --noinput
   ```

4. **SSL certificate issues:**
   ```bash
   sudo certbot renew --dry-run
   ```

## Performance Optimization

1. **Enable Gzip compression in Nginx**
2. **Configure Redis caching**
3. **Set up CDN for static files**
4. **Monitor resource usage**
5. **Optimize database queries**

## Security Best Practices

1. **Regular security updates**
2. **Monitor access logs**
3. **Use strong passwords**
4. **Limit database access**
5. **Regular backups**
6. **Monitor for suspicious activity**

For additional support, refer to the main documentation or contact the development team.