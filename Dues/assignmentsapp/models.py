from django.db import models
from userapp.models import User
import time 
from django.db import models
from userapp.models import User
from django.utils import timezone  # Import timezone for default

class Assignment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    total_points = models.IntegerField()
    color = models.CharField(max_length=7, default='#FFFFFF')
    time_assigned = models.DateTimeField(auto_now_add=True)  # Set default to current time
    reviewers = models.ManyToManyField(User, related_name='assignments_to_review', blank=True)
    reviewees = models.ManyToManyField(User, related_name='assignments_to_be_reviewed', blank=True)
    deadline = models.DateTimeField(null=False, blank=False)
    unique_name = models.CharField(max_length=512, blank=True, unique=True)  # Store the unique name as a combination

    class Meta:
        unique_together = ('name', 'time_assigned')  # Enforce uniqueness of name + time_assigned

    def save(self, *args, **kwargs):
        # Combine the name and time_assigned to create the unique_name
        self.unique_name = f"{self.name}_{self.time_assigned.strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)  # Call the "real" save() method

    def __str__(self):
        return self.name

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    points_awarded = models.IntegerField(blank=True, null=True)
    description = models.TextField(default="")
    time_submitted = models.DateTimeField(auto_now_add=True) 
    link = models.URLField(null=True, blank=True)
    status = models.TextField(default="To be Reviewed")
    unique_submission_name = models.TextField(blank=True,null=True)

     # Automatically set to current time
    # You don't need to add the files here, as they will be in the related SubmissionFile model

    def __str__(self):
        return f"{self.user.username} - {self.assignment.name}"
    
class SubmissionFile(models.Model):
    submission = models.ForeignKey(Submission, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')  # Store in a specific directory

    def __str__(self):
        return f"File for {self.submission.user.enrollmentNo}'s submission"

class Iteration(models.Model):
    title = models.CharField(max_length=255)
    feedback =  models.TextField()
    by = models.ForeignKey(User,on_delete=models.CASCADE, related_name="reviewer")
    for_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="reviewee")
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE)
    time_assigned = models.DateTimeField(auto_now_add=True)
    submission = models.ForeignKey(Submission,on_delete=models.CASCADE)

class SubTask(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    description = models.TextField()


class CompletedAssignment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="for_user")
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE)
    reviewed_by = models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE,related_name="by_user")
    score = models.IntegerField()


