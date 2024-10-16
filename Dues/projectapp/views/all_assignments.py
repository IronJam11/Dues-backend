from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from projectapp.models import Project


def project_assignments_view(request, roomname):
    """
    View to return the assignments for a given project based on its roomname.
    """
    # Fetch the project based on the provided roomname
    project = get_object_or_404(Project, roomname=roomname)
    
    # Get all assignments related to the project
    assignments = project.get_project_assignments()
    
    # Create a list of assignments to return as JSON
    assignments_data = [
        {
            'id': assignment.id,
            'name': assignment.name,
            'description': assignment.description,
            'total_points': assignment.total_points,
            'deadline': assignment.deadline,
            # Add other fields as necessary
        }
        for assignment in assignments
    ]
    
    # Return the list of assignments as JSON response
    return JsonResponse({'assignments': assignments_data})
