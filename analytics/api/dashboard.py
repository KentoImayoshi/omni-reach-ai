from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response

from metrics.models import MetricSnapshot
from analytics.models import Insight


class DashboardView(APIView):
    """
    Aggregated dashboard endpoint used by the frontend
    to display summary metrics, trends and latest insights.
    """

    def get(self, request):

        cache_key = "dashboard_data"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        # Summary metrics
        summary = MetricSnapshot.objects.aggregate(
            impressions=Sum("impressions"),
            clicks=Sum("clicks"),
            spend=Sum("spend")
        )

        # Monthly trend
        trend = (
            MetricSnapshot.objects
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(clicks=Sum("clicks"))
            .order_by("month")
        )

        # Top integrations by clicks
        top_integrations = (
            MetricSnapshot.objects
            .values("integration__platform")
            .annotate(clicks=Sum("clicks"))
            .order_by("-clicks")[:5]
        )

        # Latest insights
        insights = (
            Insight.objects
            .select_related("integration")
            .order_by("-created_at")[:5]
            .values("type", "severity", "message")
        )

        data = {
            "summary": summary,
            "trend": list(trend),
            "top_integrations": list(top_integrations),
            "insights": list(insights),
        }

        cache.set(cache_key, data, 60 * 5)

        return Response(data)