from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from userapp.models import User
from assignmentsapp.models import Assignment
from userapp.utils import decode_jwt_token
from rest_framework.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def get_user_assignments_reviewee(request):
    if request.method == 'GET':
        try:
            # Decode the JWT token to get the payload
            payload = decode_jwt_token(request)
            enrollmentNo = payload.get('enrollmentNo')  # Get enrollmentNo from JWT payload
        except AuthenticationFailed as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Fetch the user based on the enrollment number from the decoded token
        user = get_object_or_404(User, enrollmentNo=enrollmentNo)

        # Fetch assignments where the user is a reviewee
        assignments_as_reviewee = Assignment.objects.filter(reviewees=user)

        # Create a list of assignments data to return as JSON
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

        # Return the assignments data as JSON
        return JsonResponse({'assignments': assignments_data})

def get_user_assignments_reviewer(request):
    if request.method == 'GET':
        try:
            # Decode the JWT token to get the payload
            payload = decode_jwt_token(request)
            enrollmentNo = payload.get('enrollmentNo')  # Get enrollmentNo from JWT payload
        except AuthenticationFailed as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Fetch the user based on the enrollment number from the decoded token
        user = get_object_or_404(User, enrollmentNo=enrollmentNo)

        # Fetch assignments where the user is a reviewer
        assignments_as_reviewer = Assignment.objects.filter(reviewers=user)

        # Create a list of assignments data to return as JSON
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

        # Return the assignments data as JSON
        return JsonResponse({'assignments': assignments_data})

@csrf_exempt
def delete_assignment(request, unique_assignment_name):
    if request.method == 'DELETE':
        try:
            assignment = get_object_or_404(Assignment, unique_name=unique_assignment_name)
            assignment.delete()
            return JsonResponse({'message': 'Assignment deleted successfully!'}, status=200)
        except Assignment.DoesNotExist:
            return JsonResponse({'error': 'Assignment not found'}, status=404)
    else:
        return HttpResponse(status=405)  # Method not allowed if not DELETE
