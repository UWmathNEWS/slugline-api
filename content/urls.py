from rest_framework.routers import SimpleRouter

from content.views import ArticleViewSet, UserArticleViewSet, IssueViewSet

router = SimpleRouter()

router.register("issues", IssueViewSet)
router.register("articles", ArticleViewSet)
router.register("user_articles", UserArticleViewSet, basename="user-article")

urlpatterns = router.urls
