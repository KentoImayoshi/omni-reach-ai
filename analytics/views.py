"""
Analytics views.

Provides endpoints for metrics summary and insights retrieval
used by the OmniReach dashboard.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status

from .serializers import InsightSerializer
from .pagination import InsightPagination
from .models import Insight

# Import selectors
from .selectors import get_metrics_summary


class MetricsSummaryView(APIView):
    """
    Returns aggregated metrics used in the dashboard summary.
    """

    def get(self, request):
        data = get_metrics_summary()

        return Response(data, status=status.HTTP_200_OK)


class InsightsListView(generics.ListAPIView):
    """
    Returns paginated insights with optional filters.
    """

    serializer_class = InsightSerializer
    pagination_class = InsightPagination

    def get_queryset(self):
        qs = Insight.objects.select_related("integration").all()

        severity = self.request.query_params.get("severity")
        insight_type = self.request.query_params.get("type")
        integration_id = self.request.query_params.get("integration_id")

        if severity:
            qs = qs.filter(severity=severity)

        if insight_type:
            qs = qs.filter(type=insight_type)

        if integration_id:
            qs = qs.filter(integration_id=integration_id)

        return qs


class LatestInsightView(APIView):
    """
    Returns the most recently generated insight.
    """

    def get(self, request):
        insight = (
            Insight.objects
            .select_related("integration")
            .order_by("-created_at")
            .first()
        )

        if not insight:
            return Response(
                {"detail": "No insights found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = InsightSerializer(insight)

        return Response(serializer.data, status=status.HTTP_200_OK)