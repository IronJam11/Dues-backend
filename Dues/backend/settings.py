"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta 
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
from corsheaders.defaults import default_headers


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-m2+6t)709944ferjmg2n)4c4+y87(+rvf01o(r=6(rgo2s2miu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'channels',
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt.token_blacklist',

    # 'allauth',
    # 'allauth.account',
    # 'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google'

    'rest_framework',
    'corsheaders',

    'userapp',
    'tagsapp',
    'assignmentsapp',
    'projectapp',
    'chatsapp',
    'ideasapp',
    'notificationsapp',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'channels.middleware.SessionMiddlewareStack',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'
AUTH_USER_MODEL = 'userapp.User'
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

REDIS_CONFIG = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_DB,
}

DATABASES ={
    'default' : 
    {
        "ENGINE" : "django.db.backends.postgresql",
        "NAME" : 'sunflower',
        "USER": 'postgres',
        "PASSWORD":'Barkha12345',
        "HOST":"127.0.0.1",
        "PORT":"5432",
    }
}
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
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Set your access token lifetime
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # Set your refresh token lifetime
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

REST_FRAMEWORK = {
    
    'DEFAULT_AUTHENTICATION_CLASSES': (
        
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
  
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MEDIA_ROOT = os.path.join(BASE_DIR,'media')
MEDIA_URL = '/media/'


# corsheaders 
CORS_ALLOW_METHODS = [
    "DELETE",  
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5174',  # Your frontend URL
    'http://127.0.0.1:5174',
]
CORS_ALLOW_HEADERS = list(default_headers) + [
    'Authorization1',
    'Authorization2'
]
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',
#     'allauth.account.auth_backends.AuthenticationBackend'
# ]

# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'SCOPE' : [
#             'profile',
#             'email'
#         ],
#         'APP': {
#             'client_id': os.environ['CLIENT_ID'],
#             'secret': os.environ['CLIENT_SECRET'],
#         },
#         'AUTH_PARAMS': {
#             'access_type':'online',
#         }
#     }
# }
# SITE_ID = 2

# LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = '/'
# AIzaSyCxsGfZ3zTEb9ySrrrdO7zh1A1Zk96dobc

ACCOUNT_EMAIL_VERIFICATION = "none"

SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True  # Ensure this is set for production
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True  # Ensure this is set for production


CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]