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

# Login View
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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(
            key='jwt', 
            value=token, 
            httponly=True, 
            samesite='None', 
            secure=True  # Make sure you're serving over HTTPS in production
        )
        print(request.COOKIES.get('jwt'))
        # print(f"JWT Cookie set: {response.cookies['jwt']}") 
        serializer = UserSerializer(user)
        response.data = {
            'jwt': token,
            'email': email,
            'enrollmentNo': serializer.data['enrollmentNo']
        }
        login(request,user)
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
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {'message': 'success'}
        return response

# All Users View
class AllUserView(APIView):
    def get(self, request):
        if not check_jwt_token_using_header(request):
            raise AuthenticationFailed("Unauthenticated!")

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

# Create User Details View
@api_view(['POST'])
def create_user_details(request):
    enrollmentNo = request.data.get('enrollmentNo')
    name = request.data.get('name')
    alias = request.data.get('alias')
    year = request.data.get('year')

    # Convert 'isDeveloper' to boolean
    isDeveloper = request.data.get('isDeveloper', 'false').lower() == 'true'
    profilePicture = request.FILES.get('profilePicture')

    if not enrollmentNo or not name:
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
    


def get_user(request,enrollmentNo):
    if request.method == 'GET':
        user = User.objects.get(enrollmentNo=enrollmentNo)
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
            user_details=(details)

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

