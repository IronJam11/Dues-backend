import datetime
from django.contrib.auth import login # type: ignore
from django.views.decorators.csrf import csrf_exempt  # type: ignore
from rest_framework.views import APIView  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.exceptions import AuthenticationFailed  # type: ignore
from .models import User, UserDetails
from .serializers import UserSerializer
from .jwt_utils import decode_jwt, check_jwt_token, check_jwt_token_using_header  # Import your JWT utilities
from rest_framework.decorators import api_view
from django.http import JsonResponse
import jwt
from django.conf import settings

# Register View
class Register(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


import jwt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings  # Import your settings for secret key
from .models import UserDetails  # Import your UserDetails model if applicable
from rest_framework import status

import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

def decode_jwt_token(request):
    token = request.COOKIES.get('jwt')  # Get JWT from cookies
    if not token:
        raise AuthenticationFailed('JWT token not found.')
    
    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token.')

@api_view(['GET'])
def get_credentials(request):
    # Retrieve the JWT from cookies
    jwt_token = request.COOKIES.get('jwtToken')

    if not jwt_token:
        return Response({"error": "No JWT token found in cookies."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        # Decode the JWT to extract the enrollment number
        payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        enrollment_no = payload.get('enrollmentNo')

        # Fetch the user's details using the enrollment number
        user = User.objects.get(enrollmentNo=enrollment_no)
        user_details = UserDetails.objects.get(user=user)

        # Create a response with the relevant user information
        response_data = {
            'name': user_details.name,
            'alias': user_details.alias,
            'profilePicture': user_details.profilePicture.url if user_details.profilePicture else None,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return Response({"error": "JWT token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"error": "Invalid JWT token."}, status=status.HTTP_401_UNAUTHORIZED)
    except UserDetails.DoesNotExist:
        return Response({"error": "User details not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

# Login View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import login
from django.conf import settings
import jwt
import datetime
from .serializers import UserSerializer

class Login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed("User not found")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")

        payload = {
            'id': user.id,
            'enrollmentNo': user.enrollmentNo,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        response = Response()
        
        # Set the JWT as a cookie
        response.set_cookie(
            key='jwtToken',
            value=token,
            httponly=True,  # Make it HttpOnly
            samesite='Lax',  # Adjust based on your requirements
            secure=True,    # Use secure flag for HTTPS
            max_age=3600    # Set expiration to 1 hour (60 * 60 seconds)
        )

        # Log the user in
        

        # Serialize user data
        serializer = UserSerializer(user)
        
        # Set response data
        response.data = {
            'message': 'Login successful',
            'email': email,
            'enrollmentNo': serializer.data['enrollmentNo'],
            'jwt': token
        }

        return response


# Current User View
@csrf_exempt
class CurrentUserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        payload = decode_jwt(token)
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

# Logout View
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

class LogoutView(APIView):
    def get(self, request):
        response = Response()

        try:
            # Decode the JWT token
            payload = decode_jwt_token(request)
            print(f"Decoded JWT details: {payload}")

            # Delete the 'jwt' cookie
            response.delete_cookie('jwt')
            response.data = {'message': 'Logout successful', 'user_details': payload}
        except AuthenticationFailed as e:
            response.data = {'error': str(e)}
            response.status_code = 400

        return response

# Create User Details View
@api_view(['POST'])
def create_user_details(request):
    try:
        # Decode the JWT token to get the payload
        payload = decode_jwt_token(request)
        enrollmentNo = payload['enrollmentNo']
        print(enrollmentNo)  # Get enrollmentNo from JWT payload
    except AuthenticationFailed as e:
        
        return Response({"error": str(e)}, status=400)

    name = request.data.get('name')
    alias = request.data.get('alias')
    year = request.data.get('year')
    print(enrollmentNo)

    # Convert 'isDeveloper' to boolean
    isDeveloper = request.data.get('isDeveloper', 'false').lower() == 'true'
    profilePicture = request.FILES.get('profilePicture')

    if not name:
        return Response({"error": "Missing required parameters."}, status=400)

    try:
        user = User.objects.get(enrollmentNo=enrollmentNo)
    except User.DoesNotExist:
        return Response({"error": "User with this enrollmentNo does not exist."}, status=404)

    # Create UserDetails object
    user_details = UserDetails.objects.create(
        user=user,
        name=name,
        alias=alias,
        year=year,
        isDeveloper=isDeveloper,
        profilePicture=profilePicture
    )

    return Response({"status": "User details created successfully."}, status=201)

# Check User Details View
@api_view(['GET'])
def check_user_details(request, enrollmentNo):
    try:
        user = User.objects.get(enrollmentNo=enrollmentNo)
        user_details_exists = UserDetails.objects.filter(user=user).exists()
        return Response({"exists": user_details_exists}, status=200)
    except User.DoesNotExist:
        return Response({"exists": False}, status=200)
    

from django.http import JsonResponse
from django.core.files.storage import default_storage
from .models import User, UserDetails

def get_all_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        user_details = []

        for user in users:
            user_detail = UserDetails.objects.filter(user=user).first()
            if user_detail:
                profile_picture_url = default_storage.url(user_detail.profilePicture.name) if user_detail.profilePicture else ""
                print(profile_picture_url)
                details = {
                    'email': user.email,
                    'enrollmentNo': user.enrollmentNo,
                    'is_reviewee': user.is_reviewee, 
                    'is_reviewer': user.is_reviewer,
                    'is_admin': user.is_admin,
                    'date_joined': user.date_joined,
                    'last_login': user.last_login,
                    'name': user_detail.name,
                    'alias': user_detail.alias,
                    'year': user_detail.year,
                    'isDeveloper': user_detail.isDeveloper,
                    'profilePicture': profile_picture_url,
                }
                user_details.append(details)

        return JsonResponse({'users': user_details}, safe=False)
    
def get_all_users_enrollmentNo(request):
    if request.method == 'GET':
        users = User.objects.all()
        user_details = {}

        for user in users:
            user_detail = UserDetails.objects.filter(user=user).first()
            if user_detail:
                profile_picture_url = (
                    default_storage.url(user_detail.profilePicture.name)
                    if user_detail.profilePicture else ""
                )
                details = {
                    'email': user.email,
                    'enrollmentNo': user.enrollmentNo,
                    'is_reviewee': user.is_reviewee, 
                    'is_reviewer': user.is_reviewer,
                    'is_admin': user.is_admin,
                    'date_joined': user.date_joined,
                    'last_login': user.last_login,
                    'name': user_detail.name,
                    'alias': user_detail.alias,
                    'year': user_detail.year,
                    'isDeveloper': user_detail.isDeveloper,
                    'profilePicture': profile_picture_url,
                }
                # Store details grouped by enrollmentNo
                user_details[user.enrollmentNo] = details

        return JsonResponse({'users': user_details}, safe=False)


from django.http import JsonResponse
from .models import User, UserDetails
 # Assuming this is where the helper function is
from django.core.files.storage import default_storage
from rest_framework.exceptions import AuthenticationFailed
from userapp.utils import decode_jwt_token

def get_user(request):
    if request.method == 'GET':
        try:
            # Decode the JWT token to get the payload
            payload = decode_jwt_token(request)
            enrollmentNo = payload.get('enrollmentNo')  # Get enrollmentNo from JWT payload
        except AuthenticationFailed as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Retrieve the user based on the enrollmentNo from the decoded token
        try:
            user = User.objects.get(enrollmentNo=enrollmentNo)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)

        # Retrieve user details
        user_detail = UserDetails.objects.filter(user=user).first()
        if user_detail:
            profile_picture_url = default_storage.url(user_detail.profilePicture.name) if user_detail.profilePicture else ""
            print(profile_picture_url)
            details = {
                'email': user.email,
                'enrollmentNo': user.enrollmentNo,
                'is_reviewee': user.is_reviewee,
                'is_reviewer': user.is_reviewer,
                'is_admin': user.is_admin,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'name': user_detail.name,
                'alias': user_detail.alias,
                'year': user_detail.year,
                'isDeveloper': user_detail.isDeveloper,
                'profilePicture': profile_picture_url,
            }
            user_details = details
        else:
            user_details = {
                'email': user.email,
                'enrollmentNo': user.enrollmentNo,
                'is_reviewee': user.is_reviewee,
                'is_reviewer': user.is_reviewer,
                'is_admin': user.is_admin,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
            }

        return JsonResponse(user_details, safe=False)

from django.http import JsonResponse
from django.db.models import Q

def search_users(request):
    if request.method == 'GET':
        search_query = request.GET.get('query', '')

        # Filter users based on the search query (enrollmentNo, name, alias)
        users = User.objects.filter(
            Q(enrollmentNo__icontains=search_query) |
            Q(userdetails__name__icontains=search_query) |
            Q(userdetails__alias__icontains=search_query)
        ).distinct()

        user_details_set = set()  # Use a set to ensure uniqueness
        user_details = []

        for user in users:
            user_detail = UserDetails.objects.filter(user=user).first()
            if user_detail:
                profile_picture_url = default_storage.url(user_detail.profilePicture.name) if user_detail.profilePicture else ""
                details = {
                    'email': user.email,
                    'enrollmentNo': user.enrollmentNo,
                    'is_reviewee': user.is_reviewee,
                    'is_reviewer': user.is_reviewer,
                    'is_admin': user.is_admin,
                    'date_joined': user.date_joined,
                    'last_login': user.last_login,
                    'name': user_detail.name,
                    'alias': user_detail.alias,
                    'year': user_detail.year,
                    'isDeveloper': user_detail.isDeveloper,
                    'profilePicture': profile_picture_url,
                }
                
                # Add to set to ensure uniqueness
                if user.enrollmentNo not in user_details_set:
                    user_details.append(details)
                    user_details_set.add(user.enrollmentNo)

        return JsonResponse({'users': user_details}, safe=False)


def get_all_users_by_email(request):
    if request.method == 'GET':
        users = User.objects.all()
        user_details = {}

        for user in users:
            user_detail = UserDetails.objects.filter(user=user).first()
            if user_detail:
                profile_picture_url = (
                    default_storage.url(user_detail.profilePicture.name)
                    if user_detail.profilePicture else ""
                )
                details = {
                    'email': user.email,
                    'enrollmentNo': user.enrollmentNo,
                    'is_reviewee': user.is_reviewee, 
                    'is_reviewer': user.is_reviewer,
                    'is_admin': user.is_admin,
                    'date_joined': user.date_joined,
                    'last_login': user.last_login,
                    'name': user_detail.name,
                    'alias': user_detail.alias,
                    'year': user_detail.year,
                    'isDeveloper': user_detail.isDeveloper,
                    'profilePicture': profile_picture_url,
                }
                # Store details grouped by email
                user_details[user.email] = details

        return JsonResponse({'users': user_details}, safe=False)