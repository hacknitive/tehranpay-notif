import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(DEBUG=(bool, False))

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "otp",
    "drf_yasg",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "otp.middleware.TokenValidationMiddleware",
]

ROOT_URLCONF = "notification_service.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "notification_service.wsgi.application"


# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": env("DB_NAME"),  # If needed
#         "USER": env("DB_USER"),  # If needed
#         "PASSWORD": env("DB_PASSWORD"),  # If needed
#         "HOST": env("DB_HOST"),  # If needed
#         "PORT": env("DB_PORT"),  # If needed
#     }
# }

# Redis Configuration for OTP storage and caching token validation
REDIS_HOST = env("REDIS_HOST")
REDIS_PORT = env("REDIS_PORT")
REDIS_DB = env.int("REDIS_DB")
REDIS_PASSWORD = env("REDIS_PASSWORD")

# JWT Configuration
with open(env("JWT_PUBLIC_KEY_PATH"), "r") as key_file:
    JWT_PUBLIC_KEY = key_file.read()

# OTP TTL Configuration
OTP_TTL_SECONDS = env.int("OTP_TTL_SECONDS", default=300)  # Default 5 minutes

# Token Validation Cache TTL
TOKEN_VALIDATION_CACHE_TTL = env.int(
    "TOKEN_VALIDATION_CACHE_TTL", default=300
)  # 5 minutes

# Celery Configuration
CELERY_BROKER_URL = env("CELERY_BROKER_URL")  # e.g., 'amqp://localhost'
CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND", default="rpc://"
)  # Or 'redis://localhost:6379/0'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = f"{BASE_DIR}/staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
}


TOKEN_VALIDATION_URL = env('TOKEN_VALIDATION_URL')


# Swagger Configuration
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}