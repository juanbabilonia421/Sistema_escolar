from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-cambia-esta-clave-en-produccion'

DEBUG = True

ALLOWED_HOSTS = []

# ─── APPS INSTALADAS ───────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    'usuarios',
    'academico',
    'comercial',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sistema_escolar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Carpeta global de templates (opcional pero útil)
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

WSGI_APPLICATION = 'sistema_escolar.wsgi.application'

# ─── BASE DE DATOS MYSQL ────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sistema_escolar',       # Nombre de la BD que creaste
        'USER': 'root',                  # Tu usuario de MySQL
        'PASSWORD': 'juandbm270408',     # Tu contraseña de MySQL
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# ─── MODELO DE USUARIO PERSONALIZADO ───────────────────────
# Esto le dice a Django que use nuestro Usuario en vez del default
AUTH_USER_MODEL = 'usuarios.Usuario'

# ─── INTERNACIONALIZACIÓN ───────────────────────────────────
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ─── ARCHIVOS ESTÁTICOS ─────────────────────────────────────
STATIC_URL = 'static/'
import os
STATICFILES_DIRS = [BASE_DIR / 'static'] if os.path.isdir(BASE_DIR / 'static') else []

# ─── ARCHIVOS MEDIA (entregas de actividades) ───────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── AUTENTICACIÓN ──────────────────────────────────────────
LOGIN_URL = '/usuarios/login/'
LOGIN_REDIRECT_URL = '/usuarios/dashboard/'
LOGOUT_REDIRECT_URL = '/usuarios/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'