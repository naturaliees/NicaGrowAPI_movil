import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient

ROOT = Path(__file__).resolve().parent.parent

class ProductionSettingsTests(SimpleTestCase):
    def production_env(self):
        env = os.environ.copy()
        for key in ('DJANGO_SETTINGS_MODULE', 'DB_PYTHON_DRIVER', 'DJANGO_ALLOWED_HOSTS'):
            env.pop(key, None)
        env.update({
            'APP_ENV': 'production', 'WEBSITE_HOSTNAME': 'nicagrow-test.azurewebsites.net',
            'DJANGO_SECRET_KEY': 'strong-test-secret-' * 5,
            'API_KEY': 'strong-integration-key-' * 4,
            'DB_HOST': 'example.database.windows.net', 'DB_PORT': '1433',
            'DB_NAME': 'nicagrow_dw', 'DB_USER': 'test-user', 'DB_PASSWORD': 'test-password',
            'DJANGO_DEBUG': 'true', 'DB_EXTRA_PARAMS': 'Encrypt=no;TrustServerCertificate=yes',
        })
        return env

    def run_python(self, code, env):
        return subprocess.run([sys.executable, '-c', code], cwd=ROOT, env=env,
                              capture_output=True, text=True, timeout=30)

    def test_secure_azure_defaults_and_driver(self):
        result = self.run_python("from config import settings as s; assert not s.DEBUG; assert s.SECURE_SSL_REDIRECT; assert s.SECURE_PROXY_SSL_HEADER == ('HTTP_X_FORWARDED_PROTO','https'); assert s.ALLOWED_HOSTS == ['nicagrow-test.azurewebsites.net']; assert s.DATABASES['default']['OPTIONS']['python_driver'] == 'mssql_python'; assert s.DATABASES['default']['OPTIONS']['extra_params'] == 'Encrypt=yes;TrustServerCertificate=no'", self.production_env())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_secret_does_not_fall_back_to_local_dotenv(self):
        env = self.production_env(); env.pop('API_KEY')
        result = self.run_python('import config.settings', env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ImproperlyConfigured', result.stderr)

    def test_production_checks_pass_without_connecting_to_database(self):
        env = self.production_env()
        result = subprocess.run([sys.executable, 'manage.py', 'check', '--deploy', '--fail-level', 'WARNING'], cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @override_settings(ALLOWED_HOSTS=['testserver'], SECURE_SSL_REDIRECT=True)
    @patch('api.views.connection')
    def test_public_liveness_does_not_query_database(self, db):
        response = APIClient().get('/healthz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'estado': 'activo'})
        db.cursor.assert_not_called()

    @override_settings(ALLOWED_HOSTS=['testserver'], SECURE_SSL_REDIRECT=True)
    def test_api_redirects_http_and_requires_key_over_https(self):
        client = APIClient()
        self.assertEqual(client.get('/api/productos/').status_code, 301)
        self.assertEqual(client.get('/api/productos/', secure=True).status_code, 401)
