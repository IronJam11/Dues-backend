from django.http import JsonResponse
from rest_framework.decorators import api_view
from assignmentsapp.models import Submission, SubmissionFile, Assignment


@api_view(['GET'])
def submission_detail(request, unique_submission_name):
    try:
        # Fetch the submission using the provided unique_submission_name
        submission = Submission.objects.get(unique_submission_name=unique_submission_name)
        assignment = submission.assignment
        max_points = assignment.total_points
        
        # Prepare the submission details as a dictionary
        submission_details = {
            'id': submission.id,
            'user': submission.user.enrollmentNo,  # Get the user's enrollment number
            'assignment': submission.assignment.unique_name,  # Get the assignment's unique name
            'points_awarded': submission.points_awarded,
            'description': submission.description,
            'time_submitted': submission.time_submitted.isoformat(),  # Format the time as ISO
            'link': submission.link,
            'status': submission.status,
            'max_points': max_points,
            'unique_submission_name': submission.unique_submission_name,
            'files': [ 
                {
                    'id': file.id,
                    'file_url': file.file.url,  # URL to access the file
                } for file in submission.files.all()  # Retrieve all associated files
            ],
        }
        
        # Return the submission details as a JSON response
        return JsonResponse(submission_details, safe=False)  # safe=False allows non-dict objects

    except Submission.DoesNotExist:
        # Return an error if the submission does not exist
        return JsonResponse({"error": "Submission not found."}, status=404)

    except Exception as e:
        # Return a generic error message for other exceptions
        return JsonResponse({"error": str(e)}, status=500)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from assignmentsapp.models import Iteration, CompletedAssignment, Submission, Assignment
from userapp.models import User
from rest_framework.exceptions import NotFound, ValidationError
from userapp.utils import get_enrollment_no_from_token
from django.shortcuts import get_object_or_404

class ReviewSubmission(APIView):

    def post(self, request):
        # Extract necessary data from the request
        feedback = request.data.get('feedback')
        points = request.data.get('points')
        status_value = request.data.get('status')
        unique_submission_name = request.data.get('unique_submission_name')

        if not feedback or not status_value:
            return Response({'error': 'Feedback and status are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the submission and corresponding assignment
            submission = Submission.objects.get(unique_submission_name=unique_submission_name)
            assignment = submission.assignment

            # Get the `for_user` from the submission (the user being reviewed)
            for_user = submission.user  # This assumes the user is the one being reviewed

            # Get the reviewer (`by` user) from the access token
            auth_header = request.headers.get('Authorization')
            if auth_header is None or not auth_header.startswith('Bearer '):
                return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = auth_header.split(' ')[1]
            enrollment_no_or_error = get_enrollment_no_from_token(token)
            if isinstance(enrollment_no_or_error, dict):  # Check if an error occurred during token decoding
                return Response(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)
            
            enrollment_no = enrollment_no_or_error
            by_user = get_object_or_404(User, enrollmentNo=enrollment_no)  # Reviewer

            # Create the Iteration object for feedback
            iteration = Iteration.objects.create(
                title=f"Review for {assignment.name}",
                feedback=feedback,
                by=by_user,  # Reviewer
                for_user=for_user,  # Reviewee fetched from submission
                assignment=assignment,
                submission=submission
            )
            submission.status = "Reviewed"
            submission.save()

            # If status is 'approved', validate and create a CompletedAssignment object
            if status_value == 'approved':
                max_points = assignment.total_points  # Maximum points for the assignment
                if points is None or not points.isdigit():
                    return Response({'error': 'Points must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)
                
                points_awarded = int(points)

                if points_awarded < 0 or points_awarded > max_points:
                    return Response({
                        'error': f'Points must be between 0 and {max_points}.'}, status=status.HTTP_400_BAD_REQUEST)

                CompletedAssignment.objects.create(
                    user=for_user,  # User being reviewed
                    assignment=assignment,
                    score=points_awarded, # Points provided in the frontend
                    reviewed_by = by_user,
                )

            return Response({'success': 'Review and status updated successfully.'}, status=status.HTTP_200_OK)

        except Submission.DoesNotExist:
            return Response({'error': 'Submission not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
