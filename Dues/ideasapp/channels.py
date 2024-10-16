import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Idea, Vote
from userapp.models import User

class IdeaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the "ideas_group" to listen for broadcasts
        await self.channel_layer.group_add(
            'ideas_group',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the "ideas_group" when the WebSocket connection is closed
        await self.channel_layer.group_discard(
            'ideas_group',
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming messages from WebSocket
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        unique_name = text_data_json.get('unique_name')
        enrollmentNo = text_data_json.get('enrollmentNo')

        if message_type == 'vote':
            vote_type = text_data_json.get('vote')
            await self.handle_vote(unique_name, enrollmentNo, vote_type)

    async def handle_vote(self, unique_name, enrollmentNo, vote_type):
        try:
            # Fetch the Idea object asynchronously
            idea = await Idea.objects.aget(unique_name=unique_name)
            user = await User.objects.aget(enrollmentNo=enrollmentNo)

            # Fetch or create the Vote object asynchronously
            vote, created = await Vote.objects.aget_or_create(user=user, idea=idea)

            if not created:
                # User already voted, update vote type
                if vote.vote_type == 'for' and vote_type == 'against':
                    idea.for_votes -= 1
                    idea.against_votes += 1
                    vote.vote_type = 'against'
                elif vote.vote_type == 'against' and vote_type == 'for':
                    idea.against_votes -= 1
                    idea.for_votes += 1
                    vote.vote_type = 'for'
            else:
                # First-time vote
                if vote_type == 'for':
                    idea.for_votes += 1
                    vote.vote_type = 'for'
                elif vote_type == 'against':
                    idea.against_votes += 1
                    vote.vote_type = 'against'

            # Save the vote and idea asynchronously
            await vote.asave()
            await idea.asave()

            # Broadcast the updated vote counts asynchronously
            await self.channel_layer.group_send(
                'ideas_group',
                {
                    'type': 'vote_update',
                    'unique_name': unique_name,
                    'for_votes': idea.for_votes,
                    'against_votes': idea.against_votes,
                }
            )

        except Idea.DoesNotExist:
            # Handle the case where the idea does not exist
            await self.send(text_data=json.dumps({
                'error': 'Idea does not exist'
            }))
        except User.DoesNotExist:
            await self.send(text_data=json.dumps({
                'error': 'User does not exist'
            }))
        except Exception as e:
            print(f"An error occurred: {e}")
            await self.send(text_data=json.dumps({
                'error': 'An unexpected error occurred'
            }))

    async def vote_update(self, event):
        # Send the updated vote counts to the WebSocket asynchronously
        await self.send(text_data=json.dumps({
            'type': 'vote_update',
            'unique_name': event['unique_name'],
            'for_votes': event['for_votes'],
            'against_votes': event['against_votes'],
        }))
