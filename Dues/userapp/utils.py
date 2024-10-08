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
    """
    Retrieves the enrollmentNo of the user based on the JWT token.
    """
    if request.method == 'GET':
        try:
            # Decode the JWT token to get the payload
            token = request.COOKIES.get('jwt')  # Assuming the JWT token is stored in cookies
            payload = decode_jwt_token_boolean(token)  # Decode the token and check for expiry

            if payload['is_token_expired']:
                return JsonResponse({"error": "Token has expired."}, status=401)

            enrollmentNo = payload.get('enrollmentNo')  # Get enrollmentNo from JWT payload
        except AuthenticationFailed as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Return the enrollmentNo as a JSON response
        return JsonResponse({"enrollmentNo": enrollmentNo}, safe=False)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)
    


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
