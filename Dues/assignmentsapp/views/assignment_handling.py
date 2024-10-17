from django.shortcuts import get_object_or_404
from userapp.models import User
from assignmentsapp.models import Assignment, CompletedAssignment, Submission, Iteration, SubTask
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
        print("token", token)

        enrollment_no_or_error = get_enrollment_no_from_token(token)
        if isinstance(enrollment_no_or_error, dict):  # Check if it's an error dictionary
            return Response(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)

        enrollment_no = enrollment_no_or_error  # Extract enrollmentNo

        user = get_object_or_404(User, enrollmentNo=enrollment_no)

        # Filter assignments for the reviewee and exclude those with a completed assignment by the same user and assignment
        assignments_as_reviewee = Assignment.objects.filter(reviewees=user).exclude(
            completedassignment__user=user, completedassignment__assignment__in=Assignment.objects.filter(reviewees=user)
        )

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

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from assignmentsapp.models import Assignment, Submission, Iteration, SubTask, CompletedAssignment

def get_assignment_details(request, unique_name):

    # Fetch the assignment using the unique_name
    assignment = get_object_or_404(Assignment, unique_name=unique_name)

    # Fetch related submissions for this assignment
    submissions = Submission.objects.filter(assignment=assignment)
    
    # Fetch related iterations (feedback)
    iterations = Iteration.objects.filter(assignment=assignment)
    
    # Fetch related subtasks
    subtasks = SubTask.objects.filter(assignment=assignment)
    
    # Fetch completed assignments (if any)
    completed_assignments = CompletedAssignment.objects.filter(assignment=assignment)

    # Fetch reviewers and reviewees using .all() to get the actual data
    reviewers = assignment.reviewers.all()  # Get all reviewers for this assignment
    reviewees = assignment.reviewees.all()  # Get all reviewees for this assignment
    
    # Build the response dictionary
    assignment_data = {
        'name': assignment.name,
        'description': assignment.description,
        'total_points': assignment.total_points,
        'color': assignment.color,
        'time_assigned': assignment.time_assigned,
        'deadline': assignment.deadline,
        'unique_name': assignment.unique_name,
        'submissions': [
            {
                'user': submission.user.enrollmentNo,
                'points_awarded': submission.points_awarded,
                'description': submission.description,
                'time_submitted': submission.time_submitted,
                'link': submission.link,
                'status': submission.status,
                'files': [file.file.url for file in submission.files.all()]
            }
            for submission in submissions
        ],
        'iterations': [
            {
                'title': iteration.title,
                'feedback': iteration.feedback,
                'by': iteration.by.enrollmentNo,
                'for_user': iteration.for_user.enrollmentNo,
                'time_assigned': iteration.time_assigned
            }
            for iteration in iterations
        ],
        'subtasks': [
            {
                'description': subtask.description,
                'attachment': subtask.attachment.url if subtask.attachment else None
            }
            for subtask in subtasks
        ],
        'completed_assignments': [
            {
                'user': completed_assignment.user.enrollmentNo,
                'score': completed_assignment.score,
                'reviewed_by': completed_assignment.reviewed_by.enrollmentNo if completed_assignment.reviewed_by else 'Not reviewed yet'
            }
            for completed_assignment in completed_assignments
        ],
        'reviewers': [
            reviewer.email
            for reviewer in reviewers  # Use .all() to iterate over reviewers
        ],
        'reviewees': [
            reviewee.email  # Create a list of emails for reviewees
            for reviewee in reviewees  # Use .all() to iterate over reviewees
        ]
    }

    # Return the assignment data as a JSON response
    return JsonResponse(assignment_data)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def edit_assignment_details(request, unique_name):
    try:
        # Get the assignment object based on the unique name
        assignment = Assignment.objects.get(unique_name=unique_name)

        # Extract form data
        name = request.data.get('name')
        print(name)
        description = request.data.get('description')
        total_points = request.data.get('total_points')
        deadline = request.data.get('deadline')
        reviewers_emails = request.data.get('reviewers')  # List of reviewer emails
        reviewees_emails = request.data.get('reviewees')  # List of reviewee emails
        print(reviewees_emails)
        # Update the assignment details
        assignment.name = name
        assignment.description = description
        assignment.total_points = total_points
        assignment.deadline = deadline
        assignment.save()

        # Fetch User objects for reviewers and reviewees
        reviewers = User.objects.filter(email__in=reviewers_emails)
        reviewees = User.objects.filter(email__in=reviewees_emails)
        print(reviewees)

        # Update the many-to-many relationships for reviewers and reviewees
        assignment.reviewers.set(reviewers)  # Update reviewers
        assignment.reviewees.set(reviewees)  # Update reviewees

        assignment.save()

        return Response({'message': 'Assignment updated successfully!'}, status=status.HTTP_200_OK)

    except Assignment.DoesNotExist:
        return Response({'error': 'Assignment not found!'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)