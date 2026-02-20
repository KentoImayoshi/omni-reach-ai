from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import IntegrationAccount
from .serializers import IntegrationAccountSerializer
from .tasks import sync_integration_metrics


class IntegrationAccountViewSet(viewsets.ModelViewSet):
    serializer_class = IntegrationAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return IntegrationAccount.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):
        integration = serializer.save(
            company=self.request.user.company
        )
        sync_integration_metrics.delay(str(integration.id))