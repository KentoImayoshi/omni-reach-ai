from django.db import models
import uuid


class MetricSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    integration = models.ForeignKey(
        "integrations.IntegrationAccount",
        on_delete=models.CASCADE,
        related_name="metrics"
    )

    impressions = models.IntegerField()
    clicks = models.IntegerField()
    spend = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["integration", "created_at"]),
        ]

    def __str__(self):
        return f"{self.integration.platform} - {self.created_at}"