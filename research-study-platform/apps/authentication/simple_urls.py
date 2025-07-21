"""
Simple URL configuration for authentication
"""
from django.urls import path
from . import simple_views

urlpatterns = [
    path('test/', simple_views.simple_test, name='simple_test'),
    path('register/', simple_views.simple_register, name='simple_register'),
    path('login/', simple_views.simple_login, name='simple_login'),
    path('google-auth/', simple_views.simple_google_auth, name='simple_google_auth'),
]