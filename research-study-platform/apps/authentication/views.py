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
from .group_assignment import get_balanced_study_group, get_group_statistics
from apps.core.models import User
import secrets
import string


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def register(request):
    print(f"🔍 Register request from: {request.META.get('HTTP_ORIGIN', 'Unknown origin')}")
    print(f"🔍 Request method: {request.method}")
    print(f"🔍 Request data: {request.data}")
    
    # Make a copy of request data to modify it
    data = request.data.copy()
    # Override study_group with balanced assignment
    data['study_group'] = get_balanced_study_group()
    
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
    print(f"🔍 Content type: {request.content_type}")
    
    # Early return with detailed error response for debugging
    try:
        if not hasattr(request, 'data') or not request.data:
            error_msg = "No request data received"
            print(f"❌ {error_msg}")
            return Response({
                'error': error_msg,
                'debug_info': {
                    'method': request.method,
                    'content_type': request.content_type,
                    'headers': dict(request.headers)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as debug_error:
        print(f"❌ Debug error: {debug_error}")
        return Response({
            'error': 'Failed to process request',
            'debug_error': str(debug_error)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        token = request.data.get('token')
        study_group = request.data.get('study_group', get_balanced_study_group())  # Balanced assignment
        
        if not token:
            error_msg = 'Google token is required'
            print(f"❌ {error_msg}")
            return Response({
                'error': error_msg,
                'received_data': dict(request.data),
                'data_keys': list(request.data.keys()) if request.data else []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the Google token
        try:
            # Check if Google OAuth libraries are available
            try:
                from google.oauth2 import id_token
                from google.auth.transport import requests as google_requests
            except ImportError as import_error:
                print(f"❌ Google OAuth libraries not available: {import_error}")
                return Response({
                    'error': 'Google OAuth libraries not installed',
                    'detail': str(import_error)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # You'll need to set GOOGLE_OAUTH2_CLIENT_ID in your settings
            client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)
            print(f"🔑 Using Google Client ID: {client_id}")
            
            if not client_id:
                return Response({
                    'error': 'Google OAuth not configured'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Verify the token
            print(f"🔍 Verifying Google token: {token[:20]}...")
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), client_id
            )
            print(f"✅ Token verified successfully")
            
            email = idinfo.get('email')
            name = idinfo.get('name', '')
            
            print(f"📧 Google user: {email} ({name})")
            
            if not email:
                return Response({
                    'error': 'Email not provided by Google'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as ve:
            print(f"❌ Google token verification failed: {ve}")
            return Response({
                'error': 'Invalid Google token',
                'detail': str(ve)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as token_error:
            print(f"❌ Google token verification error: {token_error}")
            return Response({
                'error': 'Google token verification failed',
                'detail': str(token_error)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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


@api_view(['GET', 'POST', 'OPTIONS'])
@permission_classes([AllowAny])
def cors_test(request):
    """Test endpoint to verify CORS is working"""
    print(f"🧪 CORS Test - Origin: {request.META.get('HTTP_ORIGIN', 'None')}, Method: {request.method}")
    
    return Response({
        'message': 'CORS test successful',
        'method': request.method,
        'origin': request.META.get('HTTP_ORIGIN', 'None'),
        'headers': dict(request.headers),
        'timestamp': timezone.now().isoformat(),
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def group_statistics(request):
    """Get current group distribution statistics"""
    stats = get_group_statistics()
    return Response({
        'message': 'Group statistics retrieved successfully',
        'statistics': stats,
        'timestamp': timezone.now().isoformat(),
    }, status=status.HTTP_200_OK)