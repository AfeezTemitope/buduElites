import os
import logging
from urllib.parse import parse_qs
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from content_hub.routing import websocket_urlpatterns

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'befa.settings')


class JWTMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        token = None

        # Check for token in Authorization header
        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        # Check for token in query string
        elif scope.get('query_string', b''):
            query_string = scope['query_string'].decode()
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]  # Get first 'token' value if present

        if token:
            try:
                user = await self.get_user_from_token(token)
                scope['user'] = user
            except Exception as e:
                logger.error(f"JWT authentication error: {str(e)}")
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        token_obj = AccessToken(token)
        user_id = token_obj['user_id']
        from users.models import User
        return User.objects.get(id=user_id)


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JWTMiddleware(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})