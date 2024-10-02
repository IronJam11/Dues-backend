import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from userapp.models import User, UserDetails
from rest_framework.decorators import api_view

@csrf_exempt
@api_view(['POST'])
def update_user_details(request):
    if request.method == 'POST':
        try:
            # Fetch the JWT token from the cookies
            jwt_cookie = request.COOKIES.get('jwt')
            if not jwt_cookie:
                return JsonResponse({'status': 'error', 'message': 'Authentication token not found.'}, status=401)

            # Decode the JWT token to extract enrollmentNo
            payload = jwt.decode(jwt_cookie, settings.SECRET_KEY, algorithms=['HS256'])
            enrollment_no = payload.get('enrollmentNo')

            # Get the user associated with the enrollmentNo
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

        except jwt.ExpiredSignatureError:
            return JsonResponse({'status': 'error', 'message': 'Token has expired.'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': 'Invalid token.'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)