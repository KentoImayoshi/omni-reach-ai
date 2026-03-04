from celery import shared_task

from analytics.models import MetricSnapshot
from analytics.services.insight_engine import generate_and_store_insights


@shared_task
def process_snapshot(snapshot_id):
    """
    Process a metric snapshot and generate insights.
    """

    snapshot = MetricSnapshot.objects.get(id=snapshot_id)

    generate_and_store_insights(snapshot)