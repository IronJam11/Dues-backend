from django.db import models
from userapp.models import User
from assignmentsapp.models import Assignment
# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    group_image = models.ImageField(upload_to='groupImages/', default="")
    participants = models.ManyToManyField(User, related_name='group_participants', blank=False)
    time_assigned = models.DateTimeField(auto_now_add=True)  # Auto-add the current time when created
    deadline = models.DateTimeField(null=False, blank=False)
    roomname = models.TextField(unique=True)
    assignments = models.ManyToManyField(Assignment, related_name='group_assignments', blank=True)  # Assignments can be empty

    def save(self, *args, **kwargs):
        if not self.roomname:
            self.roomname = f"{self.name}_{self.time_assigned}_{self.deadline}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
