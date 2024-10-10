from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.middleware.csrf import get_token
from django.http import JsonResponse

def decode_jwt_token(request):
    # Get all cookies and print them for debugging purposes
    cookies = request.COOKIES
    if cookies:
        print("All cookies received:")
        for key, value in sorted(cookies.items()):  # Sorting cookies by their keys
            print(f"{key}: {value}")
    else:
        print("No cookies received")

    # Get JWT and CSRF token from cookies
    token = request.COOKIES.get('jwtToken')
    csrf = request.COOKIES.get('csrftoken')
    
    # Print specific tokens
    print("CSRF Token:", csrf)
    print("JWT Token:", token)

    if not token:
        print("No JWT token found")
        raise AuthenticationFailed('JWT token not found.')

    print("Proceeding with decoding the token...")

    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token.')




import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
import datetime

def decode_jwt_token_boolean(token):
    if not token:
        raise AuthenticationFailed('Authentication token not provided')
    print(token)

    try:
        # Decode the token using the secret key from settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        # Extract the token expiration time and check if it's expired
        exp = datetime.datetime.utcfromtimestamp(payload['exp'])
        is_expired = exp < datetime.datetime.utcnow()

        # Return the enrollmentNo, whether the token is expired, and the token itself
        return {
            'enrollmentNo': payload['enrollmentNo'],
            'is_token_expired': is_expired,
            'token': token
        }
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')

def get_user_enrollment_no(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method. Only GET is allowed.'}, status=405)

    # Get the JWT token from cookies
    auth_header = request.headers.get('Authorization')


    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

    token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'
    print("token",token)

    enrollment_no_or_error = get_enrollment_no_from_token(token)

   
    


import jwt
from django.conf import settings
from userapp.models import User

def get_enrollment_no_from_token(token):
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        id = decoded_token.get('user_id') 
        user = User.objects.get(id = id)
        enrollment_no = user.enrollmentNo # Adjust according to your token's payload structure

        if enrollment_no:
            return enrollment_no
        else:
            return {'error': 'Invalid token: Enrollment number not found'}

    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.DecodeError:
        return {'error': 'Error decoding token'}
