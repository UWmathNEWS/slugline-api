from django.db import models

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


FORBIDDEN_USERNAMES = {"admin", "administrator", "root", "toor", "sudo", "sudoers"}


class SluglineUser(AbstractUser):
    email = models.EmailField(blank=False)
    """Articles written by this user will use this name by default."""
    writer_name = models.CharField(max_length=255)

    @property
    def is_editor(self):
        """Is this user an editor?"""
        return self.groups.filter(name="Editor").exists()

    # We write a setter as we construct temporary users when doing password validation, and sometimes editor information
    # is part of the data.
    @is_editor.setter
    def is_editor(self, value):
        pass

    class Meta:
        ordering = ["date_joined"]


class UserSerializer(serializers.ModelSerializer):
    is_editor = serializers.BooleanField(default=False)

    def create(self, validated_data):
        if (
            SluglineUser.objects.filter(
                username=validated_data.get("username", None)
            ).exists()
            or validated_data.get("username", "").lower() in FORBIDDEN_USERNAMES
        ):
            raise serializers.ValidationError(
                {"username": ["USER.USERNAME.ALREADY_EXISTS"]}
            )
        user = SluglineUser.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.groups.add(Group.objects.get(name="Contributor"))

        if validated_data["is_editor"]:
            user.groups.add(Group.objects.get(name="Editor"))

        return user

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data["password"])

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.writer_name = validated_data.get("writer_name", instance.writer_name)

        instance.save()

        if validated_data.get("is_editor", False):
            instance.groups.add(Group.objects.get(name="Editor"))
        elif not validated_data.get("is_editor", True):
            instance.groups.remove(Group.objects.get(name="Editor"))

        return instance

    def validate(self, data):
        # Quickly validate username and email
        errors_list = {}
        if "email" in data:
            try:
                validate_email(data["email"])
            except ValidationError:
                errors_list["email"] = ["USER.EMAIL.INVALID"]

        if "password" in data:
            try:
                current_attrs = UserSerializer(self.instance).data
                current_attrs.update(data)
                validate_password(data["password"], user=SluglineUser(**current_attrs))
            except ValidationError as err:
                errors_list["password"] = list(
                    map(
                        lambda e: "USER."
                        + e.code.replace("_", ".", 1).upper()
                        + (
                            "."
                            + ",".join(map(str, e.params.values())).replace(" ", "_")
                            if e.params is not None
                            else ""
                        ),
                        err.error_list,
                    )
                )

        if len(errors_list):
            raise serializers.ValidationError(errors_list)

        return data

    class Meta:
        model = SluglineUser
        fields = (
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_editor",
            "writer_name",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True}}
