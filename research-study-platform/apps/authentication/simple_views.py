"""
Simple authentication views that work locally without CORS issues
"""
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth import get_user_model

User = get_user_model()
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import secrets
import string


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def simple_register(request):
    """Simple registration endpoint"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return JsonResponse({
                'success': False,
                'error': 'Username, email and password required'
            })
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'error': 'Username already exists'
            })
            
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'Email already exists'
            })
        
        # Generate participant ID and assign default study group
        participant_id = f"USER_{secrets.token_hex(4).upper()}"
        study_group = 'PDF'  # Default to PDF group
        
        # Create user with required fields
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            participant_id=participant_id,
            study_group=study_group
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'participant_id': participant_id,
                'study_group': study_group
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def simple_login(request):
    """Simple login endpoint"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return JsonResponse({
                'success': False,
                'error': 'Username and password required'
            })
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user:
            django_login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'participant_id': user.participant_id,
                    'study_group': user.study_group
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid username or password'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def simple_test(request):
    """Simple test endpoint"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    return JsonResponse({
        'success': True,
        'message': 'Server is working!',
        'timestamp': '2025-07-21'
    })