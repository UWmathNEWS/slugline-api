from content.tests import ContentTestCase


class ArticleTestCase(ContentTestCase):
    def test_editors_can_read_articles(self):
        self.c.force_authenticate(self.editor)
        response = self.c.get(f"/api/articles/{self.unpublished_article.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.unpublished_article.title)

    def test_editors_can_edit_articles(self):
        self.c.force_authenticate(self.editor)
        response = self.c.patch(
            f"/api/articles/{self.unpublished_article.id}/", {"title": "New Title"}
        )

        self.unpublished_article.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.unpublished_article.title, "New Title")

    def test_copyeditors_can_read_articles(self):
        self.c.force_authenticate(self.copyeditor)
        response = self.c.get(f"/api/articles/{self.unpublished_article.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.unpublished_article.title)

    def test_copyeditors_can_edit_articles(self):
        self.c.force_authenticate(self.copyeditor)
        response = self.c.patch(
            f"/api/articles/{self.unpublished_article.id}/", {"title": "New Title"}
        )

        self.unpublished_article.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.unpublished_article.title, "New Title")

    def test_contrib_can_read_articles(self):
        self.c.force_authenticate(self.contrib)
        response = self.c.get(f"/api/articles/{self.unpublished_article.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.unpublished_article.title)

    def test_contrib_cannot_edit_articles(self):
        self.c.force_authenticate(self.contrib)
        response = self.c.patch(
            f"/api/articles/{self.unpublished_article.id}/", {"title": "New Title"}
        )

        self.assertEqual(response.status_code, 403)

    def test_contrib_can_edit_own_articles(self):
        self.c.force_authenticate(self.contrib)
        self.unpublished_article.user = self.contrib
        self.unpublished_article.save()

        response = self.c.patch(
            f"/api/articles/{self.unpublished_article.id}/", {"title": "New Title"}
        )

        self.unpublished_article.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.unpublished_article.title, "New Title")

    def test_unauthed_cannot_read_unpublished_articles(self):
        self.c.force_authenticate(None)
        response = self.c.get(f"/api/articles/{self.unpublished_article.id}/")

        self.assertEqual(response.status_code, 403)

    def test_unauthed_can_read_published_articles(self):
        self.c.force_authenticate(None)
        response = self.c.get(f"/api/articles/{self.published_article.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.published_article.title)
