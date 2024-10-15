from django.db import models

class Tag(models.Model):
   name = models.CharField(max_length=255,unique=True)
   description = models.CharField(max_length=255)
   condition = models.CharField()
   color = models.CharField(max_length=7,default='#FFFFFF')
   time_added = models.DateTimeField()
   def __str__(self):
        return self.name

