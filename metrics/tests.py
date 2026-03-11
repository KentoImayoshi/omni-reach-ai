from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from companies.models import Company
from integrations.models import IntegrationAccount
from metrics.models import MetricSnapshot


class MetricSnapshotApiTests(APITestCase):
    def setUp(self):
        company = Company.objects.create(name="Alpha")
        User = get_user_model()
        self.user = User.objects.create_user(
            username="usera",
            password="pass",
            company=company,
        )
        self.integration = IntegrationAccount.objects.create(
            company=company,
            platform="meta",
            access_token="token-a",
        )

        now = timezone.now()

        MetricSnapshot.objects.bulk_create([
            MetricSnapshot(
                integration=self.integration,
                impressions=100,
                clicks=10,
                spend=20.0,
                created_at=now,
            ),
            MetricSnapshot(
                integration=self.integration,
                impressions=200,
                clicks=20,
                spend=40.0,
                created_at=now,
            ),
            MetricSnapshot(
                integration=self.integration,
                impressions=300,
                clicks=30,
                spend=60.0,
                created_at=now,
            ),
        ])

    def test_metrics_list_is_paginated(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/metrics/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 3)
