from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from userapp.models import User
from userapp.serializers import UserSerializer
from django.conf import settings
import requests
import jwt
import datetime
from rest_framework import status
from django.http import JsonResponse

# OAuth2 settings
client_id = "Ql6I4IgAMGQo1upboRMXGbTcyP6w1WPfkTNaiayy"
client_secret = "OtelF9pdlZAF3BhK95fBpkE2H0SJv7plXcpDPJotdWLFhMxOR4HRN6OsE1eeb4wJDbABEqdVTkr1WxA29xvGFjwYjtDhuI6djBhxKbZx6YtbFv2dgBEaSpeh2XWSdjwq"
redirect_uri = 'http://localhost:5173/homepage'
success_string1 = 'yay'
request_token_url = 'https://channeli.in/open_auth/token/'
request_data_url = 'https://channeli.in/open_auth/get_user_data/'

# OAuth2 parameters
params = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'authorization_code',
    'code': '',
    'redirect_uri': redirect_uri,
    'state': success_string1
}
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class RequestAccessAPI(APIView):
    """
    API to redirect the user to the OAuth authorization page.
    """
    def get(self, request):
        auth_url = f"https://channeli.in/oauth/authorise?client_id={client_id}&redirect_uri={redirect_uri}&state={success_string1}"
        return redirect(auth_url)


class CallbackAPI(APIView):
    def get(self, request):
        auth_code = request.GET.get("code")
        if auth_code is None:
            return Response("Authorization code is missing", status=400)

        # Exchange the authorization code for an access token
        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri,
            'state': success_string1
        }
        token_response = requests.post(request_token_url, data=params)

        if token_response.status_code != 200:
            return Response("Failed to obtain access token", status=400)

        response_data = token_response.json()
        access_token = response_data.get('access_token')
        refresh_token = response_data.get('refresh_token')

        if not access_token:
            return Response("Access token is missing in the response", status=400)

        # Fetch user data using the access token
        headers = {"Authorization": f"Bearer {access_token}"}
        user_data_response = requests.get(request_data_url, headers=headers)

        if user_data_response.status_code != 200:
            return Response("Failed to get user data", status=400)

        user_data = user_data_response.json()
        enrollment_no = user_data.get('username')
        username = user_data['person'].get('fullName')
        email = user_data['contactInformation'].get('emailAddress')

        # Check if the user exists or create a new one
        user, created = User.objects.get_or_create(enrollmentNo=enrollment_no, defaults={'email': email})

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Redirect to frontend with tokens as query params
        frontend_redirect_url = f"http://localhost:5173/loading?access-token={access_token}&refresh-token={refresh_token}"
        return redirect(frontend_redirect_url)
    




class CallbackAPIDetails(APIView):
    def get(self, request):
        auth_code = request.GET.get('code')
        if auth_code is None:
            return Response("Authorization code is missing", status=400)

        # Exchange the authorization code for an access token
        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri,
            'state': success_string1
        }
        token_response = requests.post(request_token_url, data=params)

        if token_response.status_code != 200:
            return Response("Failed to obtain access token", status=400)

        response_data = token_response.json()
        access_token_initial = response_data.get('access_token')
        refresh_token_intitial  = response_data.get('refresh_token')

        if not access_token_initial:
            return Response("Access token is missing in the response", status=400)

        # Fetch user data using the access token
        headers = {"Authorization": f"Bearer {access_token_initial}"}
        user_data_response = requests.get(request_data_url, headers=headers)

        if user_data_response.status_code != 200:
            return Response("Failed to get user data", status=400)

        user_data = user_data_response.json()
        enrollment_no = user_data.get('username')
        username = user_data['person'].get('fullName')
        email = user_data['contactInformation'].get('emailAddress')

        # Check if the user exists or create a new one
        user, created = User.objects.get_or_create(enrollmentNo=enrollment_no, defaults={'email': email})

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Redirect to frontend with tokens as query params
        
        return JsonResponse({
            'accessToken': access_token,
            'refreshToken':refresh_token
        })