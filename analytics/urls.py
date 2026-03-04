from django.urls import path
from .views import InsightsListView, LatestInsightView
from .api.dashboard import DashboardView

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

    path(
        "dashboard/",
        DashboardView.as_view(),
        name="analytics-dashboard"
    ),
]