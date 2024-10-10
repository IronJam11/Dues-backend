from django.urls import path
from .views.assignment_handling import GetUserAssignmentsRevieweeView, GetUserAssignmentsReviewerView
from .views.new_assignment import create_assignment
from .views.subtasks import create_subtask, get_subtasks_by_assignment
from assignmentsapp.views.submit_assignment import submit_assignment, list_submissions_all, list_my_submissions_all
from assignmentsapp.views.review_assignment import submission_detail, ReviewSubmission
from assignmentsapp.views.permission_views import check_assignment_permission
from assignmentsapp.views.delete_assignment import delete_assignment
from assignmentsapp.views.iterations_views import GetUserIterations
urlpatterns = [
    path('get-all/reviewee/', GetUserAssignmentsRevieweeView.as_view(), name='get_user_assignments_reviewee'),
    path('get-all/reviewer/', GetUserAssignmentsReviewerView.as_view(), name='get_user_assignments_reviewer'),
    path('create-assignment/', create_assignment, name="create_new_assignment"),
    path('check-permission/<str:unique_name>/', check_assignment_permission, name="check_for_permission"),
    path('delete/<str:unique_name>/', delete_assignment, name='delete-assignment'),
    path('subtask/create/',create_subtask,name="new_subtask"),
    path('subtasks/<str:unique_name>/', get_subtasks_by_assignment, name='get_subtasks_by_assignment'),
    path('submit-assignment/', submit_assignment, name="submit_assignment"),
    path('list-submissions/<str:unique_name>/',list_submissions_all,name="list_all_submissions"),
    path('list-my-submissions/<str:unique_name>/',list_my_submissions_all,name="list_all_submissions"),
    path('submission-details/<str:unique_submission_name>/',submission_detail),
    path('review/',ReviewSubmission.as_view(),name="review_submission"),
    path('iterations/<str:unique_name>/',GetUserIterations.as_view(),name="review_submission")
]
