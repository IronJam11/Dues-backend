from django.urls import path
from .views import Register,Login,LogoutView,get_credentials
from .views import create_user_details,check_user_details, get_all_users, get_user, search_users, get_all_users_enrollmentNo, get_all_users_by_email, LogoutView
from .auth import RequestAccessAPI, CallbackAPI, LogoutUser
from .edit_views import update_user_details
from .jwt_utils import VerifyTokenView
from .utils import get_user_enrollment_no

urlpatterns = [
    path('register/', Register.as_view()),
    path('login/', Login.as_view()),
    path('logout/', LogoutView.as_view()),
    path('login2/', create_user_details),
    path('check-user-details/<str:enrollmentNo>/',check_user_details),
    path("auth/oauth/", RequestAccessAPI.as_view(), name='login'),
    path("homepage/", CallbackAPI.as_view(), name='home'),
    path('logout2/', LogoutUser.as_view()),
    path('all-users-details/',get_all_users),
    path('all-users-details-enrollmentNo/',get_all_users_enrollmentNo),
    path('all-users-details-email/',get_all_users_by_email),
    path('user-info/',get_user),
    path('change-user-info/',update_user_details),
    path('search/', search_users, name='search_users'),
    path('check/',VerifyTokenView.as_view()),
    path('get-enrollmentNo/', get_user_enrollment_no)

]