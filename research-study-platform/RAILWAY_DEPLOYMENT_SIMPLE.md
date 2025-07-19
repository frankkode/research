# Simple Railway Deployment Guide

This guide focuses on deploying to Railway **without** external services like AWS S3. Everything runs on Railway.

## What's Included

✅ **Backend**: Django app with PostgreSQL database  
✅ **Static Files**: Served by WhiteNoise (no S3 needed)  
✅ **Media Files**: Stored on Railway (no images used)  
✅ **Frontend**: Deploy separately on Vercel/Netlify  

## Step-by-Step Deployment

### 1. Sign Up for Railway

1. Go to **https://railway.app**
2. Sign in with your GitHub account

### 2. Deploy Backend

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `frankkode/research`
4. Railway will auto-detect Django and start building

### 3. Add PostgreSQL Database

1. In your project, click **"+ New Service"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway automatically connects it via `DATABASE_URL`

### 4. Configure Environment Variables

Click on your Django service → **"Variables"** tab → Add these:

**Required Variables:**
```env
SECRET_KEY=l=kih3f%ez1^9xaw79a&%&1*4c#f3u)m@w13_wj^gw-xj4+l)u
DEBUG=False
DJANGO_SETTINGS_MODULE=research_platform.settings_production
OPENAI_API_KEY=your-actual-openai-api-key-here
```

**Optional Variables:**
```env
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7
```

### 5. Get Your Backend URL

After deployment:
1. Your backend will be available at: `https://your-app-name.railway.app`
2. Add this to your variables:
   ```env
   ALLOWED_HOSTS=your-app-name.railway.app
   ```

### 6. Deploy Frontend

**Option A: Vercel (Recommended)**

1. Go to **vercel.com** → Import GitHub repo
2. Build settings:
   - **Root Directory**: `research-study-platform/frontend`
   - **Build Command**: `npm run build` 
   - **Output Directory**: `build`
3. Add environment variable:
   ```env
   REACT_APP_API_BASE_URL=https://your-backend-railway-domain.railway.app
   ```

**Option B: Netlify**

1. Go to **netlify.com** → New site from Git
2. Build settings:
   - **Base directory**: `research-study-platform/frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `research-study-platform/frontend/build`
3. Add environment variable:
   ```env
   REACT_APP_API_BASE_URL=https://your-backend-railway-domain.railway.app
   ```

### 7. Update CORS Settings

Add your frontend URL to backend environment variables:
```env
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

### 8. Test Everything

1. **Backend**: Visit `https://your-app.railway.app/admin/` - should show Django admin
2. **Frontend**: Visit your frontend URL - should load the research platform
3. **Database**: Try registering a user - should work
4. **ChatGPT**: Test the chat functionality - should respond to any topic

## Static Files Explanation

### How It Works
- **WhiteNoise** serves static files (CSS, JS) directly from Railway
- No external storage needed (S3, etc.)
- Files are compressed and cached automatically
- Perfect for apps without user-uploaded images

### What's Served
- Django admin CSS/JS
- REST framework browsable API styles
- Any custom CSS/JS from your app

### No Media Files Needed
Since your research platform doesn't use images, you don't need external storage.

## Troubleshooting

### Build Fails
- Check Railway build logs for specific errors
- Ensure `requirements.txt` is properly formatted
- Verify Python version compatibility

### Static Files Not Loading
- Check that `DJANGO_SETTINGS_MODULE=research_platform.settings_production`
- Verify `collectstatic` ran during deployment
- Look for static files errors in Railway logs

### Database Issues
- Ensure PostgreSQL service is running in Railway
- Check that `DATABASE_URL` appears in your service variables
- Verify migrations ran successfully in deployment logs

### CORS Issues
- Make sure `CORS_ALLOWED_ORIGINS` includes your exact frontend URL
- Include both `http://` and `https://` if testing locally

### OpenAI Issues
- Verify your API key is correct and has credits
- Check OpenAI usage in your OpenAI dashboard
- Monitor rate limiting in Railway logs

## Expected Costs

- **Railway**: $5-10/month (includes PostgreSQL)
- **Vercel/Netlify**: Free tier sufficient
- **OpenAI**: Pay per usage (~$0.03 per 1K tokens for GPT-4)

## Monitoring

Railway provides built-in monitoring:
- **Metrics**: CPU, memory, request count
- **Logs**: Real-time application logs
- **Deployments**: History of all deployments

## Database Backups

Railway automatically backs up PostgreSQL databases. For additional safety:
1. Use Django's `dumpdata` command periodically
2. Export via Railway's database connection tools
3. Consider automated backup scripts

## Next Steps

1. **Create admin user**: Use Railway console to run `python manage.py createsuperuser`
2. **Add real participants**: Remove test data, add real study participants
3. **Monitor usage**: Keep an eye on OpenAI costs and Railway resources
4. **Custom domain**: Add your own domain in Railway settings

This setup gives you a production-ready research platform without complex external dependencies!