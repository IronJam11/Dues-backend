from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from projectapp.models import Project
from userapp.models import UserDetails, User
from rest_framework.response import Response
from rest_framework import status
from userapp.utils import get_enrollment_no_from_token

def project_detail_view(request, roomname):
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return JsonResponse({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)
            
    token = auth_header.split(' ')[1]
    enrollment_no_or_error = get_enrollment_no_from_token(token)
    if isinstance(enrollment_no_or_error, dict):  # Check if an error occurred during token decoding
        return JsonResponse(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)
            
    enrollment_no = enrollment_no_or_error
    user = get_object_or_404(User, enrollmentNo=enrollment_no) 
    
    # Fetch the project based on the provided roomname
    project = get_object_or_404(Project, roomname=roomname)
    if user not in project.participants.all():
        return JsonResponse({"error": "User is not the part of the group"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create a list of participants (assumed User model has fields like name, email, etc.)
    participants_data = [
        {
            'id': participant.id,
            'email': participant.email,
            'name': UserDetails.objects.filter(user=participant).first().name,
            'alias':UserDetails.objects.filter(user=participant).first().alias,
              # if User model has an alias field
            # Add other fields as necessary
        }
        for participant in project.participants.all()
    ]
    
    # Create a list of assignments (assuming Assignment model has fields like name, description, etc.)
    assignments_data = [
        {
            'id': assignment.id,
            'name': assignment.name,
            'description': assignment.description,
            'total_points': assignment.total_points,
            'deadline': assignment.deadline,
            # Add other fields as necessary
        }
        for assignment in project.get_project_assignments()
    ]
    
    # Create a response dictionary with all the details of the project
    project_data = {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'group_image': project.group_image.url if project.group_image else None,
        'time_assigned': project.time_assigned,
        'deadline': project.deadline,
        'roomname': project.roomname,
        'participants': participants_data,
        'assignments': assignments_data
    }
    
    # Return the project details as a JSON response
    return JsonResponse({'project': project_data})
