from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .models import UserProfile
from apps.core.models import User
import secrets
import string
import random


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def register(request):
    if request.method == 'OPTIONS':
        from django.http import HttpResponse
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    # Make a copy of request data to modify it
    data = request.data.copy()
    # Override study_group with random assignment
    data['study_group'] = random.choice(['PDF', 'ChatGPT'])
    
    serializer = UserRegistrationSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        UserProfile.objects.create(user=user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'OPTIONS':
        from django.http import HttpResponse
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except:
        return Response({'error': 'Error logging out'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    print(f"DEBUG: Profile request for user {request.user.participant_id}")
    print(f"DEBUG: User interaction_completed: {request.user.interaction_completed}")
    serializer = UserSerializer(request.user)
    response_data = serializer.data
    print(f"DEBUG: Serialized interaction_completed: {response_data.get('interaction_completed')}")
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_consent(request):
    """Submit consent form and update user status"""
    try:
        agreed = request.data.get('agreed', False)
        
        if not agreed:
            return Response({
                'error': 'Consent must be agreed to proceed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.consent_completed = True
        user.consent_completed_at = timezone.now()
        user.save()
        
        # Update user profile if it exists
        try:
            profile = user.profile
            profile.consent_given = True
            profile.consent_timestamp = timezone.now()
            profile.save()
        except:
            # Create profile if it doesn't exist
            UserProfile.objects.create(
                user=user,
                consent_given=True,
                consent_timestamp=timezone.now()
            )
        
        return Response({
            'message': 'Consent submitted successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to submit consent',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_interaction(request):
    """Mark interaction phase as completed"""
    try:
        user = request.user
        user.interaction_completed = True
        user.interaction_completed_at = timezone.now()
        user.save()
        
        return Response({
            'message': 'Interaction completed successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to complete interaction',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def google_auth(request):
    """Authenticate user with Google OAuth token"""
    print(f"🔍 Google auth request from: {request.META.get('HTTP_ORIGIN', 'Unknown origin')}")
    print(f"🔍 Request method: {request.method}")
    print(f"🔍 Request data keys: {list(request.data.keys()) if hasattr(request, 'data') else 'No data'}")
    
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        from django.http import HttpResponse
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    try:
        token = request.data.get('token')
        study_group = request.data.get('study_group', random.choice(['PDF', 'ChatGPT']))  # Random assignment
        
        if not token:
            return Response({
                'error': 'Google token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the Google token
        try:
            # You'll need to set GOOGLE_OAUTH2_CLIENT_ID in your settings
            client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)
            if not client_id:
                return Response({
                    'error': 'Google OAuth not configured'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), client_id
            )
            
            email = idinfo.get('email')
            name = idinfo.get('name', '')
            
            if not email:
                return Response({
                    'error': 'Email not provided by Google'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError:
            return Response({
                'error': 'Invalid Google token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
            # User exists, log them in
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'created': False
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Create new user
            username = email.split('@')[0]
            # Generate unique participant ID
            participant_id = f"GOOGLE_{secrets.token_hex(4).upper()}"
            
            # Ensure unique username and participant_id
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            while User.objects.filter(participant_id=participant_id).exists():
                participant_id = f"GOOGLE_{secrets.token_hex(4).upper()}"
            
            user = User.objects.create_user(
                email=email,
                username=username,
                participant_id=participant_id,
                study_group=study_group,
                password=''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'created': True
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'error': 'Google authentication failed',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)