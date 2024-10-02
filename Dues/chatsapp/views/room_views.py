from django.utils import timezone
from userapp.models import User
from chatsapp.models import Room
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from projectapp.models import Project

@api_view(['POST'])
def isRoomAdmin(request):
    slug = request.data.get('slug')
    room = Room.objects.get(slug=slug)
    enrollmentNo = request.data.get('enrollmentNo')
    user = User.objects.get(enrollmentNo = enrollmentNo)
    if user in room.admins.all():
        return JsonResponse({"isAdmin":"true"})
    else:
        return JsonResponse({"isAdmin":"false"})

@api_view(['POST'])
def create_room(request):
    try:
        # Extract data from the request
        room_name = request.data.get('room_name')
        participant_emails = request.data.get('participant_emails', [])
        admin_enrollmentNos = request.data.get('admin_enrollmentNos')
        late_joiner_emails = request.data.get('late_joiner_emails', [])
        room_type = request.data.get('type')
        slug  = request.data.get('slug')


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
            slug = slug,
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


@api_view(['GET'])
def room_details(request, slug):
    # Retrieve the room based on the slug
    room = get_object_or_404(Room, slug=slug)
    
    # Prepare the room details to return
    room_data = {
        'room_name': room.room_name,
        'type': room.type,
        'participants': list(room.participants.values('id', 'email', 'enrollmentNo')),
        'admins': list(room.admins.values('id', 'email', 'enrollmentNo')),
        'late_joiners': list(room.late_joiners.values('id', 'email', 'enrollmentNo')),
        'time_created': room.time_created,
        'slug': room.slug,
    }

    # Return room details as JSON
    return JsonResponse(room_data)


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from userapp.models import User
from chatsapp.models import Room

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from userapp.models import User
from chatsapp.models import Room
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from userapp.models import User
from chatsapp.models import Room
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view

@api_view(["POST"])
def remove_user_from_room(request):
    """
    Remove a user from a room based on the room slug and user's email.
    The initiator is identified by enrollmentNo and must be an admin.
    The target user is removed from participants, late_joiners, and admins.
    """
    try:
        # Extract enrollmentNo of the initiator and email of the target user from the POST request data
        initiator_enrollment_no = request.data.get('enrollmentNo')
        target_email = request.data.get('email')
        room_slug = request.data.get('slug')

        # Validate required fields
        if not initiator_enrollment_no:
            return JsonResponse({'error': 'Initiator enrollmentNo is required.'}, status=400)

        if not target_email:
            return JsonResponse({'error': 'Target user email is required.'}, status=400)

        # Get the room by its slug
        room = get_object_or_404(Room, slug=room_slug)

        # Get the initiator by enrollmentNo
        initiator = get_object_or_404(User, enrollmentNo=initiator_enrollment_no)
        print(initiator.enrollmentNo)

        # Check if the initiator is an admin of the room
        if initiator not in room.admins.all():
            return JsonResponse({'error': 'You do not have permission to remove users from this room as you are not an admin.'}, status=403)

        # Get the target user by email
        target_user = get_object_or_404(User, email=target_email)

        # Remove the target user from participants, late_joiners, and admins if they exist
        removed_from = []
        if target_user in room.participants.all():
            room.participants.remove(target_user)
            removed_from.append('participants')

        if target_user in room.late_joiners.all():
            room.late_joiners.remove(target_user)
            removed_from.append('late_joiners')

        if target_user in room.admins.all():
            room.admins.remove(target_user)
            removed_from.append('admins')

        # If the user was not in any group, return an error
        if not removed_from:
            return JsonResponse({'error': 'User is not a member of this room in any capacity.'}, status=404)

        # Return success message
        return JsonResponse({'message': f'User {target_user.email} removed from {", ".join(removed_from)} in room {room.room_name}.'})

    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Room, initiator, or target user not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
 # Adjust the import to your app and models
from django.core.exceptions import ObjectDoesNotExist

@api_view(["POST"])
def promote_user_to_admin(request):
    """
    Promote a user to admin in a room based on the room slug and user's email.
    """
    try:
        # Extract user email and room slug from POST request data
        email = request.data.get('email')
        room_slug = request.data.get('slug')
        enrollmentNo = request.data.get('enrollmentNo')

        if not email:
            return JsonResponse({'error': 'User email is required.'}, status=400)

        # Get the room by its slug
        room = get_object_or_404(Room, slug=room_slug)

        # Get the user by email
        user = get_object_or_404(User, email=email)
        admin = User.objects.get(enrollmentNo = enrollmentNo)

        # Check if the user is already an admin
        if user in room.admins.all():
            return JsonResponse({'error': f'User {user.email} is already an admin in this room.'}, status=400)

        # Check if the user is a participant in the room
        if user not in room.participants.all():
            return JsonResponse({'error': 'User must be a participant to be promoted to admin.'}, status=400)
        if admin not in room.admins.all():
            return JsonResponse({'error': 'User must be a admin to promote someone else to admin'}, status=400)
        # Add the user to the admins list of the room
        room.admins.add(user)

        return JsonResponse({'message': f'User {user.email} has been promoted to admin in room {room.room_name}.'})

    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Room or user not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def add_participants_to_room(request):
    try:
        # Extract the room slug and list of participant emails from the request
        room_slug = request.data.get('room_slug')
        user_emails = request.data.get('participant_emails', [])

        # Ensure room slug and participant emails are present
        if not room_slug or not user_emails:
            return Response({"error": "Room slug and participant emails are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the room by slug
        room = get_object_or_404(Room, slug=room_slug)

        # Fetch the users by their emails
        users_to_add = User.objects.filter(email__in=user_emails)

        # Ensure at least one valid user is found
        if not users_to_add.exists():
            return Response({"error": "No valid users found for the given emails."}, status=status.HTTP_400_BAD_REQUEST)

        # Add the users to the room's participants
        room.participants.add(*users_to_add)

        # Get the associated project by roomname (assuming roomname matches the project's roomname)
        project = Project.objects.filter(roomname=room_slug).first()
        
        if project:
            # Add users to the project's participants
            project.participants.add(*users_to_add)
            project.save()

        room.save()

        return Response({
            'message': f"Successfully added {len(users_to_add)} users to the room and project.",
            'participants': list(room.participants.values('email'))
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
