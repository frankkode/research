from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('consent/', views.submit_consent, name='submit_consent'),
    path('complete-interaction/', views.complete_interaction, name='complete_interaction'),
    path('google-auth/', views.google_auth, name='google_auth'),
    path('cors-test/', views.cors_test, name='cors_test'),
    path('group-statistics/', views.group_statistics, name='group_statistics'),
]