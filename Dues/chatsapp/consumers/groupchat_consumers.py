import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from asgiref.sync import sync_to_async
from userapp.models import User
import time
import redis

redis_instance = redis.Redis(**settings.REDIS_CONFIG)

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room']
        self.enrollmentNo = self.scope['url_route']['kwargs']['enrollmentNo']
        # self.enrollmentNo2 = self.scope['url_route']['kwargs']['enrollmentNo2']
        print("hello")

        # Ensure enrollment numbers are in a consistent order (sorted)

        # Create the room name by joining the sorted enrollment numbers
        self.room_group_name = f'chat_{self.room_name}'

        print(f"Connecting to room: {self.room_group_name}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"Connected to room: {self.room_group_name}")

    async def disconnect(self, close_code):
        print(f"Disconnecting from room: {self.room_group_name}, Close code: {close_code}")
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            room = self.room_name
            enrollmentNo = self.enrollmentNo

            print(f"Received message: {message} from user: {enrollmentNo} in room: {room}")

            # Save the message to the database
            await self.save_message(enrollmentNo, room, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'enrollmentNo': enrollmentNo,
                    'user':enrollmentNo,
                }
            )
        except Exception as e:
            print(f"Error receiving message: {str(e)}")

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        enrollmentNo = event['enrollmentNo']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'enrollmentNo': enrollmentNo,
            'user':enrollmentNo
        }))
        print(f"Sent message: {message} to WebSocket for user: {enrollmentNo}")

    # Handle message deletion event
    async def delete_messages_event(self, event):
        # Notify WebSocket clients that all messages have been deleted
        await self.send(text_data=json.dumps({
            'action': 'delete_messages',
            'message': 'All messages in the room have been deleted'
        }))
        print(f"Notified users about message deletion in room: {self.room_group_name}")

    @sync_to_async
    def save_message(self, enrollmentNo, room, content):
        try:
            # Check if user exists, catch User.DoesNotExist
            user = User.objects.get(enrollmentNo=int(enrollmentNo))
            
            # Store message in Redis
            print(enrollmentNo)
            message = {
                'user': enrollmentNo,  # Use username or another identifying field
                'content': content,
                'timestamp': time.time()
            }
            redis_instance.lpush(room, json.dumps(message))

            return JsonResponse({'message': 'Message stored successfully'})
        
        except User.DoesNotExist:
            print(f"User does not exist: {enrollmentNo}")
            return HttpResponseBadRequest('User does not exist!')
        
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON format')
        
        except Exception as e:
            print(f"Error saving message: {str(e)}")
            return HttpResponseBadRequest('Error saving message')
