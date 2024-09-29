# chat/urls.py
from django.urls import path
from ..views import groupchat_views

urlpatterns = [
    path('newproject/room/', groupchat_views.create_room, name='create_new_room'),
]
