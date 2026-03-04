from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Insight
from .serializers import InsightSerializer
from .pagination import InsightPagination


class InsightsListView(ListAPIView):
    """
    Return paginated insights with optional filters.
    """

    serializer_class = InsightSerializer
    pagination_class = InsightPagination

    def get_queryset(self):
        """
        Build queryset with optional filters and optimized queries.
        """

        queryset = (
            Insight.objects
            .select_related("integration")  # optimize FK query
            .order_by("-created_at")
        )

        # Query parameters
        severity = self.request.query_params.get("severity")
        insight_type = self.request.query_params.get("type")
        integration_id = self.request.query_params.get("integration_id")

        # Apply filters if provided
        if severity:
            queryset = queryset.filter(severity=severity)

        if insight_type:
            queryset = queryset.filter(type=insight_type)

        if integration_id:
            queryset = queryset.filter(integration_id=integration_id)

        return queryset


class LatestInsightView(APIView):
    """
    Return the most recent insight.
    """

    def get(self, request):

        latest_insight = (
            Insight.objects
            .select_related("integration")  # optimize FK query
            .order_by("-created_at")
            .first()
        )

        if not latest_insight:
            return Response({"latest": None})

        serializer = InsightSerializer(latest_insight)

        return Response({
            "latest": serializer.data
        })