from django.urls import path
from .views import InsightsListView, LatestInsightView


urlpatterns = [
    path(
        "insights/",
        InsightsListView.as_view(),
        name="insights-list"
    ),

    path(
        "insights/latest/",
        LatestInsightView.as_view(),
        name="insights-latest"
    ),
]