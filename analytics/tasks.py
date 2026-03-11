"""
Celery tasks responsible for processing metric snapshots
and generating insights asynchronously.
"""

from celery import shared_task

from metrics.models import MetricSnapshot
from analytics.services.insight_engine import generate_and_store_insights
from analytics.services.anomaly_engine import generate_and_store_anomalies


@shared_task
def process_snapshot(snapshot_id):
    """
    Process a metric snapshot and generate insights.
    """

    try:
        snapshot = MetricSnapshot.objects.get(id=snapshot_id)
    except MetricSnapshot.DoesNotExist:
        return

    generate_and_store_insights(snapshot)
    generate_and_store_anomalies(snapshot)
