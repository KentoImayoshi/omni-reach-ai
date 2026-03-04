from django.urls import path
from .views import InsightsListView


urlpatterns = [
    path(
        "insights/",
        InsightsListView.as_view(),
        name="insights-list"
    ),
]