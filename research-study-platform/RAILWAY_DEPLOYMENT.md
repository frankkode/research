# Railway Deployment Guide

This guide covers deploying the Research Study Platform to Railway.app, a modern deployment platform.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository with your code
- OpenAI API key

## Quick Deployment Steps

### 1. Prepare Your Repository

Ensure your code is pushed to GitHub with all the latest changes:

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Deploy Backend to Railway

1. **Go to Railway.app and sign in**
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your repository**
5. **Railway will auto-detect it's a Django project**

### 3. Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```env
# Required Variables
SECRET_KEY=your-very-secure-secret-key-here-generate-a-new-one
DEBUG=False
OPENAI_API_KEY=your-openai-api-key-here

# Railway will automatically provide DATABASE_URL, but you can also add:
ALLOWED_HOSTS=your-railway-domain.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

# Optional Variables
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7
DJANGO_SETTINGS_MODULE=research_platform.settings_production
```

### 4. Add PostgreSQL Database

1. **In Railway dashboard, click "New Service"**
2. **Select "Database" → "PostgreSQL"**
3. **Railway automatically connects it to your app via DATABASE_URL**

### 5. Deploy Frontend

For the frontend, you have several options:

#### Option A: Deploy to Vercel (Recommended)
1. Go to vercel.com
2. Import your GitHub repository
3. Set build settings:
   - Framework Preset: Create React App
   - Root Directory: frontend
   - Build Command: `npm run build`
   - Output Directory: build

#### Option B: Deploy to Netlify
1. Go to netlify.com
2. Connect your GitHub repository
3. Set build settings:
   - Base directory: frontend
   - Build command: `npm run build`
   - Publish directory: frontend/build

#### Option C: Deploy frontend to Railway
1. Create new Railway service
2. Connect same GitHub repo
3. Set start command to serve the built frontend

### 6. Configure Frontend Environment Variables

Add these to your frontend deployment platform:

```env
REACT_APP_API_BASE_URL=https://your-backend-railway-domain.railway.app
NODE_ENV=production
GENERATE_SOURCEMAP=false
```

## Detailed Configuration

### Backend Railway Configuration

Create a `railway.toml` file in your repository root:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn research_platform.wsgi:application"
healthcheckPath = "/admin/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Django Settings for Railway

The settings are already configured to work with Railway's DATABASE_URL. Make sure you're using the production settings:

```env
DJANGO_SETTINGS_MODULE=research_platform.settings_production
```

### Database Migrations

Railway will automatically run migrations on deployment, but you can also run them manually:

1. Go to Railway dashboard
2. Click on your project
3. Go to "Deployments" tab
4. Click "View Logs" to see if migrations ran successfully

### Static Files

Railway handles static files automatically with WhiteNoise. Your `settings_production.py` is already configured for this.

## Environment Variables Reference

### Required Variables
- `SECRET_KEY` - Django secret key (generate a new one)
- `DEBUG` - Set to `False` for production
- `OPENAI_API_KEY` - Your OpenAI API key

### Automatically Provided by Railway
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Application port
- `RAILWAY_ENVIRONMENT` - Current environment

### Optional Variables
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins
- `DJANGO_SETTINGS_MODULE` - Django settings module to use
- `OPENAI_MODEL` - OpenAI model to use (default: gpt-4)
- `REDIS_URL` - Redis connection string (if using Redis)

## Domain Configuration

### Custom Domain for Backend
1. In Railway dashboard, go to Settings
2. Click "Generate Domain" or add custom domain
3. Update `ALLOWED_HOSTS` environment variable

### Custom Domain for Frontend
Follow your frontend deployment platform's documentation:
- **Vercel**: Project Settings → Domains
- **Netlify**: Site Settings → Domain Management

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check build logs in Railway dashboard
   - Ensure `requirements.txt` includes all dependencies
   - Verify Python version compatibility

2. **Database Connection Issues**
   - Ensure PostgreSQL service is running
   - Check if `DATABASE_URL` is set correctly
   - Verify database migrations ran successfully

3. **Static Files Not Loading**
   - Ensure `collectstatic` runs during deployment
   - Check `STATIC_ROOT` and `STATIC_URL` settings
   - Verify WhiteNoise is configured correctly

4. **CORS Issues**
   - Update `CORS_ALLOWED_ORIGINS` with frontend URL
   - Ensure frontend is making requests to correct backend URL

5. **OpenAI API Issues**
   - Verify `OPENAI_API_KEY` is set correctly
   - Check API key has sufficient credits
   - Monitor rate limiting

### Debugging

**View Logs:**
1. Railway Dashboard → Project → Deployments
2. Click on latest deployment
3. View logs for errors

**Database Access:**
1. Railway Dashboard → PostgreSQL service
2. Click "Connect" → "psql" for database access

**Environment Variables:**
1. Railway Dashboard → Project → Variables
2. Verify all required variables are set

## Monitoring and Maintenance

### Health Monitoring
Railway provides built-in monitoring:
- CPU usage
- Memory usage
- Request metrics
- Error rates

### Backup Strategy
Railway automatically backs up PostgreSQL databases, but consider:
1. Exporting data regularly
2. Storing backups externally
3. Testing restoration procedures

### Updates
To update your application:
1. Push changes to GitHub
2. Railway automatically deploys new commits
3. Monitor deployment logs for issues

## Production Checklist

- [ ] `SECRET_KEY` is unique and secure
- [ ] `DEBUG=False`
- [ ] PostgreSQL database is connected
- [ ] `OPENAI_API_KEY` is set
- [ ] `ALLOWED_HOSTS` includes Railway domain
- [ ] `CORS_ALLOWED_ORIGINS` includes frontend domain
- [ ] SSL is enabled (automatic with Railway)
- [ ] Database migrations ran successfully
- [ ] Static files are served correctly
- [ ] Frontend can communicate with backend
- [ ] Test all major functionality

## Cost Optimization

### Railway Pricing
- Starter Plan: $5/month
- Database: $5/month for PostgreSQL
- Usage-based pricing for additional resources

### Tips to Reduce Costs
1. Monitor resource usage
2. Optimize database queries
3. Use efficient API calls to OpenAI
4. Implement caching where appropriate
5. Consider scaling down during low-usage periods

## Support

- Railway Documentation: https://docs.railway.app
- Railway Community: https://railway.app/help
- Django Deployment Guide: https://docs.djangoproject.com/en/stable/howto/deployment/

For project-specific issues, check the application logs and ensure all environment variables are correctly configured.