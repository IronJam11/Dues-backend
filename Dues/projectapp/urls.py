from django.urls import path
from .views.new_project import createNewProject, deleteProject
from .views.all_projects import get_user_projects
from .views.all_assignments import project_assignments_view
from .views.project_handling import project_detail_view

urlpatterns = [
    path('new-project/', createNewProject, name='create_new_project'),
    path('user-projects/', get_user_projects, name='get_user_projects'),
    path('delete/<str:roomname>/', deleteProject, name='delete-project'),
    path('project-details/<str:roomname>/', project_detail_view, name='project_details'),
    path('assignments/<str:roomname>/', project_assignments_view,name="get_all_assignments")
]
