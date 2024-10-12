from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings
from userapp.models import User, UserDetails
from django.core.files.storage import default_storage

def get_user_from_access_token(token):
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')

        if user_id is not None:
            user = User.objects.get(id=user_id)
            user_detail = UserDetails.objects.filter(user=user).first()
            profile_picture_url = default_storage.url(user_detail.profilePicture.name) if user_detail.profilePicture else ""

            return {
                'id': user.id,
                'email': user.email,
                'enrollmentNo': user.enrollmentNo,
                'name': user_detail.name,
                'alias': user_detail.alias,
                'year': user_detail.year,
                'isDeveloper': user_detail.isDeveloper,
                'profilePicture': profile_picture_url,
                'is_reviewee': user.is_reviewee,
                'is_reviewer': user.is_reviewer,
                'is_admin': user.is_admin,
            }
        else:
            return {'error': 'Invalid token: User ID not found'}

    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.DecodeError:
        return {'error': 'Error decoding token'}
    except User.DoesNotExist:
        return {'error': 'User not found'}

class GetUserFromTokenView(APIView):

    def get(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header is None or not auth_header.startswith('Bearer '):
            return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

        token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'
        
        user_details = get_user_from_access_token(token)

        return Response(user_details, status=status.HTTP_200_OK)




def check_user_has_user_details(token):
    try:
        # Decode the token to get the user ID
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')

        if user_id is not None:
            # Try to get the user object
            user = User.objects.get(id=user_id)
            
            # Check if UserDetails exists for the user
            user_detail = UserDetails.objects.filter(user=user).first()

            if user_detail:
                # User has corresponding UserDetails
                return {
                    'user_has_details': True,
                    'message': f"UserDetails found for user {user.enrollmentNo}",
                    'name': user_detail.name,
                    'alias': user_detail.alias,
                    'enrollmentNo': user.enrollmentNo,
                }
            else:
                # User does not have UserDetails
                return {
                    'user_has_details': False,
                    'message': f"UserDetails not found for user {user.enrollmentNo}",
                    'enrollmentNo': user.enrollmentNo,
                }
        else:
            return {'error': 'Invalid token: User ID not found'}

    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.DecodeError:
        return {'error': 'Error decoding token'}
    except User.DoesNotExist:
        return {'error': 'User not found'}

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CheckUserDetailsView(APIView):

    def get(self, request, *args, **kwargs):
        # Extract the Authorization header
        auth_header = request.headers.get('Authorization')

        # Check if the Authorization header is present and formatted correctly
        if auth_header is None or not auth_header.startswith('Bearer '):
            return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

        # Extract the JWT token from the Authorization header (Bearer <token>)
        token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'
        
        # Call the function to check if the user has UserDetails
        user_check_result = check_user_has_user_details(token)

        # Return the result as a response
        return Response(user_check_result, status=status.HTTP_200_OK if 'error' not in user_check_result else status.HTTP_400_BAD_REQUEST)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage


# Function to get user details by enrollment number
def get_user_from_enrollment_no(enrollment_no):
    try:
        # Fetch the user based on the enrollment number
        user = User.objects.get(enrollmentNo=enrollment_no)
        user_detail = UserDetails.objects.filter(user=user).first()

        # Get the profile picture URL if it exists
        profile_picture_url = default_storage.url(user_detail.profilePicture.name) if user_detail and user_detail.profilePicture else ""

        # Return user details
        return {
            'id': user.id,
            'email': user.email,
            'enrollmentNo': user.enrollmentNo,
            'name': user_detail.name if user_detail else None,
            'alias': user_detail.alias if user_detail else None,
            'year': user_detail.year if user_detail else None,
            'isDeveloper': user_detail.isDeveloper if user_detail else False,
            'profilePicture': profile_picture_url,
            'is_reviewee': user.is_reviewee,
            'is_reviewer': user.is_reviewer,
            'is_admin': user.is_admin,
        }

    except User.DoesNotExist:
        return {'error': 'User not found'}

# API view to fetch user details by enrollment number
class GetUserByEnrollmentNoView(APIView):

    def get(self, request, enrollmentNo, *args, **kwargs):
        # Fetch user details using enrollment number
        user_details = get_user_from_enrollment_no(enrollmentNo)

        # If user not found, return a 404 error
        if 'error' in user_details:
            return Response(user_details, status=status.HTTP_404_NOT_FOUND)

        # Otherwise, return the user details
        return Response(user_details, status=status.HTTP_200_OK)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def delete_user(request, enrollmentNo):
    try:
        # Fetch the user by enrollmentNo
        user = get_object_or_404(User, enrollmentNo=enrollmentNo)
        
        # Delete the user
        user.delete()
        
        # Return a success response
        return JsonResponse({'message': 'User deleted successfully.'}, status=204)
    except Exception as e:
        # Handle any potential errors
        return JsonResponse({'error': str(e)}, status=500)
