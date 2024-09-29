from django.db import models
from userapp.models import User

from django.db import models
from django.utils.text import slugify
from userapp.models import User
import uuid

class Room(models.Model):
    DM = 'dm'
    GROUPCHAT = 'groupchat'

    ROOM_TYPE_CHOICES = [
        (DM, 'Direct Message'),
        (GROUPCHAT, 'Group Chat'),
    ]

    room_name = models.TextField()
    participants = models.ManyToManyField(User, related_name='rooms')
    admins = models.ManyToManyField(User, related_name="room_admins")
    late_joiners = models.ManyToManyField(User, related_name="late_room_participants")
    time_created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    type = models.CharField(
        max_length=10,
        choices=ROOM_TYPE_CHOICES,
        default=DM,
    )

    def save(self, *args, **kwargs):
        # Generate unique slug before saving the room
        if not self.slug:
            participant_ids = sorted([str(user.id) for user in self.participants.all()])
            late_joiner_ids = sorted([str(user.id) for user in self.late_joiners.all()])
            unique_string = f"{self.room_name}-Participants-{','.join(participant_ids)}-LateJoiners-{','.join(late_joiner_ids)}-{self.time_created.strftime('%Y%m%d%H%M%S')}"
            self.slug = slugify(unique_string)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Room: {self.room_name} ({self.get_type_display()})"
