from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import User, UserDetails
import json

@csrf_exempt
def update_user_details(request):
    if request.method == 'POST':
        try:
            # Get the user associated with the enrollmentNo
            enrollment_no = request.POST.get('enrollmentNo')
            user = User.objects.get(enrollmentNo=enrollment_no)

            # Get the associated UserDetails
            user_details = UserDetails.objects.filter(user=user).first()

            # Update the fields if they are provided in the request
            print(request.POST)
            print(request.FILES)

            name = request.POST.get('name')
            alias = request.POST.get('alias')
            year = request.POST.get('year')
            is_developer = request.POST.get('isDeveloper') == 'true'  # Convert to boolean

            if name:
                user_details.name = name
            if alias:
                user_details.alias = alias
            if year:
                user_details.year = year
            if is_developer is not None:
                user_details.isDeveloper = is_developer
            
            # Update the profile picture if provided
            if 'profilePicture' in request.FILES:
                user_details.profilePicture = request.FILES['profilePicture']
           
            # Save the updated UserDetails
            user_details.save()

            return JsonResponse({'status': 'success', 'message': 'User details updated successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
