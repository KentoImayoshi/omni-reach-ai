from django.db.models import Sum
from ..models_aggregates import MetricsAggregate


def get_metrics_summary():
    """
    Returns aggregated metrics for the dashboard.
    """

    metrics = MetricsAggregate.objects.aggregate(
        total_impressions=Sum("impressions"),
        total_clicks=Sum("clicks"),
        total_spend=Sum("spend"),
    )

    return {
        "impressions": metrics["total_impressions"] or 0,
        "clicks": metrics["total_clicks"] or 0,
        "spend": metrics["total_spend"] or 0,
    }