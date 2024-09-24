from django.db import models
from userapp.models import User


class Assignment(models.Model):
   name = models.CharField(max_length=255)
   description =  models.TextField()
   total_points = models.IntegerField()
   color = models.CharField(max_length=7,default='#FFFFFF')
   time_assigned = models.DateTimeField(null=False,blank=False)
   reviewers = models.ManyToManyField(User, related_name='assignments_to_review', blank=True, null= True)
   reviewees = models.ManyToManyField(User, related_name='assignments_to_be_reviewed',blank=True, null= True)
   deadline = models.DateTimeField(null=False,blank=False) 
   def __str__(self):
        return self.name
   
   
class SubTask(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    description = models.TextField()



class Iteration(models.Model):
    title = models.CharField(max_length=255)
    feedback =  models.TextField()
    by = models.ForeignKey(User,on_delete=models.CASCADE)
    for_user = models.ForeignKey(User,on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE)
    time_assigned = models.DateTimeField(null=False,blank=False)




class Submission(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE)
    points_awarded = models.IntegerField(black = True, null = True)

