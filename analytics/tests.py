from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from companies.models import Company
from integrations.models import IntegrationAccount
from metrics.models import MetricSnapshot
from analytics.models import Insight as AnalyticsInsight
from analytics.models_aggregates import MetricsAggregate
from analytics.services.aggregates import update_daily_aggregate


class AnalyticsApiTests(APITestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name="Alpha")
        self.company_b = Company.objects.create(name="Beta")

        User = get_user_model()
        self.user_a = User.objects.create_user(
            username="usera",
            password="pass",
            company=self.company_a,
        )
        self.user_b = User.objects.create_user(
            username="userb",
            password="pass",
            company=self.company_b,
        )

        self.integration_a = IntegrationAccount.objects.create(
            company=self.company_a,
            platform="meta",
            access_token="token-a",
        )
        self.integration_b = IntegrationAccount.objects.create(
            company=self.company_b,
            platform="google",
            access_token="token-b",
        )

        now = timezone.now()

        MetricSnapshot.objects.bulk_create([
            MetricSnapshot(
                integration=self.integration_a,
                impressions=100,
                clicks=10,
                spend=20.50,
                created_at=now,
            ),
            MetricSnapshot(
                integration=self.integration_b,
                impressions=999,
                clicks=99,
                spend=199.00,
                created_at=now,
            ),
        ])

    def test_dashboard_scoped_to_company(self):
        AnalyticsInsight.objects.create(
            integration=self.integration_a,
            type="anomaly_clicks",
            severity="warning",
            message="A insight",
            recommendation="R",
        )
        AnalyticsInsight.objects.create(
            integration=self.integration_b,
            type="anomaly_clicks",
            severity="warning",
            message="B insight",
            recommendation="R",
        )

        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, 200)

        summary = response.data["summary"]
        self.assertEqual(summary["impressions"], 100)
        self.assertEqual(summary["clicks"], 10)
        self.assertEqual(float(summary["spend"]), 20.50)

        platforms = {item["integration__platform"] for item in response.data["top_integrations"]}
        self.assertEqual(platforms, {"meta"})

        insight_messages = {item["message"] for item in response.data["insights"]}
        self.assertEqual(insight_messages, {"A insight"})

    def test_insights_list_scoped_to_company(self):
        AnalyticsInsight.objects.create(
            integration=self.integration_a,
            type="anomaly_clicks",
            severity="warning",
            message="A insight",
            recommendation="R",
        )
        AnalyticsInsight.objects.create(
            integration=self.integration_b,
            type="anomaly_clicks",
            severity="warning",
            message="B insight",
            recommendation="R",
        )

        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/insights/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        result = response.data["results"][0]
        self.assertEqual(str(result["integration"]), str(self.integration_a.id))

    def test_latest_insight_scoped_to_company(self):
        now = timezone.now()

        a_old = AnalyticsInsight.objects.create(
            integration=self.integration_a,
            type="anomaly_ctr",
            severity="warning",
            message="A old",
            recommendation="R",
        )
        a_new = AnalyticsInsight.objects.create(
            integration=self.integration_a,
            type="anomaly_ctr",
            severity="warning",
            message="A new",
            recommendation="R",
        )
        b_new = AnalyticsInsight.objects.create(
            integration=self.integration_b,
            type="anomaly_ctr",
            severity="warning",
            message="B new",
            recommendation="R",
        )

        AnalyticsInsight.objects.filter(id=a_old.id).update(
            created_at=now - timedelta(days=1)
        )
        AnalyticsInsight.objects.filter(id=a_new.id).update(
            created_at=now + timedelta(minutes=1)
        )
        AnalyticsInsight.objects.filter(id=b_new.id).update(
            created_at=now + timedelta(days=1)
        )

        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/insights/latest/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "A new")

    def test_update_daily_aggregate(self):
        now = timezone.now()

        snapshot_1 = MetricSnapshot.objects.create(
            integration=self.integration_a,
            impressions=100,
            clicks=10,
            spend=25.00,
            created_at=now,
        )
        snapshot_2 = MetricSnapshot.objects.create(
            integration=self.integration_a,
            impressions=50,
            clicks=5,
            spend=10.00,
            created_at=now,
        )

        update_daily_aggregate(snapshot_1)
        update_daily_aggregate(snapshot_2)

        agg = MetricsAggregate.objects.get(
            integration=self.integration_a,
            date=timezone.localdate(now),
        )

        self.assertEqual(agg.total_impressions, 150)
        self.assertEqual(agg.total_clicks, 15)
        self.assertAlmostEqual(agg.total_spend, 35.00, places=2)
        self.assertAlmostEqual(agg.avg_ctr, 10.0, places=2)
        self.assertAlmostEqual(agg.avg_cpc, 35.00 / 15, places=3)
