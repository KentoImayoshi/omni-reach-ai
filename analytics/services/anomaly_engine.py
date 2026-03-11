"""
Anomaly detection for marketing metrics.

Uses simple statistical baselines (z-score) on recent daily aggregates.
"""

from datetime import timedelta
from statistics import mean, stdev, StatisticsError

from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from metrics.models import MetricSnapshot
from analytics.models import Insight


MIN_BASELINE_DAYS = 5
Z_WARNING = 2.0
Z_CRITICAL = 3.0


def _safe_zscore(series, value):
    """
    Return z-score or None if not enough variance or samples.
    """

    if len(series) < MIN_BASELINE_DAYS:
        return None

    try:
        sigma = stdev(series)
    except StatisticsError:
        return None

    if sigma == 0:
        return None

    return (value - mean(series)) / sigma


def _daily_aggregates(integration, *, start_date):
    """
    Aggregate snapshots per day for an integration from start_date onward.
    """

    return list(
        MetricSnapshot.objects
        .filter(integration=integration, created_at__date__gte=start_date)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            impressions=Sum("impressions"),
            clicks=Sum("clicks"),
            spend=Sum("spend"),
        )
        .order_by("day")
    )


def generate_and_store_anomalies(snapshot, *, window_days=14):
    """
    Detect anomalies for the snapshot day using recent daily aggregates.
    Stores results as analytics.Insight.
    """

    integration = snapshot.integration
    target_day = timezone.localdate(snapshot.created_at)
    start_date = target_day - timedelta(days=window_days)

    daily = _daily_aggregates(integration, start_date=start_date)

    # Split baseline vs target day
    baseline = [d for d in daily if d["day"] < target_day]
    today_rows = [d for d in daily if d["day"] == target_day]

    if not today_rows:
        return

    today = today_rows[-1]

    def rate_ctr(row):
        impressions = row["impressions"] or 0
        clicks = row["clicks"] or 0
        return (clicks / impressions) * 100 if impressions else 0

    def rate_cpc(row):
        clicks = row["clicks"] or 0
        spend = float(row["spend"] or 0)
        return (spend / clicks) if clicks else 0

    metrics_today = {
        "impressions": today["impressions"] or 0,
        "clicks": today["clicks"] or 0,
        "spend": float(today["spend"] or 0),
        "ctr": rate_ctr(today),
        "cpc": rate_cpc(today),
    }

    metrics_baseline = {
        "impressions": [d["impressions"] or 0 for d in baseline],
        "clicks": [d["clicks"] or 0 for d in baseline],
        "spend": [float(d["spend"] or 0) for d in baseline],
        "ctr": [rate_ctr(d) for d in baseline],
        "cpc": [rate_cpc(d) for d in baseline],
    }

    recommendations = {
        "impressions": "Check reach and audience size changes",
        "clicks": "Review creative performance and targeting",
        "spend": "Audit budget pacing and bid strategy",
        "ctr": "Test new creatives or refine audience targeting",
        "cpc": "Review bids and landing page performance",
    }

    for metric, value in metrics_today.items():
        z = _safe_zscore(metrics_baseline[metric], value)

        if z is None or abs(z) < Z_WARNING:
            continue

        severity = "critical" if abs(z) >= Z_CRITICAL else "warning"
        direction = "above" if z > 0 else "below"
        avg = mean(metrics_baseline[metric])

        insight_type = f"anomaly_{metric}"
        message = (
            f"{metric.upper()} is {direction} normal "
            f"({value:.2f} vs avg {avg:.2f}, z={z:.2f})"
        )

        # Avoid duplicates for same day/type/integration
        exists = Insight.objects.filter(
            integration=integration,
            type=insight_type,
            created_at__date=target_day,
        ).exists()

        if exists:
            continue

        Insight.objects.create(
            integration=integration,
            type=insight_type,
            severity=severity,
            message=message,
            recommendation=recommendations.get(metric, "Review performance changes"),
        )
