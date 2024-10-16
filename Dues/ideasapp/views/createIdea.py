from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.text import slugify  # Importing slugify to create URL-safe names
from ideasapp.models import Idea
from userapp.models import User
import json
from userapp.utils import get_enrollment_no_from_token
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status  # Importing status from DRF

@csrf_exempt
def create_idea_view(request):
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

        token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'
        print("token", token)

        enrollment_no_or_error = get_enrollment_no_from_token(token)
        if isinstance(enrollment_no_or_error, dict):  # Check if it's an error dictionary
            return JsonResponse(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)

        enrollment_no = enrollment_no_or_error  # Extract enrollmentNo

        created_by = get_object_or_404(User, enrollmentNo=enrollment_no)
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        idea_status = data.get('status', 'pending')  # Renaming local variable to avoid conflict
        user_emails = data.get('users', [])
        
        # Fetch the User objects for the selected users
        users = User.objects.filter(email__in=user_emails)
        print("users", users)

        # Create the idea with multiple contributors
        idea = Idea.objects.create(
            title=title,
            description=description,
            status=idea_status,  # Use the renamed variable here
            created_by=created_by
        )
        idea.users.set(users)  # Assign multiple users to the idea

        # Generate unique_name based on title and created_at
        unique_name = slugify(f"{title}-{idea.created_at.strftime('%Y%m%d%H%M%S')}")
        idea.unique_name = unique_name
        idea.save()

        return JsonResponse({"message": "Idea created successfully", "idea_id": idea.id, "unique_name": unique_name})

    return JsonResponse({"error": "Invalid request method"}, status=400)
