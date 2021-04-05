from datetime import date

from content.tests import ContentTestCase


class IssueTestCase(ContentTestCase):
    def test_editors_can_edit_issues(self):
        self.c.force_authenticate(user=self.editor)
        response = self.c.patch(
            f"/api/issues/{self.unpublished_issue.id}/",
            {"volume_num": 667, "issue_code": "2"},
        )
        self.unpublished_issue.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.unpublished_issue.volume_num, 667)
        self.assertEqual(self.unpublished_issue.issue_code, "2")

    def test_editors_can_read_issues(self):
        self.c.force_authenticate(user=self.editor)
        response = self.c.get(f"/api/issues/{self.unpublished_issue.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["volume_num"], self.unpublished_issue.volume_num)
        self.assertEqual(response.data["issue_code"], self.unpublished_issue.issue_code)

    def test_contributors_cannot_edit_issues(self):
        self.c.force_authenticate(user=self.contrib)
        response = self.c.patch(
            f"/api/issues/{self.unpublished_issue.id}/",
            {"volume_num": 667, "issue_code": "2"},
        )
        self.unpublished_issue.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.unpublished_issue.volume_num, 666)
        self.assertEqual(self.unpublished_issue.issue_code, "1")

    def test_contributors_can_read_issues(self):
        self.c.force_authenticate(user=self.contrib)
        response = self.c.get(f"/api/issues/{self.unpublished_issue.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["volume_num"], self.unpublished_issue.volume_num)
        self.assertEqual(response.data["issue_code"], self.unpublished_issue.issue_code)

    def test_unauth_cannot_edit_issues(self):
        self.c.force_authenticate(user=None)
        response = self.c.patch(
            f"/api/issues/{self.unpublished_issue.id}/",
            {"volume_num": 667, "issue_code": "2"},
        )

        self.unpublished_issue.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.unpublished_issue.volume_num, 666)
        self.assertEqual(self.unpublished_issue.issue_code, "1")

    def test_unauth_cannot_read_issue(self):
        self.c.force_authenticate(user=None)
        response = self.c.get(f"/api/issues/{self.unpublished_issue.id}/")

        self.assertEqual(response.status_code, 403)


class IssueArticlesTestCase(ContentTestCase):
    def test_editors_can_read_articles(self):
        self.c.force_authenticate(user=self.editor)
        response = self.c.get(f"/api/issues/{self.unpublished_issue.id}/articles/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["results"][0]["title"], self.unpublished_article.title
        )

    def test_contributors_can_read_articles(self):
        self.c.force_authenticate(user=self.contrib)
        response = self.c.get(f"/api/issues/{self.unpublished_issue.id}/articles/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["results"][0]["title"], self.unpublished_article.title
        )

    def test_unauthed_cannot_read_unpublished(self):
        self.c.force_authenticate(user=None)
        response = self.c.get(f"/api/issues/{self.unpublished_issue.id}/articles/")

        self.assertEqual(response.status_code, 403)

    def test_unauthed_can_read_published(self):
        self.c.force_authenticate(user=None)
        response = self.c.get(f"/api/issues/{self.published_issue.id}/articles/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["results"][0]["title"], self.published_article.title
        )
