from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache

from .serializers import InsightSerializer
from .pagination import InsightPagination
from .models import Insight

# Import selectors
from .selectors import get_metrics_summary


class MetricsSummaryView(APIView):
    """
    Returns aggregated metrics used in the dashboard summary.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request.user, "company", None)

        if company is None:
            return Response(
                {"detail": "User has no company assigned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = get_metrics_summary(company=company)

        return Response(data, status=status.HTTP_200_OK)


class InsightsListView(generics.ListAPIView):
    """
    Returns paginated insights with optional filters.
    """

    serializer_class = InsightSerializer
    pagination_class = InsightPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = getattr(self.request.user, "company", None)

        if company is None:
            return Insight.objects.none()

        qs = Insight.objects.select_related("integration").filter(
            integration__company=company
        )

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

    def list(self, request, *args, **kwargs):
        company = getattr(request.user, "company", None)

        if company is None:
            return Response(
                {"detail": "User has no company assigned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        severity = request.query_params.get("severity", "")
        insight_type = request.query_params.get("type", "")
        integration_id = request.query_params.get("integration_id", "")
        page = request.query_params.get("page", "1")
        page_size = request.query_params.get("page_size", "")

        cache_key = (
            f"insights_list:{company.id}:{severity}:{insight_type}:"
            f"{integration_id}:{page}:{page_size}"
        )

        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)

        cache.set(cache_key, response.data, 60)

        return response


class LatestInsightView(APIView):
    """
    Returns the most recently generated insight.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request.user, "company", None)

        if company is None:
            return Response(
                {"detail": "User has no company assigned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = f"insights_latest:{company.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        insight = (
            Insight.objects
            .select_related("integration")
            .filter(integration__company=company)
            .order_by("-created_at")
            .first()
        )

        if not insight:
            return Response(
                {"detail": "No insights found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = InsightSerializer(insight)

        cache.set(cache_key, serializer.data, 60)

        return Response(serializer.data, status=status.HTTP_200_OK)
