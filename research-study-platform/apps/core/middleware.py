"""
Custom middleware for handling CORS in production
"""
from django.http import HttpResponse


class ForceProductionCORSMiddleware:
    """
    Force CORS headers for production deployment on Railway
    This middleware ensures CORS headers are always present
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # List of allowed origins
        allowed_origins = [
            'https://gtpresearch.up.railway.app',
            'https://research-production-46af.up.railway.app',
            'http://localhost:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:3001',
        ]
        
        origin = request.META.get('HTTP_ORIGIN', '')
        
        # Debug logging
        if origin:
            print(f"🌐 CORS Middleware - Origin: {origin}, Method: {request.method}, Path: {request.path}")
        
        # Handle preflight OPTIONS requests
        if request.method == 'OPTIONS':
            print(f"📋 Handling OPTIONS preflight for {request.path}")
            response = HttpResponse()
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = (
                'Content-Type, Authorization, X-Requested-With, '
                'X-CSRFToken, Accept, Accept-Version, Content-Length, '
                'Content-MD5, Date, X-Api-Version'
            )
            response['Access-Control-Max-Age'] = '86400'  # 24 hours
        else:
            response = self.get_response(request)
        
        # Add CORS headers to all responses
        if origin in allowed_origins:
            response['Access-Control-Allow-Origin'] = origin
        elif origin.endswith('.up.railway.app'):
            response['Access-Control-Allow-Origin'] = origin
        elif 'localhost' in origin or '127.0.0.1' in origin:
            response['Access-Control-Allow-Origin'] = origin
        else:
            # For debugging - log unknown origins
            print(f"🚫 Unknown origin: {origin}")
            
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = (
            'Content-Type, Authorization, X-Requested-With, '
            'X-CSRFToken, Accept, Accept-Version, Content-Length, '
            'Content-MD5, Date, X-Api-Version'
        )
        
        return response