from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from assignmentsapp.models import Iteration, Assignment
from userapp.models import UserDetails, User
from userapp.utils import get_enrollment_no_from_token  # Ensure this function is defined in utils

class GetUserIterations(APIView):

    def get(self, request, unique_name):
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

        try:
            # Get the assignment based on the unique_name
            assignment = get_object_or_404(Assignment, unique_name=unique_name)

            # Query the Iteration model for this user and assignment
            iterations = Iteration.objects.filter(for_user=user, assignment=assignment)
            by_details = UserDetails.objects.filter(user = user).first()
            print(by_details)

            # Serialize the iterations (assuming you have a serializer for Iteration)
            iterations_data = [
                {
                    'title': iteration.title,
                    'feedback': iteration.feedback,
                    'time_assigned': iteration.time_assigned,
                    'by_email': iteration.by.email, 
                    'by_enrollmentNo': iteration.by.enrollmentNo,
                    'by_name': by_details.name,
                      # Adjust as needed
                }
                for iteration in iterations
            ]

            return Response({'iterations': iterations_data}, status=status.HTTP_200_OK)

        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
