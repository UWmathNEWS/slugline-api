from django.test import TestCase
from django.contrib.auth.models import Group

from rest_framework.test import APIClient

from content.models import Article, Issue
from user.groups import (
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
        self.editor.refresh_from_db()

        self.contrib = SluglineUser.objects.create(username="contrib")
        self.contrib.groups.add(Group.objects.get(name=CONTRIBUTOR_GROUP))
        self.contrib.save()

        self.issue = Issue.objects.create(volume_num=666, issue_code="1")
        self.issue.refresh_from_db()

        self.article = Article.objects.create(title="Article", issue=self.issue)
        self.article.refresh_from_db()
        self.c = APIClient()
