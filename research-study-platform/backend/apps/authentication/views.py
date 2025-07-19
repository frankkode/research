from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils import timezone
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .models import UserProfile


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        UserProfile.objects.create(user=user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
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