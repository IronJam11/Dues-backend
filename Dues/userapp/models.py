from typing import Any
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import UserManager,AbstractBaseUser,PermissionsMixin
from passlib.hash import pbkdf2_sha256
from tagsapp.models import Tag
# Create your models here.
class CustomUserManager(UserManager):
    def _create_user(self,email,password,enrollmentNo,**extra_fields):
        if not email:
            return ValueError("If have not provided a valid email ID!")
        email = self.normalize_email(email)
        user = self.model(email=email,enrollmentNo= enrollmentNo,**extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    def create_user(self,email=None,password=None,enrollmentNo = None,**extra_fields):
        extra_fields.setdefault('is_reviewee',True)
        extra_fields.setdefault('is_admin',False)
        extra_fields.setdefault('is_reviewer',False)
        return self._create_user(email=email,password=password,enrollmentNo = enrollmentNo,**extra_fields)
    
    def create_superuser(self,email=None,password=None,enrollmentNo=None,**extra_fields):
        extra_fields.setdefault('is_reviewee',True)
        extra_fields.setdefault('is_admin',True)
        extra_fields.setdefault('is_reviewer',True)
        return self._create_user(email=email,password=password,enrollmentNo = enrollmentNo,**extra_fields)
    

class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique = True,default='')
    enrollmentNo = models.BigIntegerField(unique=True)
    is_reviewee = models.BooleanField(default=True)
    is_reviewer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['enrollmentNo']
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def get_full_name(self):
        return self.name


class UserDetails(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    year = models.IntegerField()
    isDeveloper = models.BooleanField(default=False)
    level = models.CharField(default="Newbie")
    points = models.IntegerField(default=0)
    profilePicture = models.ImageField(upload_to='userProfile/',default="")
    google_email = models.EmailField(null=True,blank=True)
    password = models.CharField(max_length=255) # Store hashed passwords here
    tags = models.ManyToManyField(Tag,blank=True)
    streak = models.IntegerField(default=1)
    longest_streak = models.IntegerField(default=1)

    def set_password(self, raw_password):
        # Hash the password using PBKDF2 or other methods
        self.password = pbkdf2_sha256.hash(raw_password)

    def check_password(self, raw_password):
        # Check if the given password matches the stored hash
        return pbkdf2_sha256.verify(raw_password, self.password)




from django.db import models
from django.utils import timezone
from datetime import datetime, time

class DayActivity(models.Model):
    date = models.DateField()  
    user_activity = models.ForeignKey('UserActivity', related_name='day_activities', on_delete=models.CASCADE)
    login_times = models.JSONField(default=list) 
    logout_times = models.JSONField(default=list)
    points = models.IntegerField(default=0)

    def add_login(self, login_time):
        # Convert datetime to string (ISO format)
        self.login_times.append(login_time.isoformat())
        self.save()

    def add_logout(self, logout_time):
        # Convert datetime to string (ISO format)
        self.logout_times.append(logout_time.isoformat())
        self.save()

    def __str__(self):
        return f"{self.date}: Logins - {len(self.login_times)}, Logouts - {len(self.logout_times)}"


from django.utils import timezone

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Activity of {self.user.email}"

    def record_login(self, login_time):
        user_details = UserDetails.objects.filter(user=self.user).first()
        
        # Ensure login_time is naive (without timezone)
        if timezone.is_aware(login_time):
            login_time = timezone.make_naive(login_time)
        
        # Get the current date at 12:00 AM for streak calculation
        midnight_today = datetime.combine(login_time.date(), time(0, 0))
        
        # Check if there's already a DayActivity for today
        current_day_activity, created = DayActivity.objects.get_or_create(
            user_activity=self,
            date=midnight_today.date()
        )

        # Only adjust the streak if we're creating a new DayActivity
        if created:
            # Check for the last day's activity before today
            previous_day_activity = DayActivity.objects.filter(
                user_activity=self,
                date__lt=midnight_today.date()
            ).order_by('-date').first()

            # If no activity before today, reset streak to 1
            if previous_day_activity is None:
                user_details.streak = 1
            else:
                # Increment the streak if there's activity before today
                user_details.streak += 1

            # Save updated user details
            user_details.save()

        # Record login for the current day
        current_day_activity.add_login(login_time)

    def record_logout(self, logout_time):
        """Records the logout time for the current day."""
        # Ensure logout_time is naive (without timezone)
        if timezone.is_aware(logout_time):
            logout_time = timezone.make_naive(logout_time)

        current_day_activity, created = DayActivity.objects.get_or_create(
            user_activity=self, date=logout_time.date()
        )
        current_day_activity.add_logout(logout_time)
