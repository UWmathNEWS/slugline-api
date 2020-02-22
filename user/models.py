from django.db import models

from django.contrib.auth.models import AbstractUser
from rest_framework import serializers

class SluglineUser(AbstractUser):

    """Articles written by this user will use this name by default."""
    writer_name = models.CharField(max_length=255)

    @property
    def is_editor(self):
        """Is this user an editor?"""
        return self.groups.filter(name='Editor').exists()

class UserSerializer(serializers.ModelSerializer):

    class Meta: 
        model = SluglineUser
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_editor',
            'writer_name'
        )
