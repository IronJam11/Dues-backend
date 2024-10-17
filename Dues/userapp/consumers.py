import json
from channels.generic.websocket import WebsocketConsumer
from userapp.models import User, UserActivity
from asgiref.sync import async_to_sync

class UserActivityConsumer(WebsocketConsumer):
    def connect(self):
        # Extract the enrollmentNo from the frontend message (passed in the URL)
        self.enrollmentNo = self.scope['url_route']['kwargs']['enrollmentNo']
        print("HELLO")
        print(self.enrollmentNo)

        # Fetch the user and update their status to "Online"
        user = User.objects.get(enrollmentNo=self.enrollmentNo)
        user_activity, _ = UserActivity.objects.get_or_create(user=user)
        user_activity.status = "Online"
        user_activity.save()

        # Add the user to a group to track their activity
        async_to_sync(self.channel_layer.group_add)(
            "user_activity_group",  # Group name for all users
            self.channel_name
        )
        
        self.accept()

        # Send initial status to the frontend
        self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': 'Online',
            'enrollmentNo': user.enrollmentNo,
        }))

        # Broadcast to others that this user is now online
        async_to_sync(self.channel_layer.group_send)(
            "user_activity_group",
            {
                "type": "status_update",
                "status": "Online",
                "enrollmentNo": user.enrollmentNo,
            }
        )

    def disconnect(self, close_code):
        # Mark the user as "Offline" when they disconnect
        user = User.objects.get(enrollmentNo=self.enrollmentNo)
        user_activity = UserActivity.objects.get(user=user)
        
        user_activity.status = "Offline"
        user_activity.save()

        # Remove the user from the group
        async_to_sync(self.channel_layer.group_discard)(
            "user_activity_group",
            self.channel_name
        )

        # Broadcast to others that this user is now offline
        async_to_sync(self.channel_layer.group_send)(
            "user_activity_group",
            {
                "type": "status_update",
                "status": "Offline",
                "enrollmentNo": user.enrollmentNo,
            }
        )

    def receive(self, text_data):
        # Handle incoming messages if necessary
        pass

    # Method to handle status updates from the group and send them to the WebSocket
    def status_update(self, event):
        # Send the updated status and enrollmentNo to the WebSocket
        print("event",event)
        self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status'],
            'enrollmentNo': event['enrollmentNo'],
        }))
