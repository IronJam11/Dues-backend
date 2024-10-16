from django.http import JsonResponse
from ideasapp.models import Idea, Comment

def all_ideas_view(request):
    """
    View to return all ideas along with their details and associated users.
    """
    ideas = Idea.objects.all()

    # Prepare the data to return
    ideas_data = []
    for idea in ideas:
        # Get the related comments for the idea
        comments = idea.comments.all()
        comments_data = [
            {
                'id': comment.id,
                'user': comment.user.enrollmentNo,  # Adjust this to show what you need from user
                'comment_text': comment.comment_text,
                'created_at': comment.created_at,
            }
            for comment in comments
        ]

        # Get the associated users for the idea (assuming a many-to-many relationship)
        users = idea.users.all()  # Adjust based on the actual field name for the users relation
        users_data = [
            {
                'id': user.id,
                'enrollmentNo': user.enrollmentNo,
                'email': user.email,  # You can include other fields if necessary
            }
            for user in users
        ]

        # Prepare idea data
        idea_data = {
            'title': idea.title,
            'description': idea.description,
            'user': idea.created_by.enrollmentNo,  # Adjust based on what you want to show about the user
            'status': idea.status,
            'created_at': idea.created_at,
            'updated_at': idea.updated_at,
            'for_votes': idea.for_votes,
            'against_votes': idea.against_votes,
            'links': idea.links,  # Since links is an ArrayField, it will return a list
            'unique_name': idea.unique_name,
            'comments': comments_data,  # Add comments data
            'users': users_data,  # Add associated users data
        }

        ideas_data.append(idea_data)

    # Return the data as JSON
    return JsonResponse({'ideas': ideas_data})