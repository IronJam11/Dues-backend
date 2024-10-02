from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from assignmentsapp.models import Assignment, Submission, SubmissionFile
from userapp.models import User, UserDetails
from rest_framework.exceptions import AuthenticationFailed
from userapp.utils import decode_jwt_token
from django.utils import timezone

@api_view(['POST'])
@parser_classes([MultiPartParser])
def submit_assignment(request):
    try:
        # Decode the JWT token to get the enrollmentNo
        payload = decode_jwt_token(request)
        enrollment_no = payload.get('enrollmentNo')  # Get enrollmentNo from the token
    except AuthenticationFailed as e:
        return JsonResponse({"error": str(e)}, status=400)

    # Extracting other data from the request
    unique_name = request.data.get('unique_name')
    description = request.data.get('description', '')
    url = request.data.get('url')

    try:
        # Fetch the user by enrollment number
        user = User.objects.get(enrollmentNo=enrollment_no)

        # Fetch the assignment by its unique name
        assignment = Assignment.objects.get(unique_name=unique_name)

        # Create a new submission object
        submission = Submission.objects.create(
            user=user,
            assignment=assignment,
            description=description,
            link=url,
            status="To Be Reviewed"
        )

        # Format time_submitted to create unique_submission_name
        formatted_time = submission.time_submitted.strftime('%Y%m%d%H%M%S')  # Format: YYYYMMDDHHMMSS
        unique_submission_name = f"{formatted_time}_{user.enrollmentNo}"  # Combine with enrollmentNo

        # Update the submission with the unique_submission_name
        submission.unique_submission_name = unique_submission_name
        submission.save()

        # Handle file uploads
        files = request.FILES.getlist('files')
        for file in files:
            SubmissionFile.objects.create(submission=submission, file=file)
            print(file)

        return JsonResponse({'message': 'Submission successful!'}, status=201)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except Assignment.DoesNotExist:
        return JsonResponse({"error": "Assignment not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def list_submissions(request, unique_name):
    try:
        # Fetch the assignment based on the given unique name
        assignment = Assignment.objects.get(unique_name=unique_name)

        # Get all submissions linked to the assignment
        submissions = Submission.objects.filter(assignment=assignment).select_related('user')

        # Create a list to hold the serialized data
        submissions_data = []

        # Handle case where there are no submissions
        if not submissions.exists():
            return JsonResponse({'message': 'No submissions found for this assignment.'}, status=200)

        for submission in submissions:
            # Fetch all files linked to this submission
            files = SubmissionFile.objects.filter(submission=submission)
            user_details = UserDetails.objects.filter(user=submission.user).first()

            # Serialize the submission and its files
            submission_data = {
                'user': user_details.name if user_details else 'Unknown User',
                'description': submission.description,
                'points_awarded': submission.points_awarded,
                'time_submitted': submission.time_submitted,
                'files': [{'id': file.id, 'file_url': file.file.url} for file in files],
                'status': submission.status,
                'link':submission.link,
                'unique_submission_name':submission.unique_submission_name
            }

            # Add the serialized submission to the list
            submissions_data.append(submission_data)

        # Return the serialized data as JSON
        return JsonResponse({'submissions': submissions_data}, status=200)

    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Assignment not found'}, status=404)



