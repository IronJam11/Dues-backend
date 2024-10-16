# routing.py
from django.urls import re_path
from ideasapp.channels import IdeaConsumer # Import your IdeaConsumer

websocket_urlpatterns = [
    re_path(r'ws/ideas/$', IdeaConsumer.as_asgi()),  # WebSocket URL for the ideas
]
