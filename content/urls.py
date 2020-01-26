from rest_framework.routers import SimpleRouter

from content.views import ArticleViewSet, IssueViewSet

router = SimpleRouter()

router.register('issues', IssueViewSet)
router.register('articles', ArticleViewSet)

urlpatterns = router.urls


