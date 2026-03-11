from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from companies.models import Company
from integrations.models import IntegrationAccount


class IntegrationApiTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Alpha")
        User = get_user_model()
        self.user = User.objects.create_user(
            username="usera",
            password="pass",
            company=self.company,
        )

    def test_create_integration_hides_tokens(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "platform": "meta",
            "access_token": "secret-token",
            "refresh_token": "refresh-token",
            "is_active": True,
        }

        response = self.client.post("/api/integrations/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("access_token", response.data)
        self.assertNotIn("refresh_token", response.data)

        account = IntegrationAccount.objects.get(id=response.data["id"])
        self.assertTrue(account.access_token.startswith("enc:"))
        self.assertEqual(account.access_token_value, "secret-token")
        self.assertEqual(account.refresh_token_value, "refresh-token")

    def test_list_integrations_hides_tokens(self):
        IntegrationAccount.objects.create(
            company=self.company,
            platform="meta",
            access_token="secret-token",
            refresh_token="refresh-token",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/integrations/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        item = response.data[0]
        self.assertNotIn("access_token", item)
        self.assertNotIn("refresh_token", item)
