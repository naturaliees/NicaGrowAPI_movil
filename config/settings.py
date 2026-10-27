import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
IS_PRODUCTION = bool(os.getenv('WEBSITE_HOSTNAME')) or os.getenv('APP_ENV', '').lower() == 'production'
# In Azure, secrets come only from App Service environment variables.
if not IS_PRODUCTION:
    load_dotenv(BASE_DIR / '.env')
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')
API_KEY = os.getenv('API_KEY', '')
if not SECRET_KEY or not API_KEY:
    raise ImproperlyConfigured('Configura DJANGO_SECRET_KEY y API_KEY en las variables de entorno o .env local.')
if IS_PRODUCTION and (len(SECRET_KEY) < 32 or len(API_KEY) < 32):
    raise ImproperlyConfigured('En producción los dos secretos deben tener al menos 32 caracteres.')
DEBUG = False if IS_PRODUCTION else os.getenv('DJANGO_DEBUG', 'false').lower() == 'true'
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '' if IS_PRODUCTION else 'localhost,127.0.0.1').split(',') if h.strip()]
if os.getenv('WEBSITE_HOSTNAME'):
    ALLOWED_HOSTS.append(os.environ['WEBSITE_HOSTNAME'])
if IS_PRODUCTION and (not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS):
    raise ImproperlyConfigured('Configura un dominio permitido concreto para producción.')
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
INSTALLED_APPS = ['rest_framework', 'api']
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
DB_OPTIONS = {
    'driver': os.getenv('DB_DRIVER', 'ODBC Driver 18 for SQL Server'),
    'extra_params': os.getenv('DB_EXTRA_PARAMS', 'Encrypt=yes;TrustServerCertificate=no'),
    'connection_timeout': 8,
    'connection_retries': 1,
    'query_timeout': 30,
}
DB_PYTHON_DRIVER = os.getenv('DB_PYTHON_DRIVER', 'mssql_python' if IS_PRODUCTION else 'pyodbc')
if DB_PYTHON_DRIVER not in ('pyodbc', 'mssql_python'):
    raise ImproperlyConfigured('DB_PYTHON_DRIVER debe ser pyodbc o mssql_python.')
if DB_PYTHON_DRIVER == 'mssql_python':
    DB_OPTIONS['python_driver'] = 'mssql_python'
    DB_OPTIONS.pop('driver')
if IS_PRODUCTION:
    for variable in ('DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'):
        if not os.getenv(variable):
            raise ImproperlyConfigured('Falta configurar ' + variable + ' en Azure.')
    # Fixed TLS options prevent carrying local self-signed settings into production.
    DB_OPTIONS['extra_params'] = 'Encrypt=yes;TrustServerCertificate=no'
DATABASES = {'default': {
    'ENGINE': 'mssql', 'NAME': os.getenv('DB_NAME', ''),
    'HOST': os.getenv('DB_HOST', 'localhost'), 'PORT': os.getenv('DB_PORT', '1433' if IS_PRODUCTION else ''),
    'USER': os.getenv('DB_USER', ''), 'PASSWORD': os.getenv('DB_PASSWORD', ''),
    'CONN_MAX_AGE': 60 if IS_PRODUCTION else 0,
    'CONN_HEALTH_CHECKS': True,
    'OPTIONS': DB_OPTIONS,
}}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['api.authentication.ApiKeyAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'UNAUTHENTICATED_USER': None,
    'DEFAULT_RENDERER_CLASSES': ['api.renderers.ExactJSONRenderer'],
    'EXCEPTION_HANDLER': 'api.exceptions.exception_handler',
    'COERCE_DECIMAL_TO_STRING': True,
}
USE_TZ = True
TIME_ZONE = 'America/Managua'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SECURE_SSL_REDIRECT = IS_PRODUCTION
SECURE_HSTS_SECONDS = 31536000 if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
SECURE_HSTS_PRELOAD = IS_PRODUCTION
# App Service terminates TLS and sets this header at the trusted reverse proxy.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if IS_PRODUCTION else None
SECURE_REDIRECT_EXEMPT = [r'^healthz/$']
