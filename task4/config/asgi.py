import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

from calls.routing import websocket_urlpatterns as calls_ws  # noqa: E402
from chat.routing import websocket_urlpatterns as chat_ws  # noqa: E402
from whiteboard.routing import websocket_urlpatterns as whiteboard_ws  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(chat_ws + calls_ws + whiteboard_ws)
            )
        ),
    }
)
