from django.urls import path
from .views.assignment_handling import get_user_assignments_reviewee, get_user_assignments_reviewer, delete_assignment
from .views.new_assignment import create_assignment
from .views.subtasks import create_subtask, get_subtasks_by_assignment
from assignmentsapp.views.submit_assignment import submit_assignment, list_submissions

urlpatterns = [
    path('get-all/reviewee/<str:enrollment_no>/', get_user_assignments_reviewee, name='get_user_assignments_reviewee'),
    path('get-all/reviewer/<str:enrollment_no>/', get_user_assignments_reviewer, name='get_user_assignments_reviewer'),
    path('create-assignment/', create_assignment, name="create_new_assignment"),
    path('delete/<str:unique_assignment_name>/', delete_assignment, name='delete-assignment'),
    path('subtask/create/',create_subtask,name="new_subtask"),
    path('subtasks/<str:unique_name>/', get_subtasks_by_assignment, name='get_subtasks_by_assignment'),
    path('submit-assignment/', submit_assignment, name="submit_assignment"),
    path('list-submissions/<str:unique_name>/',list_submissions,name="list_all_submissions"),
]
