from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from metrics.views import MetricsSummaryView, MetricSnapshotViewSet
from companies.views import CompanyViewSet
from integrations.views import IntegrationAccountViewSet
from integrations.webhooks import meta_webhook


router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="companies")
router.register(r"integrations", IntegrationAccountViewSet, basename="integrations")
router.register(r"metrics", MetricSnapshotViewSet, basename="metrics")

urlpatterns = [
    path("admin/", admin.site.urls),

    # JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Webhook
    path("api/webhooks/meta/", meta_webhook),

    path("api/metrics/summary/", MetricsSummaryView.as_view(), name="metrics-summary"),

    path("api/", include(router.urls)),
]