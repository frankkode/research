# Redis Cloud Setup Guide

## 🔍 Getting the Correct Connection String

Your current Redis endpoint shows authentication issues. Here's how to get the correct credentials:

### 1. **Check Redis Cloud Dashboard**
1. Go to your Redis Cloud console/dashboard
2. Navigate to your database instance
3. Look for "Connect" or "Connection" tab
4. Find the **complete connection string** - it should look like:
   ```
   redis://username:password@host:port
   ```
   or
   ```
   rediss://username:password@host:port  # with SSL
   ```

### 2. **Common Redis Cloud Formats**

#### Option A: Username + Password
```bash
redis://default:your-actual-password@redis-13201.crce175.eu-north-1-1.ec2.redns.redis-cloud.com:13201
```

#### Option B: Just Password (no username)
```bash
redis://:your-actual-password@redis-13201.crce175.eu-north-1-1.ec2.redns.redis-cloud.com:13201
```

#### Option C: SSL Connection (rediss://)
```bash
rediss://:your-actual-password@redis-13201.crce175.eu-north-1-1.ec2.redns.redis-cloud.com:13201
```

### 3. **What to Look For in Dashboard**
- **Host**: `redis-13201.crce175.eu-north-1-1.ec2.redns.redis-cloud.com` ✅ (you have this)
- **Port**: `13201` ✅ (you have this)
- **Password**: The API key might not be the right password
- **Username**: Often `default` or empty
- **SSL**: Check if SSL/TLS is required (would use `rediss://` instead of `redis://`)

### 4. **Alternative Credentials to Check**
In your Redis Cloud dashboard, look for:
- **Database Password** (different from API key)
- **Access Key**
- **Auth String**
- **Connection String** (pre-formatted)

## 🔧 **Current Configuration**

### Working Setup (Local Redis)
```bash
# .env file
REDIS_URL=redis://localhost:6379  # Currently working
```

### Redis Cloud Setup (Once you get correct credentials)
```bash
# .env file
REDIS_URL=redis://correct-username:correct-password@redis-13201.crce175.eu-north-1-1.ec2.redns.redis-cloud.com:13201
```

## 🧪 **Testing New Credentials**

Once you get the correct connection string from Redis Cloud:

```bash
# Test the connection
export REDIS_URL="redis://username:password@host:port"
python3 scripts/test-redis-connection.py

# Update .env file
# Change REDIS_URL in .env to the working connection string

# Test Django configuration
python3 manage.py shell -c "
from django.conf import settings
import redis
r = redis.from_url(settings.REDIS_URL)
print('Redis ping:', r.ping())
"
```

## 📋 **Troubleshooting Checklist**

1. ✅ **Endpoint Format**: `redis-13201.crce175.eu-north-1-1.ec2.redns.redis-cloud.com:13201`
2. ❓ **Username**: Check if needed (often `default` or empty)
3. ❓ **Password**: API key might not be the database password
4. ❓ **SSL**: Check if `rediss://` is required instead of `redis://`
5. ❓ **IP Whitelist**: Ensure your IP is allowed to connect
6. ❓ **Database Access**: Verify the database is active and accessible

## 🎯 **Next Steps**

1. **Get the exact connection string from Redis Cloud dashboard**
2. **Test it with the script**: `python3 scripts/test-redis-connection.py`
3. **Update `.env`** when you find the working format
4. **Switch from local to cloud Redis**

For now, your Celery setup works perfectly with local Redis for development!