from django.urls import path
from .views import Register,Login,LogoutView,get_credentials
from .views import create_user_details,check_user_details, get_all_users, get_user, search_users, get_all_users_enrollmentNo, get_all_users_by_email
from .auth import RequestAccessAPI, CallbackAPI, CallbackAPIDetails
from .edit_views import update_user_details
from .jwt_utils import VerifyTokenView
from .utils import get_user_enrollment_no
from userapp.user_views.login_views import LoginView, LogoutView
from userapp.user_views.userDetails_views import GetUserFromTokenView, CheckUserDetailsView
from userapp.user_views.token_auth import TokenCheckView


urlpatterns = [
    path('register/', Register.as_view()),
    # path('login/', Login.as_view()),

    path('set-user-details/', create_user_details, name="set_user_details"),
    path('check-user-details/<str:enrollmentNo>/',check_user_details),

    path("auth/oauth/", RequestAccessAPI.as_view(), name='login'),
    path("homepage/", CallbackAPI.as_view(), name='home'),
    path("callback/", CallbackAPIDetails.as_view(), name='callback'),
    path("check-user-details/",CheckUserDetailsView.as_view(), name="check_user_details"),



    path('all-users-details/',get_all_users),
    path('all-users-details-enrollmentNo/',get_all_users_enrollmentNo),
    path('all-users-details-email/',get_all_users_by_email),
    path('user-info/',get_user),
    path('change-user-info/',update_user_details),
    path('search/', search_users, name='search_users'),
    path('get-enrollmentNo/', get_user_enrollment_no),


    path('login/',LoginView.as_view(),name="login_user"),
    path('logout/', LogoutView.as_view()),
    path('user-data/',GetUserFromTokenView.as_view(),name="user_details"),
    path('check/', TokenCheckView.as_view(), name='token-check'),
    
]