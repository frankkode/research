#!/usr/bin/env python3
"""
Test script to verify Redis connection with different configurations
"""

import redis
import os
import sys
from urllib.parse import urlparse

def test_redis_connection(redis_url, description=""):
    """Test Redis connection and basic operations"""
    print(f"\n{'='*50}")
    print(f"Testing Redis Connection: {description}")
    print(f"URL: {redis_url}")
    print(f"{'='*50}")
    
    try:
        # Parse URL for display
        parsed = urlparse(redis_url)
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Auth: {'Yes' if parsed.password else 'No'}")
        
        # Connect to Redis
        r = redis.from_url(redis_url, decode_responses=True)
        
        # Test basic operations
        print("Testing basic operations...")
        
        # Ping test
        pong = r.ping()
        print(f"✅ Ping: {pong}")
        
        # Set/Get test
        test_key = "celery_test_key"
        test_value = "Hello from Celery!"
        r.set(test_key, test_value, ex=30)  # Expire in 30 seconds
        retrieved_value = r.get(test_key)
        print(f"✅ Set/Get: {retrieved_value}")
        
        # List test (for Celery queues)
        queue_name = "celery"
        r.lpush(queue_name, "test_task")
        queue_length = r.llen(queue_name)
        print(f"✅ Queue operations: Queue length = {queue_length}")
        r.ltrim(queue_name, 1, 0)  # Clear the queue
        
        # Database selection test
        r.select(1)
        r.set("test_db1", "database_1_test")
        r.select(0)
        print("✅ Database selection: OK")
        
        # Info test
        info = r.info('memory')
        used_memory = info.get('used_memory_human', 'N/A')
        print(f"✅ Memory usage: {used_memory}")
        
        print(f"✅ All tests passed for {description}!")
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return False
    except redis.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False

def main():
    print("Redis Connection Tester")
    print("=" * 50)
    
    # Test configurations
    test_configs = []
    
    # Local Redis
    test_configs.append({
        'url': 'redis://localhost:6379',
        'description': 'Local Redis (no auth)'
    })
    
    # Redis Cloud - you need to update this with your actual password
    redis_password = os.getenv('REDIS_PASSWORD', 'your-password-here')
    test_configs.append({
        'url': f'redis://:{redis_password}@redis-13201.crce175.eu-north-1-1.ec2.redns.redis-cloud.com:13201',
        'description': 'Redis Cloud'
    })
    
    # Environment variable
    redis_url_env = os.getenv('REDIS_URL')
    if redis_url_env:
        test_configs.append({
            'url': redis_url_env,
            'description': 'Environment REDIS_URL'
        })
    
    # Run tests
    successful_connections = []
    failed_connections = []
    
    for config in test_configs:
        if test_redis_connection(config['url'], config['description']):
            successful_connections.append(config['description'])
        else:
            failed_connections.append(config['description'])
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Successful connections: {len(successful_connections)}")
    for conn in successful_connections:
        print(f"   - {conn}")
    
    print(f"❌ Failed connections: {len(failed_connections)}")
    for conn in failed_connections:
        print(f"   - {conn}")
    
    if successful_connections:
        print(f"\n🎉 Ready to use Redis for Celery!")
    else:
        print(f"\n⚠️  No Redis connections successful. Check your configuration.")

if __name__ == "__main__":
    main()