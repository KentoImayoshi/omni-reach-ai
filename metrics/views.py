from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import MetricSnapshot
from .serializers import (
    MetricSnapshotSerializer,
    MetricsSummaryFilterSerializer,
)
from .services import get_company_metrics_summary


# 🔹 /api/metrics/
class MetricSnapshotViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MetricSnapshotSerializer

    def get_queryset(self):
        return MetricSnapshot.objects.filter(
            integration__company=self.request.user.company
        ).order_by("-created_at")


# 🔹 /api/metrics/summary/
class MetricsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MetricsSummaryFilterSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        summary = get_company_metrics_summary(
            company=request.user.company,
            start_date=serializer.validated_data.get("start_date"),
            end_date=serializer.validated_data.get("end_date"),
        )

        return Response(summary)