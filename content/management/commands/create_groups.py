from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


BASE_PERMS = [
    "Can add article",
    "Can change article",
    "Can delete article",
    "Can view article",
    "Can view issue",
]

COPYEDITOR_PERMS = []

EDITOR_PERMS = [
    "Can add user",
    "Can change user",
    "Can delete user",
    "Can view user",
    "Can add issue",
    "Can change issue",
    "Can delete issue",
]


class Command(BaseCommand):
    help = "Creates basic groups for users"

    def handle(self, *args, **options):
        editor, _ = Group.objects.get_or_create(name="Editor")
        copyeditor, _ = Group.objects.get_or_create(name="Copyeditor")
        contrib, _ = Group.objects.get_or_create(name="Contributor")

        contrib.permissions.clear()
        copyeditor.permissions.clear()
        editor.permissions.clear()

        for perm in BASE_PERMS:
            contrib.permissions.add(Permission.objects.get(name=perm))

        for perm in COPYEDITOR_PERMS:
            copyeditor.permissions.add(Permission.objects.get(name=perm))

        for perm in EDITOR_PERMS:
            editor.permissions.add(Permission.objects.get(name=perm))
