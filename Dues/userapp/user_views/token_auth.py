from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.conf import settings
import jwt
from userapp.models import User
from rest_framework.permissions import AllowAny



class TokenCheckView(APIView):
    # permission_classes = [AllowAny]
    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response['Access-Control-Allow-Headers'] = 'Authorization1, Authorization2, content-type'
        return response
    
    def get(self, request):
      
        token = request.headers.get('Authorization')

        # Check if tokens are present
        if token:
            access_token = token.split(" ")[0]  # Remove "Bearer"
            refresh_token = token.split(" ")[1]  # Remove "Bearer"
            try:
                # Decode access token to get user
                decoded_access = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
                user = User.objects.get(id=decoded_access['user_id'])
                
                # Both tokens are valid
                return Response({
                    'valid': True,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'enrollmentNo': user.enrollmentNo,
                        # Add any other user details you want to return
                    }
                })

            except (jwt.ExpiredSignatureError, jwt.DecodeError):
                # Access token is invalid
                try:
                    # Attempt to decode refresh token
                    decoded_refresh = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
                    user = User.objects.get(id=decoded_refresh['user_id'])

                    # Generate new access token
                    new_access_token = AccessToken.for_user(user)

                    return Response({
                        'valid': True,
                        'access_token': str(new_access_token),
                        'refresh_token': refresh_token,  # Keep the old refresh token
                        'user': {
                            'id': user.id,
                            'email': user.email,
                            'enrollmentNo': user.enrollmentNo,
                        }
                    })

                except (jwt.ExpiredSignatureError, jwt.DecodeError):
                    # Both tokens are invalid
                    return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)


