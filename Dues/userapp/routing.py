# routing.py
from django.urls import re_path 
from userapp.consumers import UserActivityConsumer

websocket_urlpatterns = [
    re_path(r"^status/ws/status/(?P<enrollmentNo>[\w@.-]+)/$", UserActivityConsumer.as_asgi()),
]
