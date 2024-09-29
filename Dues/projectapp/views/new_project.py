from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.utils.text import slugify
from userapp.models import User
from projectapp.models import Project
import datetime


@api_view(['POST'])
def createNewProject(request):
    try:
        # Extract data from the request
        name = request.data.get('name')
        description = request.data.get('description')
        group_image = request.FILES.get('group_image')
        deadline = request.data.get('deadline')
        participant_emails = request.data.get('participant_emails', [])
        print(participant_emails)

        # Assign the current time as time_assigned
        time_assigned = timezone.now()

        # Remove colons from the deadline (if it is in datetime format) and convert it to a string
        if isinstance(deadline, datetime.datetime):
            deadline_str = deadline.strftime('%Y-%m-%dT%H-%M')
        else:
            deadline_str = deadline  # If deadline is already a string, use it as is

        # Create roomname dynamically based on name, time_assigned, and cleaned deadline
        roomname_raw = f"{name}-{time_assigned.strftime('%Y%m%d%H%M%S')}-{deadline_str}"
        roomname = slugify(roomname_raw)  # Slugify the roomname to ensure it conforms to URL standards

        # Create the project instance
        project = Project.objects.create(
            name=name,
            description=description,
            group_image=group_image,
            time_assigned=time_assigned,
            deadline=deadline,
            roomname=roomname
        )

        # Add participants to the project
        participants = User.objects.filter(email__in=participant_emails)
        project.participants.add(*participants)

        # Save the project after adding participants
        project.save()

        # Return success response
        return Response({"message": "Project created successfully!", "roomname": project.roomname}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from projectapp.models import Project

@api_view(['DELETE'])
def deleteProject(request, roomname):
    try:
        # Get the project by roomname
        project = Project.objects.get(roomname=roomname)

        # Delete the project
        project.delete()

        # Return success response
        return Response({"message": "Project deleted successfully!"}, status=status.HTTP_200_OK)
    
    except Project.DoesNotExist:
        return Response({"error": "Project not found!"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
