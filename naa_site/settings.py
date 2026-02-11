"""
Django settings for NAA Portal project.
Production-ready configuration with Cloudinary, WhiteNoise, and PostgreSQL.
"""

import os
import dj_database_url
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# IMPORTANT: Set DEBUG=False in production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Prevent running in production with default SECRET_KEY
if not DEBUG and SECRET_KEY == 'django-insecure-change-this-in-production':
    raise ValueError(
        "Set SECRET_KEY in the environment when DEBUG=False. "
        "Do not use the default insecure key in production."
    )

ALLOWED_HOSTS = [
    'naa-portal.onrender.com',
    'localhost',
    '127.0.0.1',
    '.onrender.com',  # Allow all Render subdomains during deployment
]

# Site URL for dynamic email links
SITE_URL = os.environ.get('SITE_URL', 'https://naa-portal.onrender.com')

# ============================================================================
# INSTALLED APPS
# ============================================================================

INSTALLED_APPS = [
    # Custom apps FIRST
    'accounts.apps.AccountsConfig',
    
    # Django contrib apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third-party apps
    'csp',
    'cloudinary',
    'cloudinary_storage',
    'rest_framework',
    'django_ckeditor_5',
]

# ============================================================================
# MIDDLEWARE
# ============================================================================

MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================================
# URL CONFIGURATION
# ============================================================================

ROOT_URLCONF = 'naa_site.urls'

# ============================================================================
# TEMPLATES
# ============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'naa_site.wsgi.application'

# ============================================================================
# DATABASE
# ============================================================================

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ============================================================================
# AUTHENTICATION
# ============================================================================

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ============================================================================

STATIC_URL = '/static/'

# CRITICAL FIX: Point to the correct directory
# Your structure is: naa-portal/static/assets/...
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # This is correct for your structure
]

# Where collectstatic will copy files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration for production

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ============================================================================
# MEDIA FILES (User Uploads)
# ============================================================================

MEDIA_URL = '/media/'

# Cloudinary for production, local folder for development
if os.environ.get("CLOUDINARY_URL"):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    CLOUDINARY_STORAGE = {
        'CLOUDINARY_URL': os.environ.get("CLOUDINARY_URL"),
    }
else:
    MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

if os.environ.get("SENDGRID_API_KEY"):
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    SENDGRID_SANDBOX_MODE_IN_DEBUG = False
else:
    # Development: print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'nigerianacademyofaudiology@gmail.com'
)

# ============================================================================
# CKEDITOR CONFIGURATION
# ============================================================================

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 
            'bold', 'italic', 'link',
            'bulletedList', 'numberedList', 
            'blockQuote', 'imageUpload',
        ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|', 'bulletedList', 'numberedList',
            '|', 'blockQuote',
        ],
        'toolbar': [
            'heading', '|', 'outdent', 'indent', '|', 
            'bold', 'italic', 'link', 'underline', 'strikethrough',
            'code', 'subscript', 'superscript', 'highlight', '|', 
            'codeBlock', 'sourceEditing', 'insertImage',
            'bulletedList', 'numberedList', 'todoList', '|',  
            'blockQuote', 'imageUpload', '|',
            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 
            'mediaEmbed', 'removeFormat', 'insertTable',
        ],
        'image': {
            'toolbar': [
                'imageTextAlternative', '|', 
                'imageStyle:alignLeft', 'imageStyle:alignCenter', 
                'imageStyle:alignRight', 'imageStyle:full', 
                'imageStyle:side', '|'
            ],
            'styles': [
                'full', 'side', 'alignLeft', 'alignCenter', 'alignRight',
            ]
        }
    }
}

# Only use Cloudinary for media when configured (avoid errors when CLOUDINARY_URL is unset)
if os.environ.get("CLOUDINARY_URL"):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    CKEDITOR_5_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# ============================================================================
# PRODUCTION SECURITY SETTINGS
# ============================================================================

if not DEBUG:
    # HTTPS enforcement
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookie security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Changed from Strict for better compatibility
    CSRF_COOKIE_SAMESITE = 'Lax'
    
    # Additional security headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    

# ============================================================================
# CONTENT SECURITY POLICY & PERMISSIONS
# ============================================================================

# -------------------------
# Content Security Policy (django-csp 4.0+ format)
# -------------------------
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'",),
        "style-src": ("'self'", "'unsafe-inline'"),  # unsafe-inline for Django admin
        "img-src": ("'self'", "data:", "https:", "res.cloudinary.com"),
        "font-src": ("'self'",),
        "connect-src": ("'self'",),
        "frame-ancestors": ("'none'",),
        "base-uri": ("'self'",),
        "form-action": ("'self'",),
    }
}

# -------------------------
# Permissions Policy
# -------------------------
# Django 6.0 recognizes SECURE_PERMISSION_POLICY (singular)
SECURE_PERMISSION_POLICY = {
    "geolocation": "()",
    "microphone": "()",
    "camera": "()",
    "payment": "()",
    "usb": "()",
    "fullscreen": "('self')",  # optional, allows fullscreen only from your domain
}



# ============================================================================
# SESSION CONFIGURATION
# ============================================================================

SESSION_COOKIE_AGE = 604800  # 7 days in seconds
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_NAME = 'naa_sessionid'

# ============================================================================
# FILE UPLOAD SECURITY
# ============================================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644

# ============================================================================
# REST FRAMEWORK
# ============================================================================

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/hour',
        'user': '100/hour',
    },
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'  # Nigerian timezone
USE_I18N = True
USE_TZ = True

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'naa_portal.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================================
# ADMIN NOTIFICATIONS
# ============================================================================

ADMINS = [
    ('NAA Admin', os.environ.get('ADMIN_EMAIL', 'nigerianacademyofaudiology@gmail.com')),
]
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ============================================================================
# DJANGO SITES FRAMEWORK
# ============================================================================

SITE_ID = 1

# ============================================================================
# DEFAULT PRIMARY KEY TYPE
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# DEBUGGING HELPERS (Development Only)
# ============================================================================

if DEBUG:
    # Print static files configuration for debugging
    print(f"\n{'='*60}")
    print("STATIC FILES DEBUG INFO:")
    print(f"{'='*60}")
    print(f"DEBUG = {DEBUG}")
    print(f"BASE_DIR = {BASE_DIR}")
    print(f"STATIC_URL = {STATIC_URL}")
    print(f"STATIC_ROOT = {STATIC_ROOT}")
    print(f"STATICFILES_DIRS = {STATICFILES_DIRS}")
    print(f"STATICFILES BACKEND = {STORAGES['staticfiles']['BACKEND']}")
    
    # Check if static directory exists
    static_dir = BASE_DIR / 'static'
    print(f"\nStatic directory exists: {static_dir.exists()}")
    if static_dir.exists():
        print(f"Contents: {list(static_dir.iterdir())}")
    print(f"{'='*60}\n")
    