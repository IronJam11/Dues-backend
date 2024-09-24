from django.db import models
from userapp.models import User
# Create your models here.
class Tag(models.Model):
   name = models.CharField(max_length=255)
   description = models.CharField(max_length=255)
   condition = models.CharField()
   user = models.ForeignKey(User,on_delete=models.CASCADE)
   color = models.CharField(max_length=7,default='#FFFFFF')
   def __str__(self):
        return self.name
