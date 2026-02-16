from django.db import models
from Jabbel import settings

class Journal(models.Model):

    # Makes a relationship between Journal and User
    user = models.ForeignKey(       
        settings.AUTH_USER_MODEL,   # Uses the user model defined in settings
        on_delete=models.CASCADE,   # When user is deleted, delete their journals too
        related_name='journals'     # Allows accessing a user's journals via user.journals
    )

    # Title and content fields
    title = models.CharField(max_length=200)                # Title of the journal
    content = models.JSONField()                            # Content of the journal stored as JSON

    # Timestamps
    date_created = models.DateTimeField(auto_now_add=True)  # Timestamp when journal is created
    date_updated = models.DateTimeField(auto_now=True)      # Timestamp when journal is last updated

    def __str__(self):
        return self.title