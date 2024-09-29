from django.utils import timezone
from userapp.models import User
from chatsapp.models import Room
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def create_room(request):
    try:
        # Extract data from the request
        room_name = request.data.get('room_name')
        participant_emails = request.data.get('participant_emails', [])
        admin_enrollmentNos = request.data.get('admin_enrollmentNos')
        late_joiner_emails = request.data.get('late_joiner_emails', [])
        room_type = request.data.get('type')

        # Debugging output
        print(f"Room Name: {room_name}")
        print(f"Admin EnrollmentNo: {admin_enrollmentNos}")
        print(f"Participants: {participant_emails}")
        print(f"Late Joiners: {late_joiner_emails}")
        print(f"Room Type: {room_type}")

        # Ensure room name and type are present
        if not room_name or not room_type:
            return Response({"error": "Room name and type are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the admin user (ensure it's fetched correctly)
        admin = User.objects.get(enrollmentNo=admin_enrollmentNos)
        if not admin:
            return Response({"error": "Admin user not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Get participants and late joiners from emails
        participants = User.objects.filter(email__in=participant_emails)
        late_joiners = User.objects.filter(email__in=late_joiner_emails)

        # Ensure at least one participant is present
        if not participants.exists():
            return Response({"error": "At least one valid participant is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the room
        room = Room.objects.create(
            room_name=room_name,
            time_created=timezone.now(),
            type=room_type,
            slug = room_name,
        )

        # Add participants, admin, and late joiners
        room.participants.set(participants)
        room.admins.set([admin])  # Add admin
        room.late_joiners.set(late_joiners)

        room.save()

        return Response({'message': 'Room created successfully!', 'slug': room.slug}, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response({"error": "Admin user not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
