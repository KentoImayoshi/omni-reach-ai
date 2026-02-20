from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from companies.views import CompanyViewSet
from integrations.views import IntegrationAccountViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="companies")
router.register(r"integrations", IntegrationAccountViewSet, basename="integrations")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]