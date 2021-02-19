from django.core.management.base import BaseCommand

from user.groups import create_default_groups


class Command(BaseCommand):
    help = "Creates basic groups for users"

    def handle(self, *args, **options):
        create_default_groups()
