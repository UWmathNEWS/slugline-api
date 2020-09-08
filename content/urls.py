from rest_framework.routers import SimpleRouter

from content.views import (
    ArticleViewSet,
    UserArticleViewSet,
    IssueViewSet,
    PublishedIssueViewSet,
    ArticleContentViewSet,
    ArticleHTMLViewSet,
)

router = SimpleRouter()

router.register("issues", IssueViewSet)
router.register("published_issues", PublishedIssueViewSet)
router.register("articles", ArticleViewSet)
router.register("user_articles", UserArticleViewSet, basename="user-articles")
router.register("article_content", ArticleContentViewSet)
router.register("article_html", ArticleHTMLViewSet)

urlpatterns = router.urls
