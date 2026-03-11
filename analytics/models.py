from django.db import models


class Insight(models.Model):
    """
    AI generated insight about campaign performance.
    """

    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    integration = models.ForeignKey(
        "integrations.IntegrationAccount",
        on_delete=models.CASCADE,
        related_name="analytics_insights"
    )

    metric_snapshot = models.ForeignKey(
        "metrics.MetricSnapshot",
        on_delete=models.CASCADE,
        related_name="analytics_insights",
        null=True,
        blank=True,
    )

    type = models.CharField(max_length=100)

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )

    confidence_score = models.FloatField(
        null=True,
        blank=True,
    )

    message = models.TextField()

    recommendation = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["integration", "created_at"]),
            models.Index(fields=["severity", "type"]),
        ]

