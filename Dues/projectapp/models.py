from django.db import models
from userapp.models import User
from assignmentapp.models import Assignment
# Create your models here.

class Project(models.Model):
   name = models.CharField(max_length=255)
   description =  models.TextField()
   date_started = models.DateTimeField(null=False,blank=False)
   group_image = models.ImageField(upload_to='groupImages/',default="")
   participants = models.ManyToManyField(User, related_name='group_participants', blank=False)
   time_assigned = models.DateTimeField(null=False,blank=False)
   deadline = models.DateTimeField(null=False,blank=False)
   roomname = models.TextField(unique=True)
   assignments = models.ManyToManyField(Assignment, related_name='group_assignments')
   
   def __str__(self):
        return self.name
   