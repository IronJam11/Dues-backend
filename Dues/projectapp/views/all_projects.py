from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from projectapp.models import Project
from userapp.models import User
from rest_framework.exceptions import AuthenticationFailed
from userapp.utils import decode_jwt_token_boolean  # Import your decode function
from userapp.utils import get_enrollment_no_from_token
from rest_framework.response import Response
from rest_framework import status

def get_user_projects(request):
    # Ensure the request method is GET
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method. Only GET is allowed.'}, status=405)

    # Get the JWT token from cookies
    auth_header = request.headers.get('Authorization')


    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

    token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'
    print("token",token)

    enrollment_no_or_error = get_enrollment_no_from_token(token)
    if isinstance(enrollment_no_or_error, dict):  # Check if it's an error dictionary
        return Response(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)
    enrollment_no = enrollment_no_or_error 
    user = get_object_or_404(User, enrollmentNo=enrollment_no)
    projects = Project.objects.filter(participants=user).values('name', 'description', 'deadline', 'roomname')
    return JsonResponse(list(projects), safe=False)


