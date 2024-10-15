from django.urls import path
from .views import CreateTagView, TagListView
from tagsapp.tag_segregated_views.userActivity import CheckUserTags, UserDetailWithTags

urlpatterns = [
    path('create-tag/', CreateTagView.as_view(), name='create-tag'),
    
    path('', TagListView.as_view(), name='tag-list'),
    path('check-user-tags/', CheckUserTags.as_view(), name='check_user_tags'),
    
    # URL for fetching user details with associated tags
    path('user-details-tags/', UserDetailWithTags.as_view(), name='get_user_details_with_tags'),
]

