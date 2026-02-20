import hmac
import hashlib

from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from integrations.models import IntegrationAccount
from metrics.models import MetricSnapshot


@api_view(["POST"])
@permission_classes([AllowAny])
def meta_webhook(request):
    """
    Simulated Meta webhook endpoint with HMAC SHA256 validation.
    """

    signature = request.headers.get("X-Hub-Signature-256")

    if not signature:
        return Response(
            {"error": "Missing X-Hub-Signature-256 header"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Generate expected signature
    expected_signature = "sha256=" + hmac.new(
        key=settings.META_WEBHOOK_SECRET.encode(),
        msg=request.body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Secure comparison
    if not hmac.compare_digest(expected_signature, signature):
        return Response(
            {"error": "Invalid signature"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Parse payload
    integration_id = request.data.get("integration_id")
    impressions = request.data.get("impressions", 0)
    clicks = request.data.get("clicks", 0)
    spend = request.data.get("spend", 0)

    if not integration_id:
        return Response(
            {"error": "integration_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        integration = IntegrationAccount.objects.get(id=integration_id)
    except IntegrationAccount.DoesNotExist:
        return Response(
            {"error": "Integration not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Create metric snapshot
    MetricSnapshot.objects.create(
        integration=integration,
        impressions=impressions,
        clicks=clicks,
        spend=spend,
    )

    return Response(
        {"status": "Metric received successfully"},
        status=status.HTTP_201_CREATED,
    )