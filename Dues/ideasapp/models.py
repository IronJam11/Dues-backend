from django.db import models
from userapp.models import User
from django.contrib.postgres.fields import ArrayField
import json 

class Idea(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('on hold', 'On Hold'),
        ('implemented', 'Implemented'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    users = models.ManyToManyField(User, related_name='contributers')  # Changed to ManyToManyField
    created_by = models.ForeignKey(User,related_name="initiator", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    for_votes = models.IntegerField(default=0)
    against_votes = models.IntegerField(default=0)
    links = ArrayField(models.URLField(), blank=True, default=list)
    deadline = models.DateTimeField(null=True, blank=True)
    unique_name = models.SlugField()

    def __str__(self):
        return self.title
    
    def get_links(self):
        return json.loads(self.links)

    def set_links(self, links_array):
        self.links = json.dumps(links_array)

class Comment(models.Model):
    idea = models.ForeignKey(Idea,on_delete=models.CASCADE,related_name="comments")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user")
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Comment by {self.user} on {self.idea.title}'

    

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference to the User
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)  # Reference to the Idea
    vote_type = models.CharField(max_length=10, choices=[('for', 'For'), ('against', 'Against')])  # 'for' or 'against'
    created_at = models.DateTimeField(auto_now_add=True)  # Track when the vote was created

    class Meta:
        unique_together = ('user', 'idea')  # Ensure a user can only vote once per idea

    def __str__(self):
        return f"{self.user.username} voted {self.vote_type} on {self.idea.unique_name}"