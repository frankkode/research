# Dashboard Data Troubleshooting Guide

## 🔍 Problem: Admin Dashboards Show No Data

If your admin dashboards (Overview, Learning Analysis, Basic Analytics, Research Data) are empty, follow this step-by-step guide to diagnose and fix the issue.

## 📋 Quick Diagnosis Checklist

### ✅ Step 1: Check Backend Server
```bash
cd research-study-platform/backend
python manage.py runserver 8000
```
- ✅ Server should start without errors
- ✅ Visit http://localhost:8000/admin/ - should show Django admin
- ✅ Should see "Django REST framework" at http://localhost:8000/api/

### ✅ Step 2: Check Frontend Connection
```bash
cd research-study-platform/frontend
npm start
```
- ✅ Frontend should start on http://localhost:3000
- ✅ Login page should load without console errors
- ✅ Check browser Network tab for API call failures

### ✅ Step 3: Test API Endpoints
Use the **Debug Data** tab in admin dashboard:
1. Go to Admin → **Debug Data**
2. Click **"Run Diagnostics"**
3. Check results for each endpoint

## 🔧 Common Solutions

### Solution 1: No Data in Database
**Symptoms:** API endpoints work but return empty arrays

**Fix:** Create test data
```bash
cd research-study-platform/backend
python manage.py populate_test_data --participants 50
```

### Solution 2: Database Migration Issues
**Symptoms:** API errors about missing tables

**Fix:** Run migrations
```bash
python manage.py migrate
python manage.py makemigrations
python manage.py migrate
```

### Solution 3: Authentication Problems
**Symptoms:** 401/403 errors in API calls

**Fix:** Create admin user and login
```bash
python manage.py createsuperuser
# Username: admin
# Password: admin123
```

### Solution 4: CORS Issues
**Symptoms:** CORS errors in browser console

**Fix:** Check `settings.py` has correct CORS settings:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Solution 5: Missing Dependencies
**Symptoms:** Import errors in Django

**Fix:** Install requirements
```bash
pip install -r requirements.txt
```

## 🧪 Using the Debug Data Tool

I've added a **Debug Data** tab to your admin dashboard that:

1. **Tests all API endpoints** - Shows which are working/failing
2. **Counts data records** - Shows how much data exists
3. **Provides specific fixes** - Tells you exactly what to run
4. **Shows data summary** - Displays what data is available

### How to Access:
1. Login to admin dashboard
2. Click **"Debug Data"** tab
3. Click **"Run Diagnostics"**
4. Follow the recommendations shown

## 📊 API Endpoint Reference

Your dashboards use these endpoints:

| Dashboard | Endpoint | Purpose |
|-----------|----------|---------|
| Overview | `/research/dashboard/overview/` | Summary stats |
| All Tabs | `/research/dashboard/activity_timeline/` | Timeline data |
| Learning Analysis | `/research/dashboard/learning_effectiveness/` | Effectiveness comparison |
| Basic/Research | `/research/participants/all/` | Participant data |
| All Tabs | `/research/statistics/` | Study statistics |

## 🐛 Advanced Debugging

### Check Django Logs
```bash
tail -f backend/logs/django.log
```

### Test API Manually
```bash
# Test from command line
python test_dashboard_data.py
```

### Check Database Directly
```bash
python manage.py shell
>>> from apps.core.models import User
>>> User.objects.count()  # Should be > 0
```

### Browser Developer Tools
1. Open dev tools (F12)
2. Go to Network tab
3. Refresh dashboard
4. Look for failed API calls (red entries)
5. Check console for JavaScript errors

## 🎯 Expected Data Structure

After running `populate_test_data`, you should have:

- **50 test participants** (25 ChatGPT, 25 PDF)
- **Study sessions** with realistic durations
- **Chat interactions** for ChatGPT group
- **PDF viewing data** for PDF group
- **Quiz responses** with pre/post scores
- **Interaction logs** for all participants

## 📈 Verification Steps

1. **Debug Data tab** shows all green checkmarks
2. **Overview tab** shows participant counts
3. **Learning Analysis tab** shows comparison charts
4. **Basic Analytics tab** shows completion rates
5. **Research Data tab** shows group distributions

## 🚨 If Still Not Working

1. **Check both servers are running** (backend:8000, frontend:3000)
2. **Clear browser cache** and reload
3. **Check browser console** for JavaScript errors
4. **Verify you're logged in as admin user**
5. **Run the populate_test_data command** with --clear flag:
   ```bash
   python manage.py populate_test_data --clear --participants 50
   ```

## 💡 Quick Test Commands

```bash
# Full reset and test data creation
cd research-study-platform/backend
python manage.py migrate
python manage.py populate_test_data --clear --participants 50
python manage.py runserver 8000

# In another terminal
cd research-study-platform/frontend  
npm start
```

Then visit http://localhost:3000/admin and check the Debug Data tab!

---

**Need more help?** Check the Debug Data tab - it will give you specific, actionable steps based on your exact situation!