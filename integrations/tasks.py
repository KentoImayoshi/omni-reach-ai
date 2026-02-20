from celery import shared_task
from random import randint
from decimal import Decimal
from metrics.models import MetricSnapshot
from integrations.models import IntegrationAccount
from alerts.models import Insight
from alerts.llm_service import generate_insight


@shared_task(bind=True, max_retries=3)
def sync_integration_metrics(self, integration_id):
    try:
        integration = IntegrationAccount.objects.get(id=integration_id)

        impressions = randint(1000, 5000)
        clicks = randint(100, 500)
        spend = Decimal(randint(1000, 5000)) / 10

        metric = MetricSnapshot.objects.create(
            integration=integration,
            impressions=impressions,
            clicks=clicks,
            spend=spend
        )

        # 🔥 AI Insight generation
        summary = generate_insight(impressions, clicks, spend)

        Insight.objects.create(
            metric_snapshot=metric,
            summary=summary
        )

        print(f"Metrics + Insight saved for integration {integration_id}")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)