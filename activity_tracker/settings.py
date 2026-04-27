import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 SECURITY
SECRET_KEY = 'django-insecure-xxxxxxxxxxxxxxxxxxxxxxxx'
DEBUG = True
ALLOWED_HOSTS = []

# 🔹 APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'tracker',
    'captcha',
]

# 🔹 MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'activity_tracker.urls'

# 🔹 TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ OK
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tracker.context_processors.user_profile',
            ],
        },
    },
]

WSGI_APPLICATION = 'activity_tracker.wsgi.application'

# 🔹 DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 🔹 PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🔹 INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'   # ✅ better for you
USE_I18N = True
USE_TZ = True

# 🔹 STATIC FILES
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "tracker" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# 🔹 MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 🔹 LOGIN SETTINGS
LOGIN_URL = 'home'
LOGIN_REDIRECT_URL = 'student_dashboard'
LOGOUT_REDIRECT_URL = 'home'

# =========================================================
# 🔥 EMAIL CONFIG (CHOOSE ONE ONLY)
# =========================================================

# ✅ OPTION 1: DEVELOPMENT (NO REAL EMAIL, PRINTS IN TERMINAL)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ✅ OPTION 2: REAL EMAIL (GMAIL SMTP)  ← USE THIS FOR OTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'harshamass2007@gmail.com'
EMAIL_HOST_PASSWORD = 'mcabffslxuffnvyr'  # 🔑 NOT normal password

# Optional
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 🔹 DEFAULT PK
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FAST2SMS_API_KEY = "YOUR_API_KEY_HERE"