from datetime import date

from django.test import TestCase
from django.contrib.auth.models import Group

from rest_framework.test import APIClient

from content.models import Article, Issue
from user.groups import (
    COPYEDITOR_GROUP,
    create_default_groups,
    EDITOR_GROUP,
    CONTRIBUTOR_GROUP,
)
from user.models import SluglineUser


class ContentTestCase(TestCase):
    def setUp(self) -> None:
        create_default_groups()
        self.editor = SluglineUser.objects.create(username="editor")
        self.editor.groups.add(Group.objects.get(name=EDITOR_GROUP))
        self.editor.save()

        self.copyeditor = SluglineUser.objects.create(username="copyeditor")
        self.copyeditor.groups.add(Group.objects.get(name=COPYEDITOR_GROUP))
        self.copyeditor.save()

        self.contrib = SluglineUser.objects.create(username="contrib")
        self.contrib.groups.add(Group.objects.get(name=CONTRIBUTOR_GROUP))
        self.contrib.save()

        self.unpublished_issue = Issue.objects.create(volume_num=666, issue_code="1")

        self.published_issue = Issue.objects.create(
            volume_num=667, issue_code="1", publish_date=date.today()
        )

        self.unpublished_article = Article.objects.create(
            title="Unpublished Article", issue=self.unpublished_issue
        )

        self.published_article = Article.objects.create(
            title="Published Article", issue=self.published_issue
        )
        self.c = APIClient()
