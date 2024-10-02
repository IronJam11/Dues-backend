import jwt  # type: ignore
from rest_framework.exceptions import AuthenticationFailed
from .models import User

def decode_jwt(token):
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token expired!")
    except jwt.DecodeError:
        raise AuthenticationFailed("Invalid token!")

# Utility function to check for JWT token from cookies
def check_jwt_token(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return False
    try:
        payload = decode_jwt(token)
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return False
        return True
    except AuthenticationFailed:
        return False

# Utility function to check for JWT token from headers
def check_jwt_token_using_header(request):
    auth = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth:
        return False

    try:
        token = auth.split(' ')[1]  # Get the token from the Authorization header
        payload = decode_jwt(token)
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return False
        return True
    except AuthenticationFailed:
        return False



from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import decode_jwt_token_boolean
from rest_framework.exceptions import AuthenticationFailed



class VerifyTokenView(APIView):
    def get(self, request):
        # Extract the token from the cookies
        token = request.COOKIES.get('jwt')  # Adjust the cookie name if necessary

        if not token:
            return Response({'error': 'Authentication token not found'}, status=400)

        try:
            # Decode the token and check if it's expired
            token_details = decode_jwt_token_boolean(token)

            # Return the token details
            return Response({
                'enrollmentNo': token_details['enrollmentNo'],
                'is_token_expired': token_details['is_token_expired'],
                'token': token_details['token']
            })
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=400)

