from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'message': 'Research Platform API',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'studies': '/api/studies/',
            'chats': '/api/chats/',
            'pdfs': '/api/pdfs/',
            'quizzes': '/api/quizzes/',
            'research': '/api/research/',
            'core': '/api/core/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/studies/', include('apps.studies.urls')),
    path('api/chats/', include('apps.chats.urls')),
    path('api/pdfs/', include('apps.pdfs.urls')),
    path('api/quizzes/', include('apps.quizzes.urls')),
    path('api/research/', include('apps.research.urls')),
    path('api/core/', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)