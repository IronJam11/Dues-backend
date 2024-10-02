from django.urls import path
from .views.new_project import createNewProject, deleteProject
from .views.all_projects import get_user_projects

urlpatterns = [
    path('new-project/', createNewProject, name='create_new_project'),
    path('user-projects/', get_user_projects, name='get_user_projects'),
    path('delete/<str:roomname>/', deleteProject, name='delete-project'),
]
