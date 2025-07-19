#!/usr/bin/env python
"""
Test script to verify user registration functionality
"""
import os
import sys
import django
import requests
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from apps.core.models import User
from apps.authentication.models import UserProfile

def test_registration_model():
    """Test user registration using Django models directly"""
    print("Testing user registration via Django models...")
    
    # Clean up any existing test user
    User.objects.filter(email='test@example.com').delete()
    
    # Create a test user
    try:
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            participant_id='P001',
            study_group='PDF'
        )
        
        # Create user profile
        profile = UserProfile.objects.create(user=user)
        
        print(f"✅ User created successfully: {user.email}")
        print(f"✅ User profile created: {profile.id}")
        print(f"✅ Participant ID: {user.participant_id}")
        print(f"✅ Study group: {user.study_group}")
        
        # Clean up
        user.delete()
        
        return True
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def test_registration_api():
    """Test user registration via API endpoint"""
    print("\nTesting user registration via API...")
    
    # Clean up any existing test user
    User.objects.filter(email='test2@example.com').delete()
    
    # Test registration data
    registration_data = {
        'email': 'test2@example.com',
        'username': 'testuser2',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'participant_id': 'P002',
        'study_group': 'CHATGPT'
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/auth/register/',
            json=registration_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Registration successful via API")
            print(f"✅ Token received: {data['token'][:10]}...")
            print(f"✅ User data: {data['user']['email']}")
            
            # Clean up
            User.objects.filter(email='test2@example.com').delete()
            
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running on port 8000.")
        return False
    except Exception as e:
        print(f"❌ Error during API registration: {e}")
        return False

def test_registration_validation():
    """Test registration validation"""
    print("\nTesting registration validation...")
    
    # Test duplicate participant ID
    User.objects.filter(participant_id='P003').delete()
    
    # Create first user
    user1 = User.objects.create_user(
        email='test3@example.com',
        username='testuser3',
        password='testpass123',
        participant_id='P003',
        study_group='PDF'
    )
    
    # Try to create another user with same participant ID
    try:
        registration_data = {
            'email': 'test4@example.com',
            'username': 'testuser4',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'participant_id': 'P003',  # Duplicate
            'study_group': 'CHATGPT'
        }
        
        response = requests.post(
            'http://localhost:8000/api/auth/register/',
            json=registration_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            print("✅ Duplicate participant ID validation working")
        else:
            print(f"❌ Expected 400 status code, got {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server for validation test")
    except Exception as e:
        print(f"❌ Error during validation test: {e}")
    
    # Clean up
    user1.delete()

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    # Create a test user
    User.objects.filter(email='logintest@example.com').delete()
    
    user = User.objects.create_user(
        email='logintest@example.com',
        username='logintest',
        password='loginpass123',
        participant_id='P004',
        study_group='PDF'
    )
    
    try:
        login_data = {
            'email': 'logintest@example.com',
            'password': 'loginpass123'
        }
        
        response = requests.post(
            'http://localhost:8000/api/auth/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful")
            print(f"✅ Token received: {data['token'][:10]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server for login test")
    except Exception as e:
        print(f"❌ Error during login test: {e}")
    
    # Clean up
    user.delete()

if __name__ == '__main__':
    print("🧪 Testing Research Platform Registration System")
    print("=" * 50)
    
    # Test 1: Direct model registration
    model_test = test_registration_model()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Model Registration: {'✅ PASS' if model_test else '❌ FAIL'}")
    print("\n🎯 To run this project locally:")
    print("1. Backend: cd backend && source venv/bin/activate && python manage.py runserver")
    print("2. Frontend: cd frontend && npm install && npm start")
    print("3. Access: http://localhost:3000")
    print("\n📋 API Endpoints:")
    print("- POST /api/auth/register/ - User registration")
    print("- POST /api/auth/login/ - User login")
    print("- POST /api/auth/logout/ - User logout")
    print("- GET /api/auth/profile/ - User profile")