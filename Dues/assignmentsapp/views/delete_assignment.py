from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from assignmentsapp.models import Assignment
from userapp.models import User
from userapp.utils import get_enrollment_no_from_token

@api_view(['DELETE'])  # Use DELETE method to handle assignment deletion
def delete_assignment(request, unique_name):
    try:
        # Fetch the assignment based on the unique_name from the URL
        assignment = get_object_or_404(Assignment, unique_name=unique_name)

        # Get the Authorization token from the request header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

        # Extract the token and get the user's enrollment number
        token = auth_header.split(' ')[1]
        enrollment_no_or_error = get_enrollment_no_from_token(token)

        if isinstance(enrollment_no_or_error, dict):  # Check if an error occurred during token decoding
            return Response(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user using the enrollment number
        enrollment_no = enrollment_no_or_error
        user = get_object_or_404(User, enrollmentNo=enrollment_no)

        # Check if the user is in the assignment's reviewers
        if user in assignment.reviewers.all():
            # If the user is a reviewer, delete the assignment
            assignment.delete()
            return Response({"message": "Assignment deleted successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Permission denied. User is not a reviewer for this assignment."}, status=status.HTTP_403_FORBIDDEN)

    except Assignment.DoesNotExist:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
