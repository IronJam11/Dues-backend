from typing import Any
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import UserManager,AbstractBaseUser,PermissionsMixin
from passlib.hash import pbkdf2_sha256
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

    def set_password(self, raw_password):
        # Hash the password using PBKDF2 or other methods
        self.password = pbkdf2_sha256.hash(raw_password)

    def check_password(self, raw_password):
        # Check if the given password matches the stored hash
        return pbkdf2_sha256.verify(raw_password, self.password)
    
class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(null=False,blank=False)
    logout_time = models.DateTimeField(null=False,blank=False)
    day_weight = models.IntegerField(default=0) # for calculating how much he did on that day 


    



