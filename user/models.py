from django.db import models

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from user.groups import (
    GROUPS,
    EDITOR_GROUP,
    COPYEDITOR_GROUP,
    CONTRIBUTOR_GROUP,
    role_at_least,
)

FORBIDDEN_USERNAMES = {"admin", "administrator", "root", "toor", "sudo", "sudoers"}


class SluglineUser(AbstractUser):
    email = models.EmailField(blank=False)
    """Articles written by this user will use this name by default."""
    writer_name = models.CharField(max_length=255)
    """Uniquely generated token to reset password"""
    password_reset_token = models.CharField(max_length=128, default="")

    @property
    def role(self):
        """Returns the highest role that a user has."""
        if self.groups.filter(name=EDITOR_GROUP).exists():
            return EDITOR_GROUP
        elif self.groups.filter(name=COPYEDITOR_GROUP).exists():
            return COPYEDITOR_GROUP
        else:
            return CONTRIBUTOR_GROUP

    # We write a setter as we construct temporary users when doing password validation, and sometimes role information
    # is part of the data.
    @role.setter
    def role(self, value):
        pass

    def at_least(self, minimum):
        """Returns if a user has at least a given role's privileges"""
        return self.is_staff or role_at_least(self.role, minimum)

    class Meta:
        ordering = ["date_joined"]


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default=CONTRIBUTOR_GROUP)

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
        user.save()

        user.groups.add(Group.objects.get(name=CONTRIBUTOR_GROUP))

        if validated_data["role"] in GROUPS:
            for base_role in GROUPS[validated_data["role"]]:
                user.groups.add(Group.objects.get(name=base_role))
            user.groups.add(Group.objects.get(name=validated_data["role"]))

        return user

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data["password"])

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.writer_name = validated_data.get("writer_name", instance.writer_name)

        instance.save()

        if validated_data.get("role") in GROUPS:
            new_roles = {validated_data["role"], *GROUPS[validated_data["role"]]}
            current_roles = set(instance.groups.values_list("name", flat=True))

            for obsolete_role in current_roles - new_roles:
                instance.groups.remove(Group.objects.get(name=obsolete_role))

            for new_role in new_roles - current_roles:
                instance.groups.add(Group.objects.get(name=new_role))

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
            "role",
            "writer_name",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True}}
