from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Users(AbstractUser):
    
    # Define email field as unique
    email = models.EmailField(unique=True)

    # Set email as the login identifier
    USERNAME_FIELD = "email"

    # This makes 'username' required when running 'createsuperuser'
    REQUIRED_FIELDS = ["username"]

    # Image field for profile picture
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.email