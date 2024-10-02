from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from projectapp.models import Project
from userapp.models import User
from rest_framework.exceptions import AuthenticationFailed
from userapp.utils import decode_jwt_token_boolean  # Import your decode function


def get_user_projects(request):
    # Ensure the request method is GET
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method. Only GET is allowed.'}, status=405)

    # Get the JWT token from cookies
    token = request.COOKIES.get('jwt')

    if not token:
        return JsonResponse({'error': 'Authentication token not found'}, status=401)

    try:
        # Decode the token and check if it's expired
        decoded_data = decode_jwt_token_boolean(token)

        # If the token is expired, return an error
        if decoded_data['is_token_expired']:
            return JsonResponse({'error': 'Token has expired'}, status=401)

        # Fetch the user based on enrollmentNo from the decoded token
        enrollmentNo = decoded_data['enrollmentNo']
        user = get_object_or_404(User, enrollmentNo=enrollmentNo)

        # Get all projects where the user is a participant
        projects = Project.objects.filter(participants=user).values('name', 'description', 'deadline', 'roomname')

        # Return the project data as a JSON response
        return JsonResponse(list(projects), safe=False)

    except AuthenticationFailed as e:
        return JsonResponse({'error': str(e)}, status=401)
