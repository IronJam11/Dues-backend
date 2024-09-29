from django.urls import path
from .views import Register,Login,LogoutView
from .views import AllUserView, create_user_details,check_user_details, get_all_users, get_user, search_users
from .auth import RequestAccessAPI, CallbackAPI, LogoutUser
from .edit_views import update_user_details

urlpatterns = [
    path('register/', Register.as_view()),
    path('login/', Login.as_view()),
    path('logout/', LogoutUser.as_view()),
    path('all-users/',AllUserView.as_view()),
    path('login2/', create_user_details),
    path('check-user-details/<str:enrollmentNo>/',check_user_details),
    path("auth/oauth/", RequestAccessAPI.as_view(), name='login'),
    path("homepage/", CallbackAPI.as_view(), name='home'),
    path('logout2/', LogoutUser.as_view()),
    path('all-users-details/',get_all_users),
    path('user/<int:enrollmentNo>/',get_user),
    path('change-user-info/',update_user_details),
    path('search/', search_users, name='search_users'),

]