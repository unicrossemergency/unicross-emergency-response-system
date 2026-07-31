"""
ASGI config for emergency project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

print("🚀🚀🚀 ASGI IS RUNNING 🚀🚀🚀")

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import incident.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            incident.routing.websocket_urlpatterns
        )
    ),
})