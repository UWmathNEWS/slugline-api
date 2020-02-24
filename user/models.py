from django.db import models

from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


class SluglineUser(AbstractUser):
    """Articles written by this user will use this name by default."""
    writer_name = models.CharField(max_length=255)

    @property
    def is_editor(self):
        """Is this user an editor?"""
        return self.groups.filter(name='Editor').exists()


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = SluglineUser.objects.create(**validated_data)
        user.groups.add(Group.objects.get(name='Contributor'))
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.writer_name = validated_data.get('writer_name', instance.writer_name)
        instance.save()
        return instance

    def validate(self, data):
        # Quickly validate that the username field is unique
        errors_list = {}
        if SluglineUser.objects.filter(username=data['username']):
            errors_list['username'] = 'Username already exists.'
        if len(errors_list):
            raise serializers.ValidationError(errors_list)

        if 'password' in data:
            try:
                validate_password(data['password'], user=SluglineUser.objects.get(username=data['username']))
            except SluglineUser.DoesNotExist:
                validate_password(data['password'], user=SluglineUser(**data))
            except ValidationError as err:
                raise serializers.ValidationError({'password': map(lambda e: e.message, err.error_list)})
        return data

    class Meta: 
        model = SluglineUser
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_editor',
            'writer_name'
        )
        read_only_fields = ('is_staff',)
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
