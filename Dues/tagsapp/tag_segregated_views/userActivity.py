from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from userapp.models import User, UserDetails
from userapp.utils import get_enrollment_no_from_token
from django.shortcuts import get_object_or_404
from tagsapp.models import Tag


class CheckUserTags(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Bearer '):
            return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)
            
        token = auth_header.split(' ')[1]
        enrollment_no_or_error = get_enrollment_no_from_token(token)
        if isinstance(enrollment_no_or_error, dict):  # Check if an error occurred during token decoding
            return Response(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)
            
        enrollment_no = enrollment_no_or_error
        user = get_object_or_404(User, enrollmentNo=enrollment_no)  # Fetch the user
        user_details = UserDetails.objects.filter(user=user).first()  # Fetch the corresponding UserDetails
        
        # Fetch tags for developer and designer
        developer_tag = get_object_or_404(Tag, name='Developer')
        designer_tag = get_object_or_404(Tag, name='Designer')
        first_year_tag = get_object_or_404(Tag,name='1Y')
        second_year_tag = get_object_or_404(Tag,name='2Y')
        third_year_tag = get_object_or_404(Tag,name='3Y')
        fourth_year_tag = get_object_or_404(Tag,name='4Y')
        fifth_year_tag = get_object_or_404(Tag,name='5Y')
        if user_details.year == 1 and first_year_tag not in user_details.tags.all():
            user_details.tags.add(first_year_tag)
        if user_details.year == 2 and second_year_tag not in user_details.tags.all():
            user_details.tags.add(second_year_tag)
        if user_details.year == 3 and third_year_tag not in user_details.tags.all():
            user_details.tags.add(third_year_tag)
        if user_details.year == 4 and fourth_year_tag not in user_details.tags.all():
            user_details.tags.add(fourth_year_tag)
        if user_details.year == 5 and fifth_year_tag not in user_details.tags.all():
            user_details.tags.add(fifth_year_tag)

        
        # Check if user is a developer and add the tag if not already present
        if user_details.isDeveloper and developer_tag not in user_details.tags.all():
            user_details.tags.add(developer_tag)

        # Check if user is a designer and add the tag if not already present
        if not user_details.isDeveloper and designer_tag not in user_details.tags.all():
            user_details.tags.add(designer_tag)

        # Return the updated user details
        return Response({'success': 'Tags checked and updated if necessary.'}, status=status.HTTP_200_OK)


class UserDetailWithTags(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Bearer '):
            return Response({"error": "Token not provided or incorrect format"}, status=status.HTTP_400_BAD_REQUEST)
        
        token = auth_header.split(' ')[1]
        enrollment_no_or_error = get_enrollment_no_from_token(token)
        if isinstance(enrollment_no_or_error, dict):  # Check if an error occurred during token decoding
            return Response(enrollment_no_or_error, status=status.HTTP_400_BAD_REQUEST)

        enrollment_no = enrollment_no_or_error
        user = get_object_or_404(User, enrollmentNo=enrollment_no)  # Fetch the user
        user_details = UserDetails.objects.filter(user=user).first()  # Fetch the corresponding UserDetails

        # Prepare the user details and associated tags
        user_data = {
            "name": user_details.name,
            "alias": user_details.alias,
            "year": user_details.year,
            "isDeveloper": user_details.isDeveloper,
            "level": user_details.level,
            "points": user_details.points,
            "profilePicture": user_details.profilePicture.url if user_details.profilePicture else None,
            "tags": []
        }

        # Fetch and include tags with their name, color, and description
        for tag in user_details.tags.all():
            user_data["tags"].append({
                "name": tag.name,
                "color": tag.color,
                "description": tag.description
            })

        return Response(user_data, status=status.HTTP_200_OK)
