from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from assignmentsapp.models import Assignment, CompletedAssignment
from userapp.models import User
from userapp.utils import get_enrollment_no_from_token  # Ensure this function is defined in utils

class GetCompletedAssignments(APIView):

    def get(self, request):
        # Extract the token from the request header
        auth_header = request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Bearer '):
            return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)
        
        token = auth_header.split(' ')[1]
        enrollment_no_or_error = get_enrollment_no_from_token(token)
        if isinstance(enrollment_no_or_error, dict):  # Check if an error occurred during token decoding
            return Response(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment_no = enrollment_no_or_error
        
        # Get the user from the enrollment number
        user = get_object_or_404(User, enrollmentNo=enrollment_no)
        print(user.enrollmentNo)

        try:
            # Query the CompletedAssignment model for all completed assignments for this user
            completed_assignments = CompletedAssignment.objects.filter(user = user)
            
            # Collect the details of each completed assignment, including the score
            completed_assignments_data = [
                {
                    'assignment_name': completed_assignment.assignment.name,
                    'description': completed_assignment.assignment.description,
                    'total_points': completed_assignment.assignment.total_points,
                    'deadline': completed_assignment.assignment.deadline,
                    'color': completed_assignment.assignment.color,
                    'user': completed_assignment.user.enrollmentNo,
                    'score': completed_assignment.score,
                    'unique_name': completed_assignment.assignment.unique_name,
                    'time_assigned': completed_assignment.assignment.time_assigned,
                    'reviewer': completed_assignment.reviewed_by.enrollmentNo,
                    'max_points': completed_assignment.assignment.total_points,
                }
                for completed_assignment in completed_assignments
            ]

            return Response({'completed_assignments': completed_assignments_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
