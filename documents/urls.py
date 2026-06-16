from rest_framework.routers import DefaultRouter

from documents.views import CategoryViewSet, DocumentViewSet

app_name = "documents"

router = DefaultRouter()
router.register("", DocumentViewSet, basename="document")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
