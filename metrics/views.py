from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from .models import MetricSnapshot
from .pagination import MetricSnapshotPagination
from .serializers import (
    MetricSnapshotSerializer,
    MetricsSummaryFilterSerializer,
)
from .services import (
    get_company_metrics_summary,
    get_company_daily_breakdown,
    get_company_monthly_breakdown
)

from .utils.cache import get_or_set_cache


class MetricSnapshotViewSet(ModelViewSet):
    """
    Provides CRUD access to raw metric snapshots.
    Multi-tenant safe by filtering through integration__company.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MetricSnapshotSerializer
    pagination_class = MetricSnapshotPagination

    def get_queryset(self):

        company = getattr(self.request.user, "company", None)

        if company is None:
            return MetricSnapshot.objects.none()

        return MetricSnapshot.objects.filter(
            integration__company=company
        ).order_by("-created_at")


class MetricsSummaryView(APIView):
    """
    Returns aggregated totals for the current company.
    Supports optional date range filtering.
    Cached to improve dashboard performance.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = MetricsSummaryFilterSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        company = getattr(request.user, "company", None)

        if company is None:
            return Response(
                {"detail": "User has no company assigned"},
                status=400
            )

        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")

        cache_key = f"metrics_summary:{company.id}:{start_date}:{end_date}"

        def fetch_data():
            """
            Fetch data from service layer if cache miss occurs.
            """
            return get_company_metrics_summary(
                company=company,
                start_date=start_date,
                end_date=end_date,
            )

        summary = get_or_set_cache(cache_key, fetch_data)

        return Response(summary)


class MetricsDailyBreakdownView(APIView):
    """
    Returns grouped metrics per day for dashboard visualization.
    Cached to avoid heavy aggregation queries.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = MetricsSummaryFilterSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        company = getattr(request.user, "company", None)

        if company is None:
            return Response(
                {"detail": "User has no company assigned"},
                status=400
            )

        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")

        cache_key = f"metrics_daily:{company.id}:{start_date}:{end_date}"

        def fetch_data():
            """
            Fetch daily breakdown from service layer if cache miss.
            """
            return get_company_daily_breakdown(
                company=company,
                start_date=start_date,
                end_date=end_date,
            )

        breakdown = get_or_set_cache(cache_key, fetch_data)

        return Response(breakdown)


class MetricsMonthlyBreakdownView(APIView):
    """
    Returns grouped metrics per month.
    Useful for dashboard charts.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = MetricsSummaryFilterSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        company = getattr(request.user, "company", None)

        if company is None:
            return Response(
                {"detail": "User has no company assigned"},
                status=400
            )

        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")

        cache_key = f"metrics_monthly:{company.id}:{start_date}:{end_date}"

        def fetch_data():

            return get_company_monthly_breakdown(
                company=company,
                start_date=start_date,
                end_date=end_date,
            )

        data = get_or_set_cache(cache_key, fetch_data)

        return Response(data)
