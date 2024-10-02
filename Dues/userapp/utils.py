from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.middleware.csrf import get_token

def decode_jwt_token(request):
    # Get JWT from cookies
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('JWT token not found.')

    # Fetch the CSRF token from headers
    # print("hello")
    # print("hello")
    # print("hello")
    # print("hello")
    # print("hello")
    # csrf_token = request.META.get('HTTP_X_CSRF_TOKEN')  # CSRF token sent in headers
    # if not csrf_token:
    #     raise AuthenticationFailed('CSRF token not found.')

    # # Validate the CSRF token
    # print("expected:- ")
    # print(csrf_token)
    # expected_csrf_token = get_token(request)
    # print("but:- ")
    # print(expected_csrf_token)  # Get the CSRF token from the session
    # if csrf_token != expected_csrf_token:
    #     raise AuthenticationFailed('Invalid CSRF token.')
    print("hello")
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