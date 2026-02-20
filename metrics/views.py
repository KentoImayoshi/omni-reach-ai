from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import MetricSnapshot
from .serializers import MetricSnapshotSerializer


class MetricSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MetricSnapshotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MetricSnapshot.objects.filter(
            integration__company=self.request.user.company
        ).select_related("integration")