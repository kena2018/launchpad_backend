from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class DefaultTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            raise AuthenticationFailed('Authorization header is missing')

        auth_token = auth_header.split(' ')[1] if auth_header.startswith('Token ') else None
        print(settings.DEFAULT_AUTH_TOKEN)
        if auth_token == settings.DEFAULT_AUTH_TOKEN:
            print("Token allowed")
            return None, None  # authentication successful
        else:
            raise AuthenticationFailed('Invalid token')