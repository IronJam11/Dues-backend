from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from userapp.models import User
from assignmentsapp.models import Assignment
from userapp.utils import get_enrollment_no_from_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class GetUserAssignmentsRevieweeView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')


        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

        token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'
        print("token",token)

        enrollment_no_or_error = get_enrollment_no_from_token(token)
        if isinstance(enrollment_no_or_error, dict):  # Check if it's an error dictionary
            return Response(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)

        enrollment_no = enrollment_no_or_error  # Extract enrollmentNo

        user = get_object_or_404(User, enrollmentNo=enrollment_no)

        assignments_as_reviewee = Assignment.objects.filter(reviewees=user)

        assignments_data = [
            {
                'name': assignment.name,
                'description': assignment.description,
                'total_points': assignment.total_points,
                'color': assignment.color,
                'time_assigned': assignment.time_assigned,
                'deadline': assignment.deadline,
                'unique_name': assignment.unique_name,
            }
            for assignment in assignments_as_reviewee
        ]

        return Response({'assignments': assignments_data})

class GetUserAssignmentsReviewerView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

        token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'

        enrollment_no_or_error = get_enrollment_no_from_token(token)
        if isinstance(enrollment_no_or_error, dict):  # Check if it's an error dictionary
            return Response(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)

        enrollment_no = enrollment_no_or_error  # Extract enrollmentNo

        user = get_object_or_404(User, enrollmentNo=enrollment_no)

        assignments_as_reviewer = Assignment.objects.filter(reviewers=user)

        assignments_data = [
            {
                'name': assignment.name,
                'description': assignment.description,
                'total_points': assignment.total_points,
                'color': assignment.color,
                'time_assigned': assignment.time_assigned,
                'deadline': assignment.deadline,
                'unique_name': assignment.unique_name,
            }
            for assignment in assignments_as_reviewer
        ]

        return Response({'assignments': assignments_data})
