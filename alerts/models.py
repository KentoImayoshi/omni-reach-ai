from django.db import models
import uuid


class Insight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    metric_snapshot = models.ForeignKey(
        "metrics.MetricSnapshot",
        on_delete=models.CASCADE,
        related_name="insights"
    )

    summary = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight for {self.metric_snapshot.id}"