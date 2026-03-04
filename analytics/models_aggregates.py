from django.db import models


class MetricsAggregate(models.Model):
    """
    Precomputed daily metrics for faster analytics queries.
    """

    integration = models.ForeignKey(
        "integrations.IntegrationAccount",
        on_delete=models.CASCADE
    )

    date = models.DateField()

    total_spend = models.FloatField(default=0)
    total_clicks = models.IntegerField(default=0)
    total_impressions = models.IntegerField(default=0)

    avg_ctr = models.FloatField(default=0)
    avg_cpc = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["integration", "date"])
        ]