from django.urls import path
from ideasapp.views.allIdeas import all_ideas_view
from ideasapp.views.createIdea import create_idea_view
from ideasapp.views.voting import userVotingDetails

urlpatterns = [
    path('all-ideas/', all_ideas_view, name='display_all_ideas'),
    path('create-new-idea/',create_idea_view,name='create_new_idea'),
    path('user-voting-details/',userVotingDetails,name="user_voting_details")
    
]