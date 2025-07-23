import os
from pathlib import Path
import environ

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='your-secret-key-here')

DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['localhost','127.0.0.1','0.0.0.0','gtpresearch.up.railway.app','research-production-46af.up.railway.app']

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_extensions',
    'django_celery_beat',
    # CSP will be added when installed: 'csp',
]

LOCAL_APPS = [
    'apps.core',
    'apps.authentication',
    'apps.studies',
    'apps.chats',
    'apps.pdfs',
    'apps.quizzes',
    'apps.research',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'research_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'research_platform.wsgi.application'

import dj_database_url

# Database Configuration - Railway provides DATABASE_URL
DATABASE_URL = env('DATABASE_URL', default=None)

if DATABASE_URL:
    # Railway or other cloud database URL
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
] if os.path.exists(os.path.join(BASE_DIR, 'static')) and os.listdir(os.path.join(BASE_DIR, 'static')) else []

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://gtpresearch.up.railway.app",
    "https://research-production-46af.up.railway.app",
]

CORS_ALLOW_CREDENTIALS = True

# OpenAI Configuration
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4')
OPENAI_MAX_TOKENS = env('OPENAI_MAX_TOKENS', default=500, cast=int)
OPENAI_TEMPERATURE = env('OPENAI_TEMPERATURE', default=0.7, cast=float)
OPENAI_RATE_LIMIT_REQUESTS = env('OPENAI_RATE_LIMIT_REQUESTS', default=60, cast=int)  # per minute
OPENAI_RATE_LIMIT_TOKENS = env('OPENAI_RATE_LIMIT_TOKENS', default=40000, cast=int)  # per minute
from django.conf import settings
client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)

# Google OAuth Configuration
GOOGLE_OAUTH2_CLIENT_ID = env('GOOGLE_OAUTH2_CLIENT_ID', default='')

REDIS_URL = env('REDIS_URL', default='redis://localhost:6379')

# Celery Configuration
# Use different Redis databases for broker and results to avoid conflicts
def get_redis_url_with_db(base_url, db_number):
    """Helper to append database number to Redis URL"""
    if base_url.endswith('/'):
        return f"{base_url.rstrip('/')}/{db_number}"
    elif '/' in base_url.split('://', 1)[1]:
        # URL already has a database number, replace it
        parts = base_url.rsplit('/', 1)
        return f"{parts[0]}/{db_number}"
    else:
        return f"{base_url}/{db_number}"

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=get_redis_url_with_db(REDIS_URL, 0))
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=get_redis_url_with_db(REDIS_URL, 1))
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Worker Configuration
CELERY_WORKER_CONCURRENCY = env('CELERY_WORKER_CONCURRENCY', default=2, cast=int)
CELERY_WORKER_MAX_TASKS_PER_CHILD = env('CELERY_WORKER_MAX_TASKS_PER_CHILD', default=1000, cast=int)
CELERY_TASK_ALWAYS_EAGER = env('CELERY_TASK_ALWAYS_EAGER', default=DEBUG, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = env('CELERY_TASK_EAGER_PROPAGATES', default=True, cast=bool)

# Celery Beat Configuration
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Task routing and execution
CELERY_TASK_ROUTES = {
    'apps.quizzes.tasks.schedule_transfer_quiz_notification': {'queue': 'notifications'},
    'apps.quizzes.tasks.send_manual_transfer_quiz_link': {'queue': 'notifications'},
}

# Celery task time limits (in seconds)
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 600       # 10 minutes

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Research Platform Specific Settings
MAX_PARTICIPANTS_PER_STUDY = env('MAX_PARTICIPANTS_PER_STUDY', default=1000, cast=int)
SESSION_TIMEOUT_MINUTES = env('SESSION_TIMEOUT_MINUTES', default=30, cast=int)
QUIZ_TIME_LIMIT_MINUTES = env('QUIZ_TIME_LIMIT_MINUTES', default=45, cast=int)
PDF_MAX_SIZE_MB = env('PDF_MAX_SIZE_MB', default=50, cast=int)

# Frontend URL for email links
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:3000')

# Email settings
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@research-platform.com')

# Content Security Policy (CSP) Settings
# Allow 'unsafe-eval' for recharts/d3 visualization library
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "'unsafe-eval'"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", "data:", "blob:"]
CSP_FONT_SRC = ["'self'", "data:"]
CSP_CONNECT_SRC = ["'self'"]
CSP_DEFAULT_SRC = ["'self'"]