# chat/urls.py
from django.urls import path
from ..views.chatrooms import user_rooms_view

urlpatterns = [
    # path('create-room/', dm_views.create_room, name='create_room'),
    # path('rooms/<int:enrollmentNo>/', dm_views.user_rooms, name='user_rooms'),
    path('user-rooms/<str:enrollmentNo>/',user_rooms_view, name='get_users_rooms'),
   
    # path('schedule-message/', dm_views.schedule_chat_message, name='schedule_chat_message'),
]
