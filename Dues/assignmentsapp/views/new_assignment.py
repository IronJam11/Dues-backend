from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from assignmentsapp.models import Assignment
from userapp.models import User
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.utils.text import slugify
from django.utils import timezone





@api_view(['POST'])
def create_assignment(request):
    try:
        # Extract data from the request
        name = request.data.get('name')
        description = request.data.get('description')
        total_points = request.data.get('total_points')
        deadline = request.data.get('deadline')
        reviewers = request.data.get('reviewers', [])
        reviewees = request.data.get('reviewees', [])
        time_assigned = timezone.now()

        if not name or not total_points:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate unique_name (slug) using name and time_assigned
        formatted_time = time_assigned.strftime('%Y-%m-%d-%H-%M-%S')  # Remove colons
        unique_name = slugify(f"{name}-{formatted_time}")

        # Create the assignment
        assignment = Assignment.objects.create(
            name=name,
            description=description,
            total_points=total_points,
            time_assigned=time_assigned,
            deadline=deadline,
            unique_name=unique_name,  # Add unique_name to the Assignment creation
        )

        # Add reviewers and reviewees
        assignment.reviewers.set(User.objects.filter(email__in=reviewers))
        assignment.reviewees.set(User.objects.filter(email__in=reviewees))

        assignment.save()

        return Response({"message": "Assignment created successfully", "unique_name": unique_name}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)