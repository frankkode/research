"""
Simple authentication views that work locally without CORS issues
"""
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth import get_user_model

User = get_user_model()
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .group_assignment import get_balanced_study_group, get_group_statistics
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
        
        # Generate participant ID and assign balanced study group
        participant_id = f"USER_{secrets.token_hex(4).upper()}"
        study_group = get_balanced_study_group()  # Balanced assignment
        
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


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def simple_google_auth(request):
    """Google OAuth authentication endpoint"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        import jwt
        from django.conf import settings
        import requests
        
        data = json.loads(request.body)
        token = data.get('token')
        
        if not token:
            return JsonResponse({
                'success': False,
                'error': 'Google token required'
            })
        
        # Verify Google token
        try:
            # Get Google's public keys
            google_keys_url = 'https://www.googleapis.com/oauth2/v3/certs'
            google_keys = requests.get(google_keys_url).json()
            
            # Decode token header to get key id
            header = jwt.get_unverified_header(token)
            key_id = header['kid']
            
            # Find the correct key
            public_key = None
            for key_data in google_keys['keys']:
                if key_data['kid'] == key_id:
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
                    break
            
            if not public_key:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid Google token key'
                })
            
            # Verify and decode the token
            google_client_id = '875588092118-0d4ok5qjudm1uh0nd68mf5s54ofvdf4r.apps.googleusercontent.com'
            payload = jwt.decode(
                token, 
                public_key, 
                algorithms=['RS256'],
                audience=google_client_id
            )
            
        except jwt.InvalidTokenError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid Google token: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Token verification failed: {str(e)}'
            })
        
        # Extract user information from Google token
        email = payload.get('email')
        name = payload.get('name', '')
        google_id = payload.get('sub')
        
        if not email or not google_id:
            return JsonResponse({
                'success': False,
                'error': 'Invalid Google token payload'
            })
        
        # Check if user already exists
        try:
            user = User.objects.get(email=email)
            # User exists, log them in
            django_login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Google login successful',
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'participant_id': user.participant_id,
                    'study_group': user.study_group
                }
            })
            
        except User.DoesNotExist:
            # Create new user
            username = email.split('@')[0]  # Use email prefix as username
            counter = 1
            original_username = username
            
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1
            
            # Generate participant ID and assign balanced study group
            participant_id = f"GUSER_{secrets.token_hex(4).upper()}"
            study_group = get_balanced_study_group()  # Balanced assignment
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name.split(' ')[0] if name else '',
                last_name=' '.join(name.split(' ')[1:]) if len(name.split(' ')) > 1 else '',
                participant_id=participant_id,
                study_group=study_group
            )
            
            # Set an unusable password since this is OAuth
            user.set_unusable_password()
            user.save()
            
            django_login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Google registration and login successful',
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
            'error': f'Google authentication failed: {str(e)}'
        })