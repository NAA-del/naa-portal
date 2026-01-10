"""
Django settings for naa_site project.
Integrated with Cloudinary for Media and WhiteNoise for Static files.
"""

import os
import dj_database_url
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key')

# Set DEBUG to False by default on Render, True locally
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['naa-portal.onrender.com', 'localhost', '127.0.0.1']

# --- CLOUDINARY CONFIGURATION (BEST PRACTICE) ---
# Uses the single CLOUDINARY_URL environment variable from your dashboard
CLOUDINARY_STORAGE = {
    'CLOUDINARY_URL': os.environ.get("CLOUDINARY_URL"),
}

# Application definition
INSTALLED_APPS = [
    # Cloudinary storage MUST be before django.contrib.staticfiles
    'accounts.apps.AccountsConfig',
    'cloudinary_storage',
    'cloudinary',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Essential for serving static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'naa_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Allows for a global templates folder
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

# Database
# Uses PostgreSQL on Render via DATABASE_URL, fallback to SQLite locally
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES (CSS, JS, Medicio Assets) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# High-performance static serving for Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- MEDIA FILES (Images, Documents, Photos) ---
MEDIA_URL = '/media/' 

# Use Cloudinary if the URL is set (Production/Render), otherwise use Local Media
if os.environ.get("CLOUDINARY_URL"):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # Local development fallback
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# --- AUTHENTICATION REDIRECTS ---
# Fixed to point to your URL names to avoid 404/Accounts/Login errors
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- EMAIL CONFIGURATION ---
# Prints emails to terminal/logs (Set to SMTP for live deployment)
# Use SMTP for sending actual emails
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
DEFAULT_FROM_EMAIL = 'nigerianacademyofaudiology@gmail.com' # Must be the one you verify in SendGrid