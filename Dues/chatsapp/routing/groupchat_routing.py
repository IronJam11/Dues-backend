from django.urls import path, re_path

from ..consumers.groupchat_consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"^ws/group/(?P<room>[\w@.:+-]+)/(?P<enrollmentNo>[\w@.-]+)/$", ChatConsumer.as_asgi())

]
