from django.urls import path, re_path

from ..consumers.dm_consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"^ws/(?P<enrollmentNo1>[\w@.-]+)/(?P<enrollmentNo2>[\w@.-]+)/$", ChatConsumer.as_asgi()),
]
