from django.db import models
from userapp.models import User
from assignmentsapp.models import Assignment
from ideasapp.models import Idea


class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="sender")
    receivers = models.ManyToManyField(User,blank=True,related_name="receivers")
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True) 
    assignment = models.ForeignKey(Assignment,blank=True,null=True, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea,blank=True,null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.message

class PointsUpdateNotification: 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
    type = models.TextField()


