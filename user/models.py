from django.db import models

from django.contrib.auth.models import AbstractUser

class SluglineUser(AbstractUser):

    """Articles written by this user will use this name by default."""
    writer_name = models.CharField(max_length=255)    
    
