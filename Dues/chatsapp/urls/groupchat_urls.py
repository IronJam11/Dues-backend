# chat/urls.py
from django.urls import path
from ..views import room_views
from ..views.groupchat_views import store_chat_message, get_chat_messages, get_latest_messages, delete_all_messages

urlpatterns = [
    path('newproject/room/', room_views.create_room, name='create_new_room'),
    path('store/',store_chat_message, name='store_chat_message'),
    path('get/room-messages/<str:room>/', get_chat_messages, name='get_chat_messages'),
    path('latest/<str:room>/<int:count>/', get_latest_messages, name='get_latest_messages'),
    path('delete/<str:room>/',delete_all_messages, name="delete-messages"),
    path('get/room-details/<str:slug>/',room_views.room_details,name="get_room_details"),
    path('remove-user/',room_views.remove_user_from_room, name="remove_user_from_chat"),
    path('add-admin/',room_views.promote_user_to_admin,name="add_admin"),
    path('add-participants/', room_views.add_participants_to_room,name="add_participants"),
    path('isAdmin/',room_views.isRoomAdmin,name="is_room_admin"),


]
