from content.tests import ContentTestCase


class PublishedIssueTestCase(ContentTestCase):
    def test_does_not_show_unpublished_issues(self):
        self.c.force_authenticate(user=None)
        response = self.c.get("/api/published_issues/")

        article_ids = map(lambda a: a["id"], response.data["results"])
        self.assertTrue(self.published_article.id in article_ids)
        self.assertFalse(self.unpublished_article.id in article_ids)

    def test_editors_can_read(self):
        self.c.force_authenticate(user=self.editor)
        response = self.c.get(f"/api/published_issues/{self.published_issue.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.published_issue.id)

    def test_contributors_can_read(self):
        self.c.force_authenticate(user=self.contrib)
        response = self.c.get(f"/api/published_issues/{self.published_issue.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.published_issue.id)

    def test_unauthed_can_read(self):
        self.c.force_authenticate(user=None)
        response = self.c.get(f"/api/published_issues/{self.published_issue.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.published_issue.id)

    def test_editors_cannot_edit(self):
        self.c.force_authenticate(user=self.editor)
        response = self.c.patch(
            f"/api/published_issues/{self.published_issue.id}/",
            {"volume_num": 667, "issue_code": "1"},
        )

        self.assertEqual(response.status_code, 405)

    def test_contributors_cannot_edit(self):
        self.c.force_authenticate(user=self.contrib)
        response = self.c.patch(
            f"/api/published_issues/{self.published_issue.id}/",
            {"volume_num": 667, "issue_code": "1"},
        )

        self.assertEqual(response.status_code, 405)

    def test_unauth_cannot_edit(self):
        self.c.force_authenticate(user=None)
        response = self.c.patch(
            f"/api/published_issues/{self.published_issue.id}/",
            {"volume_num": 667, "issue_code": "1"},
        )

        self.assertEqual(response.status_code, 405)
