from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from assignmentsapp.models import Assignment, Submission, SubmissionFile
from userapp.models import User, UserDetails

@api_view(['POST'])
@parser_classes([MultiPartParser])
def submit_assignment(request):
    # Extracting data from the request
    enrollment_no = request.data.get('enrollment_no')
    unique_name = request.data.get('unique_name')
    description = request.data.get('description', '')

    # Fetch the user by enrollment number
    user = User.objects.get(enrollmentNo=enrollment_no)

    # Fetch the assignment by its unique name
    assignment = Assignment.objects.get(unique_name=unique_name)

    # Create a new submission object
    submission = Submission.objects.create(
        user=user,
        assignment=assignment,
        description=description
    )

    # Create a SubmissionFile object for each uploaded file
    files = request.FILES.getlist('files')
    for file in files:
        SubmissionFile.objects.create(submission=submission, file=file)

    return JsonResponse({'message': 'Submission successful!'}, status=201)


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
            }

            # Add the serialized submission to the list
            submissions_data.append(submission_data)

        # Return the serialized data as JSON
        return JsonResponse({'submissions': submissions_data}, status=200)

    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Assignment not found'}, status=404)
