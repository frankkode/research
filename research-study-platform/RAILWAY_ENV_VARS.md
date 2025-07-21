# Railway Environment Variables Configuration

## Required Environment Variables for Production

Set these in your Railway dashboard under **Variables**:

### Core Django Settings
```
DJANGO_SETTINGS_MODULE=research_platform.settings_production
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### Database
```
DATABASE_URL=postgresql://user:password@host:port/database
```
*Note: Railway automatically provides this for PostgreSQL*

### CORS Configuration
```
CORS_ALLOWED_ORIGINS=https://gtpresearch.up.railway.app,https://research-production-46af.up.railway.app
```

### Google OAuth (REQUIRED for auth to work)
```
GOOGLE_OAUTH2_CLIENT_ID=875588092118-0d4ok5qjudm1uh0nd68mf5s54ofvdf4r.apps.googleusercontent.com
```

### Optional (with defaults)
```
OPENAI_API_KEY=your-openai-key (if using AI features)
REDIS_URL=redis://localhost:6379 (if using Redis)
SECURE_SSL_REDIRECT=True
```

## Quick Setup Commands for Railway CLI

```bash
# Core settings
railway env set DJANGO_SETTINGS_MODULE=research_platform.settings_production
railway env set SECRET_KEY=l=kih3f%ez1^9xaw79a&%&1*4c
railway env set DEBUG=False

# CORS
railway env set CORS_ALLOWED_ORIGINS=https://gtpresearch.up.railway.app,https://research-production-46af.up.railway.app

# Google OAuth (CRITICAL)
railway env set GOOGLE_OAUTH2_CLIENT_ID=875588092118-0d4ok5qjudm1uh0nd68mf5s54ofvdf4r.apps.googleusercontent.com
```

## Troubleshooting

- **Google Auth 400 Error**: Missing `GOOGLE_OAUTH2_CLIENT_ID`
- **CORS Errors**: Check `CORS_ALLOWED_ORIGINS` 
- **500 Errors**: Check `DJANGO_SETTINGS_MODULE` and `SECRET_KEY`

Check Railway logs: `railway logs`