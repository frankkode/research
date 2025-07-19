from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.core.models import User
from .models import UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'participant_id', 'study_group']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def validate_participant_id(self, value):
        if User.objects.filter(participant_id=value).exists():
            raise serializers.ValidationError("This participant ID is already registered")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['age', 'gender', 'education_level', 'consent_given', 'consent_timestamp']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'participant_id', 'study_group', 'profile', 
            'created_at', 'completion_percentage',
            'consent_completed', 'pre_quiz_completed', 'interaction_completed', 
            'post_quiz_completed', 'study_completed', 'is_staff', 'is_superuser',
            'consent_completed_at', 'pre_quiz_completed_at', 'interaction_completed_at',
            'post_quiz_completed_at', 'study_completed_at'
        ]