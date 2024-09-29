from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from userapp.models import User
from assignmentsapp.models import Assignment

def get_user_assignments_reviewee(request, enrollment_no):
    # Fetch the user based on enrollment number
    user = get_object_or_404(User, enrollmentNo=enrollment_no)
    
    # Fetch assignments where the user is a reviewer or reviewee
    # assignments_as_reviewer = Assignment.objects.filter(reviewers=user)
    assignments_as_reviewee = Assignment.objects.filter(reviewees=user)
    
    # Combine the queryset results (use distinct to avoid duplicates)
    # all_assignments = assignments_as_reviewer.union(assignments_as_reviewee).distinct()
    
    # Create a list of assignments data to return as JSON
    assignments_data = [
        {
            'name': assignment.name,
            'description': assignment.description,
            'total_points': assignment.total_points,
            'color': assignment.color,
            'time_assigned': assignment.time_assigned,
            'deadline': assignment.deadline,
            'unique_name':assignment.unique_name,
        }
        for assignment in assignments_as_reviewee
    ]
    
    # Return the assignments data as JSON
    return JsonResponse({'assignments': assignments_data})



def get_user_assignments_reviewer(request, enrollment_no):
    # Fetch the user based on enrollment number
    user = get_object_or_404(User, enrollmentNo=enrollment_no)
    
    # Fetch assignments where the user is a reviewer or reviewee
    # assignments_as_reviewer = Assignment.objects.filter(reviewers=user)
    assignments_as_reviewer = Assignment.objects.filter(reviewers=user)
    
    # Combine the queryset results (use distinct to avoid duplicates)
    # all_assignments = assignments_as_reviewer.union(assignments_as_reviewee).distinct()
    
    # Create a list of assignments data to return as JSON
    assignments_data = [
        {
            'name': assignment.name,
            'description': assignment.description,
            'total_points': assignment.total_points,
            'color': assignment.color,
            'time_assigned': assignment.time_assigned,
            'deadline': assignment.deadline,
            'unique_name':assignment.unique_name,
        }
        for assignment in assignments_as_reviewer
    ]
    
    # Return the assignments data as JSON
    return JsonResponse({'assignments': assignments_data})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from assignmentsapp.models import Assignment 
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def delete_assignment(request, unique_assignment_name):
    if request.method == 'DELETE':
        try:
            assignment = get_object_or_404(Assignment, unique_name = unique_assignment_name)
            assignment.delete()
            return JsonResponse({'message': 'Assignment deleted successfully!'}, status=200)
        except Assignment.DoesNotExist:
            return JsonResponse({'error': 'Assignment not found'}, status=404)
    else:
        return HttpResponse(status=405)  # Method not allowed if not DELETE

