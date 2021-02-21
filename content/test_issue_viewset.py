from datetime import date

from content.tests import ContentTestCase


class IssueTestCase(ContentTestCase):
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

    def test_unauth_cannot_read_issue(self):
        self.c.force_authenticate(user=None)
        response = self.c.get(f"/api/issues/{self.issue.id}/")

        self.assertEqual(response.status_code, 403)


class IssueArticlesTestCase(ContentTestCase):
    def test_editors_can_read_articles(self):
        self.c.force_authenticate(user=self.editor)
        response = self.c.get(f"/api/issues/{self.issue.id}/articles/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Article")

    def test_contributors_can_read_articles(self):
        self.c.force_authenticate(user=self.contrib)
        response = self.c.get(f"/api/issues/{self.issue.id}/articles/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Article")

    def test_unauthed_cannot_read_unpublished(self):
        self.c.force_authenticate(user=None)
        response = self.c.get(f"/api/issues/{self.issue.id}/articles/")

        self.assertEqual(response.status_code, 403)

    def test_unauthed_can_read_published(self):
        self.c.force_authenticate(user=None)
        self.issue.publish_date = date.today()
        self.issue.save()
        response = self.c.get(f"/api/issues/{self.issue.id}/articles/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Article")
