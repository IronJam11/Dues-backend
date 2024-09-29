from rest_framework.views import APIView
from rest_framework.response import Response
import os
import requests
from django.shortcuts import redirect
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import login, logout, authenticate
from userapp.models import User
from userapp.serializers import UserSerializer



client_id = "Ql6I4IgAMGQo1upboRMXGbTcyP6w1WPfkTNaiayy"
client_secret = "OtelF9pdlZAF3BhK95fBpkE2H0SJv7plXcpDPJotdWLFhMxOR4HRN6OsE1eeb4wJDbABEqdVTkr1WxA29xvGFjwYjtDhuI6djBhxKbZx6YtbFv2dgBEaSpeh2XWSdjwq"
redirect_uri = 'http://localhost:8000/users/homepage/'
success_string1 = 'yay'
request_token_url = 'https://channeli.in/open_auth/token/'
request_data_url = 'https://channeli.in/open_auth/get_user_data/'


params = {'client_id': client_id,
        'client_secret': client_secret, 
        'grant_type': 'authorization_code',
        'code': '' ,
        'redirect_uri' : redirect_uri,
        'state': success_string1}

class RequestAccessAPI(APIView):
    def get(self, request):
        print("Hello")
        URL= 'https://channeli.in/oauth/authorise' + "?client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&state=" + success_string1
        return redirect(URL)

class CallbackAPI(APIView):
    
    def get(self, request):
        print("hello")
        print("We have the code(user has given permission)")
        AUTH_CODE = request.GET.get("code")

        if AUTH_CODE is None:
            return Response("Authorization code is missing", status=400)

        params['code'] = AUTH_CODE
        r = requests.post(request_token_url, data=params)

        # Check if the response was successful
        if r.status_code != 200:
            return Response("Failed to obtain access token", status=400)

        response_data = r.json()
        access_token = response_data.get('access_token')
        refresh_token = response_data.get('refresh_token')

        if access_token is None:
            return Response("Access token is missing in the response", status=400)

        print(access_token)
        print(refresh_token)

        # We have the access token and now will get the user information from it
        header = {
            "Authorization": "Bearer " + access_token,
        }
        
        r = requests.get(url=request_data_url, headers=header)

        # Check if the user data request was successful
        if r.status_code != 200:
            return Response("Failed to get user data", status=400)

        data = r.json()

        # verifying that the logged in user is from IMG and if yes then adding to our user database is not already
        enrollment_no = data.get('username')
        if enrollment_no is None:
            return Response("Enrollment number is missing in user data", status=400)

        username = data['person'].get('fullName')

        # Uncomment this section to handle user creation and login
        # if User.objects.filter(enrollment_no=enrollment_no).exists():
        #     # means that user already exists
        #     print("User already exists, so logging in the user")
        #     user = User.objects.get(enrollment_no=enrollment_no)
        #     try:
        #         login(request=request, user=user)
        #         print("Successful login for ")
        #         print(request.user)
        #         return redirect("http://localhost:5173/document")
        #     except Exception as e:
        #         return Response("Unable to login", status=500)
        # else:
        #     print("User does not exist hence now adding user")
        #     user = User.objects.create(username=username, enrollment_no=enrollment_no)
        #     print(user)
        #     try:
        #         login(request, user)
        #         print("Successful login for ", request.user)
        #         return redirect("http://localhost:5173/document", user)
        #     except:
        #         return Response("Unable to log in", status=500)

        print(enrollment_no)
         

        # Add a final return statement to avoid returning None
        return Response({"status": "User data processed", "enrollment_no": enrollment_no}, status=200)


from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
import jwt
import logging

# Set up logging

class LogoutUser(APIView):
    # permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        token = request.COOKIES.get('jwt')  # Get the JWT from cookies

        # Log the token before deletion
        print(f"Token before deletion: {token}")

        # Log the user out
        # logout(request)  # Log the user out
        
        # Prepare response
        response = Response({"message": "Logout was successful."})
        
        # Delete the JWT cookie
        response.delete_cookie('jwt')
        response.set_cookie('jwt', '', max_age=0, httponly=True, secure=True, samesite='Strict')

        # Log that the token has been deleted
        print("Token deleted.")

        return response
