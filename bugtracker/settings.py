import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from datetime import timedelta


# Load .env file and fail if not found
env_file = find_dotenv()
if not env_file:
    raise FileNotFoundError(".env file not found.")
load_dotenv(env_file)

# === Required env fetcher ===
def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"❌ Required environment variable '{name}' not set.")
    return value

BASE_DIR = Path(__file__).resolve().parent.parent

# ========== LOG FILE ==========
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = 'bugtracker.log'

# ========== Security ==========
SECRET_KEY = get_env_var('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']


# ========== Installed Apps ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'channels',
    'channels_redis',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'tracker'
]

# ========== Middleware ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bugtracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bugtracker.wsgi.application'
ASGI_APPLICATION = 'bugtracker.asgi.application'


# ========== Database ==========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ========== Redis Channel Layer ==========
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}


# ========== REST Framework ==========
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}


# ========== JWT Settings ==========
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(get_env_var('ACCESS_TOKEN_LIFETIME_IN_MIN'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(get_env_var('REFRESH_TOKEN_LIFETIME_IN_DAYS'))),
    'ROTATE_REFRESH_TOKENS': True,
}


# ========== CORS ==========
CORS_ALLOW_ALL_ORIGINS = True


# ========== Password Validators ==========
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


# ========== Time & Locale ==========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = False


# ========== Static Files ==========/
STATIC_URL = 'static/'


# ========== Default Auto Field ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
