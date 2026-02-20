from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from companies.views import CompanyViewSet
from integrations.views import IntegrationAccountViewSet
from metrics.views import MetricSnapshotViewSet
from integrations.webhooks import meta_webhook


router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="companies")
router.register(r"integrations", IntegrationAccountViewSet, basename="integrations")
router.register(r"metrics", MetricSnapshotViewSet, basename="metrics")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/webhooks/meta/", meta_webhook),  # 👈 ESSA LINHA É ESSENCIAL
]