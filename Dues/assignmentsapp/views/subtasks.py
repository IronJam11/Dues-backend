from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from assignmentsapp.models import Assignment, SubTask

@csrf_exempt
@require_http_methods(["POST"])
def create_subtask(request):
    if request.method == "POST":
        unique_name = request.POST.get('unique_name')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')
        print(unique_name)
        try:
            # Fetch the assignment using the unique_name
            assignment = Assignment.objects.get(unique_name=unique_name)
            print(assignment.total_points)

            # Create the subtask
            subtask = SubTask(
                assignment=assignment,
                description=description,
                attachment=attachment
            )
            subtask.save()

            return JsonResponse({'message': 'Subtask created successfully!'})
        except Assignment.DoesNotExist:
            return HttpResponseBadRequest('Assignment not found')
        except Exception as e:
            return HttpResponseBadRequest(f'Error creating subtask: {str(e)}')
    return HttpResponseBadRequest('Invalid request method')

@require_http_methods(["GET"])
def get_subtasks_by_assignment(request, unique_name):
    try:
        # Fetch the assignment using the unique_name
        assignment = Assignment.objects.get(unique_name=unique_name)
        
        # Fetch all subtasks linked to this assignment
        subtasks = SubTask.objects.filter(assignment=assignment).values('id', 'description', 'attachment')
        
        return JsonResponse({'subtasks': list(subtasks)}, status=200)
    
    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Assignment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
