from django.db.models import Sum
from ..models_aggregates import MetricsAggregate


def get_metrics_summary(*, company):
    """
    Returns aggregated metrics for the dashboard.
    """

    metrics = MetricsAggregate.objects.filter(
        integration__company=company
    ).aggregate(
        total_impressions=Sum("total_impressions"),
        total_clicks=Sum("total_clicks"),
        total_spend=Sum("total_spend"),
    )

    return {
        "impressions": metrics["total_impressions"] or 0,
        "clicks": metrics["total_clicks"] or 0,
        "spend": metrics["total_spend"] or 0,
    }
