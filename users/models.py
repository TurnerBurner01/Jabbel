from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class User(AbstractUser):

    # Allows spaces and certain special characters in username
    username_validator = RegexValidator(
        regex=r'^[\w\s.\'-]+$',
    )

    # Apply the custom validator to the username field
    username = models.CharField(
        max_length=150,
        unique=False, 
        validators=[username_validator],
        help_text='Enter your full name or a display name.'
    )
    
    # Define email field as unique
    email = models.EmailField(unique=True)

    # Set email as the login identifier
    USERNAME_FIELD = "email"

    # This makes 'username' required when running 'createsuperuser'
    REQUIRED_FIELDS = ["username"]

    # Image field for profile picture
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # Clean method to normalize email and trim username
    def clean(self):
        super().clean()
        if self.username:
            self.username = " ".join(self.username.split())
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)

    # String representation of the user
    def __str__(self):
        return f"{self.username} ({self.email})"