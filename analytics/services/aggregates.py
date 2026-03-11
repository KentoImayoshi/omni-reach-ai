"""
Services for maintaining analytics aggregates.
"""

from django.db.models import Sum
from django.utils import timezone

from metrics.models import MetricSnapshot
from analytics.models_aggregates import MetricsAggregate


def update_daily_aggregate(snapshot):
    """
    Recompute the daily aggregate for the snapshot's integration and day.
    """

    integration = snapshot.integration
    day = timezone.localdate(snapshot.created_at)

    totals = MetricSnapshot.objects.filter(
        integration=integration,
        created_at__date=day,
    ).aggregate(
        total_impressions=Sum("impressions"),
        total_clicks=Sum("clicks"),
        total_spend=Sum("spend"),
    )

    total_impressions = totals["total_impressions"] or 0
    total_clicks = totals["total_clicks"] or 0
    total_spend = float(totals["total_spend"] or 0)

    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions else 0
    avg_cpc = (total_spend / total_clicks) if total_clicks else 0

    MetricsAggregate.objects.update_or_create(
        integration=integration,
        date=day,
        defaults={
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_spend": total_spend,
            "avg_ctr": avg_ctr,
            "avg_cpc": avg_cpc,
        },
    )
