from django.shortcuts import get_object_or_404
from userapp.models import User
from chatsapp.models import Room

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from redis import Redis

redis_instance = Redis()

@require_http_methods(["GET"])
def get_user_rooms_sorted_by_recent_message(request, enrollment_no):
    """Fetch rooms for a user and sort by the most recent message."""
    # Fetch the user using enrollmentNo
    user = get_object_or_404(User, enrollmentNo=enrollment_no)
    
    # Fetch rooms where the user is a participant
    user_rooms = Room.objects.filter(participants=user)
    
    rooms_with_messages = []

    for room in user_rooms:
        # Fetch the most recent message for each room from Redis
        messages = redis_instance.lrange(room.slug, 0, -1)

        # Get the timestamp of the most recent message (if it exists)
        if messages:
            recent_message = json.loads(messages[-1].decode('utf-8'))
            recent_message_time = recent_message.get('timestamp')  # Ensure your messages have a timestamp field
        else:
            recent_message_time = None
        
        # Append room with the most recent message and timestamp
        rooms_with_messages.append({
            'room_name': room.room_name,
            'slug': room.slug,
            # 'type': room.get_type_display(),
            'participants': [participant.email for participant in room.participants.all()],
            'recent_message': recent_message if messages else None,
            'recent_message_time': recent_message_time
        })
    
    # Sort rooms by the recent message timestamp in descending order (most recent first)
    sorted_rooms = sorted(
        rooms_with_messages,
        key=lambda room: room['recent_message_time'] or 0,
        reverse=True
    )
    
    # Return the sorted rooms
    return JsonResponse({'rooms': sorted_rooms}, status=200)

@require_http_methods(["GET"])
def user_rooms_view(request, enrollmentNo):
    """A wrapper view that calls the get_user_rooms_sorted_by_recent_message function."""
    return get_user_rooms_sorted_by_recent_message(request, enrollmentNo)
