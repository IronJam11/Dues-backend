from django.http import JsonResponse
from rest_framework.decorators import api_view
from assignmentsapp.models import Submission, SubmissionFile

@api_view(['GET'])
def submission_detail(request, unique_submission_name):
    try:
        # Fetch the submission using the provided unique_submission_name
        submission = Submission.objects.get(unique_submission_name=unique_submission_name)
        
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
