from django.db import models

from django.contrib.auth.models import AbstractUser
from rest_framework import serializers

class SluglineUser(AbstractUser):

    """Articles written by this user will use this name by default."""
    writer_name = models.CharField(max_length=255)

class UserSerializer(serializers.ModelSerializer):

    class Meta: 
        model = SluglineUser
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'writer_name'
        )
    
