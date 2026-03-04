from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MetricSnapshot
from .services import invalidate_metrics_cache


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