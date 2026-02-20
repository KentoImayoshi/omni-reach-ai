from celery import shared_task
from random import randint
from decimal import Decimal
from metrics.models import MetricSnapshot
from integrations.models import IntegrationAccount


@shared_task(bind=True, max_retries=3)
def sync_integration_metrics(self, integration_id):
    try:
        integration = IntegrationAccount.objects.get(id=integration_id)

        # Simula dados externos
        impressions = randint(1000, 5000)
        clicks = randint(100, 500)
        spend = Decimal(randint(1000, 5000)) / 10

        MetricSnapshot.objects.create(
            integration=integration,
            impressions=impressions,
            clicks=clicks,
            spend=spend
        )

        print(f"Metrics saved for integration {integration_id}")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)