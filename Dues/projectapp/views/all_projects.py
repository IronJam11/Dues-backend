from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from projectapp.models import Project
from userapp.models import User

def get_user_projects(request, enrollmentNo):
    # Fetch the user based on the enrollmentNo
    user = get_object_or_404(User, enrollmentNo=enrollmentNo)
    
    # Get all projects where the user is a participant
    projects = Project.objects.filter(participants=user).values('name', 'description', 'deadline', 'roomname')

    return JsonResponse(list(projects), safe=False)
