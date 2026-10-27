from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
class IntegrationUser:
    is_authenticated = True
class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        supplied = request.headers.get('X-Api-Key', '')
        if not supplied or not constant_time_compare(supplied, settings.API_KEY):
            raise AuthenticationFailed('X-Api-Key ausente o inválida.')
        return IntegrationUser(), None
    def authenticate_header(self, request):
        return 'ApiKey'
