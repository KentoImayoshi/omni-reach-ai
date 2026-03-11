from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from analytics.models import Insight
from analytics.models_aggregates import MetricsAggregate


class DashboardView(APIView):
    """
    Aggregated dashboard endpoint used by the frontend
    to display summary metrics, trends and latest insights.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request.user, "company", None)

        if company is None:
            return Response(
                {"detail": "User has no company assigned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = f"dashboard_data:{company.id}"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        agg_qs = MetricsAggregate.objects.filter(
            integration__company=company
        )

        # Summary metrics
        summary = agg_qs.aggregate(
            impressions=Sum("total_impressions"),
            clicks=Sum("total_clicks"),
            spend=Sum("total_spend")
        )

        # Monthly trend
        trend = (
            agg_qs
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(clicks=Sum("total_clicks"))
            .order_by("month")
        )

        # Top integrations by clicks
        top_integrations = (
            agg_qs
            .values("integration__platform")
            .annotate(clicks=Sum("total_clicks"))
            .order_by("-clicks")[:5]
        )

        # Latest insights
        insights = (
            Insight.objects
            .select_related("integration")
            .filter(integration__company=company)
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
