from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from content.models import Article, Issue
from user.models import SluglineUser


class Command(BaseCommand):
    help = "Creates basic groups for users"

    def handle(self, *args, **options):
        editor, _ = Group.objects.get_or_create(name="Editor")
        contrib, _ = Group.objects.get_or_create(name="Contributor")

        editor.permissions.add(Permission.objects.get(name="Can add user"))
        editor.permissions.add(Permission.objects.get(name="Can change user"))
        editor.permissions.add(Permission.objects.get(name="Can delete user"))
        editor.permissions.add(Permission.objects.get(name="Can view user"))
        editor.permissions.add(Permission.objects.get(name="Can add article"))
        editor.permissions.add(Permission.objects.get(name="Can change article"))
        editor.permissions.add(Permission.objects.get(name="Can delete article"))
        editor.permissions.add(Permission.objects.get(name="Can view article"))
        editor.permissions.add(Permission.objects.get(name="Can add issue"))
        editor.permissions.add(Permission.objects.get(name="Can change issue"))
        editor.permissions.add(Permission.objects.get(name="Can delete issue"))
        editor.permissions.add(Permission.objects.get(name="Can view issue"))

        contrib.permissions.add(Permission.objects.get(name="Can add article"))
        contrib.permissions.add(Permission.objects.get(name="Can change article"))
        contrib.permissions.add(Permission.objects.get(name="Can delete article"))
        contrib.permissions.add(Permission.objects.get(name="Can view article"))
        contrib.permissions.add(Permission.objects.get(name="Can view issue"))
