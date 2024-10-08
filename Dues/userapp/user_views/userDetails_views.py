from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings
from userapp.models import User, UserDetails
from django.core.files.storage import default_storage

def get_user_from_access_token(token):
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')

        if user_id is not None:
            user = User.objects.get(id=user_id)
            user_detail = UserDetails.objects.filter(user=user).first()
            profile_picture_url = default_storage.url(user_detail.profilePicture.name) if user_detail.profilePicture else ""

            return {
                'id': user.id,
                'email': user.email,
                'enrollmentNo': user.enrollmentNo,
                'name': user_detail.name,
                'alias': user_detail.alias,
                'year': user_detail.year,
                'isDeveloper': user_detail.isDeveloper,
                'profilePicture': profile_picture_url,
                'is_reviewee': user.is_reviewee,
                'is_reviewer': user.is_reviewer,
                'is_admin': user.is_admin,
            }
        else:
            return {'error': 'Invalid token: User ID not found'}

    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.DecodeError:
        return {'error': 'Error decoding token'}
    except User.DoesNotExist:
        return {'error': 'User not found'}

class GetUserFromTokenView(APIView):

    def get(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header is None or not auth_header.startswith('Bearer '):
            return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)

        token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'
        
        user_details = get_user_from_access_token(token)

        return Response(user_details, status=status.HTTP_200_OK)
