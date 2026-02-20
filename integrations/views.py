from rest_framework import viewsets
from .models import IntegrationAccount
from .serializers import IntegrationAccountSerializer
from .tasks import sync_integration_metrics


class IntegrationAccountViewSet(viewsets.ModelViewSet):
    queryset = IntegrationAccount.objects.all()
    serializer_class = IntegrationAccountSerializer

    def perform_create(self, serializer):
        integration = serializer.save()
        sync_integration_metrics.delay(str(integration.id))