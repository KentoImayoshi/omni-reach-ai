from django.db import models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from .services import invalidate_metrics_cache


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
    
@receiver(post_save, sender=MetricSnapshot)
def clear_metrics_cache(sender, instance, created, **kwargs):
    """
    When a new metric snapshot is saved,
    invalidate cached dashboard data.
    """

    if not created:
        return

    company_id = instance.integration.company_id

    invalidate_metrics_cache(company_id)