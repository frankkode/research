#!/usr/bin/env python3
"""
Simple script to test dashboard API endpoints and data availability
Run this from the backend directory to check if your APIs are working
"""

import requests
import json
import sys

# Configuration
BASE_URL = 'http://localhost:8001/api'
LOGIN_URL = f'{BASE_URL}/auth/login/'

# Test credentials (create a test admin user)
TEST_ADMIN = {
    'username': 'admin',
    'password': 'admin123'
}

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(LOGIN_URL, data=TEST_ADMIN)
        if response.status_code == 200:
            return response.json().get('token')
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server. Make sure it's running on http://localhost:8001")
        return None

def test_endpoint(url, token, endpoint_name):
    """Test a specific API endpoint"""
    headers = {'Authorization': f'Token {token}'} if token else {}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {endpoint_name}: {len(data) if isinstance(data, list) else 'Success'}")
            return data
        else:
            print(f"❌ {endpoint_name}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ {endpoint_name}: Error - {e}")
        return None

def main():
    print("🔍 Testing Dashboard API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("\n💡 To fix login issues:")
        print("1. Make sure Django server is running: python manage.py runserver 8001")
        print("2. Create admin user: python manage.py createsuperuser")
        print("3. Use username 'admin' and password 'admin123'")
        return
    
    print(f"✅ Authentication successful")
    
    # Test endpoints
    endpoints = [
        (f'{BASE_URL}/research/dashboard/overview/', 'Dashboard Overview'),
        (f'{BASE_URL}/research/dashboard/activity_timeline/', 'Activity Timeline'),
        (f'{BASE_URL}/research/dashboard/learning_effectiveness/', 'Learning Effectiveness'),
        (f'{BASE_URL}/research/studies/', 'Research Studies'),
        (f'{BASE_URL}/research/participants/all/', 'All Participants'),
        (f'{BASE_URL}/research/statistics/', 'Study Statistics'),
    ]
    
    print("\n📊 Testing API Endpoints:")
    print("-" * 30)
    
    results = {}
    for url, name in endpoints:
        results[name] = test_endpoint(url, token, name)
    
    # Analyze results
    print("\n📋 Data Analysis:")
    print("-" * 20)
    
    if results.get('All Participants'):
        participants = results['All Participants']
        if participants:
            chatgpt_count = len([p for p in participants if p.get('study_group') == 'CHATGPT'])
            pdf_count = len([p for p in participants if p.get('study_group') == 'PDF'])
            completed_count = len([p for p in participants if p.get('study_completed')])
            
            print(f"👥 Total Participants: {len(participants)}")
            print(f"🤖 ChatGPT Group: {chatgpt_count}")
            print(f"📄 PDF Group: {pdf_count}")
            print(f"✅ Completed: {completed_count}")
        else:
            print("❌ No participant data found")
    
    if results.get('Dashboard Overview'):
        overview = results['Dashboard Overview']
        if overview:
            print(f"📈 Overview Data Available: ✅")
            print(f"   - Total Participants: {overview.get('total_participants', 0)}")
            print(f"   - Completion Rate: {overview.get('completion_rate', 0)}%")
        else:
            print("❌ No overview data")
    
    if results.get('Learning Effectiveness'):
        effectiveness = results['Learning Effectiveness']
        if effectiveness and effectiveness.get('learning_metrics'):
            print(f"🧠 Learning Effectiveness Data: ✅")
            for metric in effectiveness['learning_metrics']:
                print(f"   - {metric.get('group')}: {metric.get('learning_gain', 0)}% gain")
        else:
            print("❌ No learning effectiveness data")
    
    # Recommendations
    print("\n💡 Recommendations:")
    print("-" * 20)
    
    if not results.get('All Participants') or not participants:
        print("1. 🔧 Create test data:")
        print("   python manage.py populate_test_data --participants 50")
        print("2. 🔄 Run migrations if needed:")
        print("   python manage.py migrate")
        print("3. 🌱 Create sample study:")
        print("   python manage.py create_sample_study")
    else:
        print("✅ Data looks good! Check your frontend API calls.")
        print("🔍 Open browser dev tools and check Network tab for API errors.")

if __name__ == '__main__':
    main()