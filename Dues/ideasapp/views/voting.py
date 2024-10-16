from rest_framework.decorators import api_view
from rest_framework.response import Response
from ideasapp.models import Idea, Vote
from ideasapp.serializers import IdeaSerializer
from django.http import JsonResponse
from userapp.utils import get_enrollment_no_from_token
from rest_framework import status
from django.shortcuts import get_object_or_404
from userapp.models import User

@api_view(['GET'])
def userVotingDetails(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

    token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'
    print("token", token)

    enrollment_no_or_error = get_enrollment_no_from_token(token)
    if isinstance(enrollment_no_or_error, dict):  # Check if it's an error dictionary
        return JsonResponse(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)

    enrollment_no = enrollment_no_or_error  # Extract enrollmentNo

    user = get_object_or_404(User, enrollmentNo=enrollment_no)  # Get the currently authenticated user
    ideas = Idea.objects.all()  # Retrieve all ideas

    # Create a dictionary to map unique_name to the user's vote status
    ideas_vote_status = {}

    # Create a set of voted idea IDs for quick lookup
    voted_ideas = Vote.objects.filter(user=user).values_list('idea_id', flat=True)

    for idea in ideas:
        unique_name = idea.unique_name  # Assuming each idea has a unique_name field
        if idea.id in voted_ideas:
            # Get the vote type for the idea
            vote_type = Vote.objects.get(user=user, idea=idea).vote_type
            ideas_vote_status[unique_name] = vote_type  # Map unique_name to the user's vote
        else:
            ideas_vote_status[unique_name] = None  # No vote cast by user

    return Response({'ideas': ideas_vote_status})
