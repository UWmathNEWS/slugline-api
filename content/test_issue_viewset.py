from datetime import date

from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from content.models import Issue

from user.groups import create_default_groups, EDITOR_GROUP, CONTRIBUTOR_GROUP
from user.models import SluglineUser


class IssueTestCase(TestCase):
    def setUp(self):
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
        self.c = APIClient()

    def test_editors_can_edit_issues(self):
        self.c.force_authenticate(user=self.editor)
        response = self.c.patch(
            f"/api/issues/{self.issue.id}/", {"volume_num": 667, "issue_code": "2"},
        )
        self.issue.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.issue.volume_num, 667)
        self.assertEqual(self.issue.issue_code, "2")

    def test_editors_can_read_issues(self):
        self.c.force_authenticate(user=self.editor)
        response = self.c.get(f"/api/issues/{self.issue.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["volume_num"], self.issue.volume_num)
        self.assertEqual(response.data["issue_code"], self.issue.issue_code)

    def test_contributors_cannot_edit_issues(self):
        self.c.force_authenticate(user=self.contrib)
        response = self.c.patch(
            f"/api/issues/{self.issue.id}/", {"volume_num": 667, "issue_code": "2"}
        )
        self.issue.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.issue.volume_num, 666)
        self.assertEqual(self.issue.issue_code, "1")

    def test_contributors_can_read_issues(self):
        self.c.force_authenticate(user=self.contrib)
        response = self.c.get(f"/api/issues/{self.issue.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["volume_num"], self.issue.volume_num)
        self.assertEqual(response.data["issue_code"], self.issue.issue_code)

    def test_unauth_cannot_edit_issues(self):
        self.c.force_authenticate(user=None)
        response = self.c.patch(
            f"/api/issues/{self.issue.id}/", {"volume_num": 667, "issue_code": "2"}
        )

        self.issue.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.issue.volume_num, 666)
        self.assertEqual(self.issue.issue_code, "1")

    def test_unauth_cannot_read_unpublished_issue(self):
        self.c.force_authenticate(user=None)
        response = self.c.get(f"/api/issues/{self.issue.id}/")

        self.assertEqual(response.status_code, 403)

    def test_unauth_can_read_published_issue(self):
        # TODO: Ask Terry, unauthed people can't read published issues?
        self.c.force_authenticate(user=None)
        self.issue.publish_date = date.today()
        self.issue.save()
        response = self.c.get(f"/api/issues/{self.issue.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["volume_num"], self.issue.volume_num)
        self.assertEqual(response.data["issue_code"], self.issue.issue_code)
