# chat/views.py
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from userapp.models import User
from chatsapp.models import Room
from ..serializers import RoomSerializer
import json
import redis
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings

# Initialize Redis connection
redis_instance = redis.Redis(**settings.REDIS_CONFIG)


@api_view(['GET'])
def user_rooms(request, enrollmentNo):
    """Fetch all rooms for a specific user."""
    try:
        user = User.objects.get(enrollmentNo=enrollmentNo)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    rooms = Room.objects.filter(participants=user)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["GET"])
def get_chat_messages(request, room):
    """Get chat messages for a specific room."""
    messages = redis_instance.lrange(room, 0, -1)
    
    # If no messages are found, return an empty array instead of a 404.
    if messages:
        return JsonResponse({
            'room': room,
            'messages': [json.loads(m.decode('utf-8')) for m in reversed(messages)]
        })
    
    # Return an empty list for the messages if no messages exist yet.
    return JsonResponse({
        'room': room,
        'messages': []
    }, status=200)

@require_http_methods(["DELETE"])
@csrf_exempt
def delete_all_messages(request, room):
    """Delete all messages in a specific room."""
    if redis_instance.exists(room):
        redis_instance.delete(room)

        # Notify all users in the room about message deletion
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{room}',
            {
                'type': 'delete_messages_event',
                'message': 'All messages have been deleted'
            }
        )

        return JsonResponse({'message': f'All messages in room "{room}" have been deleted successfully'})
    return HttpResponseNotFound(f'Room "{room}" not found')

@require_http_methods(["GET"])
def get_latest_messages(request, room, count=10):
    """Get the latest N messages for a specific room."""
    messages = redis_instance.lrange(room, 0, count - 1)
    if messages:
        return JsonResponse({
            'room': room,
            'messages': [json.loads(m.decode('utf-8')) for m in messages]
        })
    return JsonResponse({'message': 'No messages found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def store_chat_message(request):
    """Store a chat message."""
    try:
        data = json.loads(request.body)
        room = data.get('room')
        enrollmentNo = data.get('enrollmentNo')
        body = data.get('body')

        if room and enrollmentNo and body:
            message = {
                'user': enrollmentNo,
                'body': body,
                'timestamp': time.time()
            }
            redis_instance.lpush(room, json.dumps(message))
            return JsonResponse({'message': 'Message stored successfully'})
        return HttpResponseBadRequest('Invalid data. Provide room, enrollmentNo, and body.')
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON format')

@csrf_exempt
@require_http_methods(["POST"])
def schedule_chat_message(request):
    """Schedule a chat message to be sent later."""
    try:
        data = json.loads(request.body)
        room = data.get('room')
        enrollmentNo = data.get('enrollmentNo')
        message = data.get('message')

        if room and enrollmentNo and message:
            # Schedule the message to be sent after a delay (e.g., 10 seconds)
            # schedule_message.delay(room, enrollmentNo, message)
            return JsonResponse({'message': 'Message scheduled successfully'})
        return HttpResponseBadRequest('Invalid data. Provide room, enrollmentNo, and message.')
    
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON format')
