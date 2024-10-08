from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from userapp.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email= request.data.get('email')
        password = request.data.get('password')

        # Authenticate the user
        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed("User not found")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")

        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh-token': str(refresh),
                'access-token': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid enrollmentNo or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken



class LogoutView(APIView):
    def get(self, request, *args, **kwargs):
        # Extract the refresh token from the request headers
        refresh_token = request.headers.get('Authorization1')  
        print("refresh token",refresh_token)# Expecting format: 'Bearer <token>'

        # Validate the refresh token format
        if not refresh_token or not refresh_token.startswith('Bearer '):
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract the actual token
        refresh_token = refresh_token.split(' ')[1]  # Get the token after 'Bearer '
        print(refresh_token)

        try:
            # Blacklist the refresh token using Simple JWT
            refresh = RefreshToken(refresh_token)
            # Call the blacklist method to mark the token as blacklisted
            refresh.blacklist()

            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({'error': 'Invalid or expired refresh token', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)



