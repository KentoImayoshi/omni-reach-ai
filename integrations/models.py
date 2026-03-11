from functools import lru_cache
import uuid

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


@lru_cache(maxsize=1)
def _get_fernet():
    key = settings.INTEGRATION_TOKENS_KEY
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


def _encrypt_token(value):
    if not value:
        return value
    if value.startswith("enc:"):
        return value
    return "enc:" + _get_fernet().encrypt(value.encode()).decode()


def _decrypt_token(value):
    if not value:
        return value
    if not value.startswith("enc:"):
        return value
    payload = value[4:]
    try:
        return _get_fernet().decrypt(payload.encode()).decode()
    except InvalidToken:
        return None


class IntegrationAccount(models.Model):
    PLATFORM_CHOICES = [
        ("meta", "Meta"),
        ("apple", "Apple"),
        ("google", "Google"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="integrations"
    )

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "platform")
        indexes = [
            models.Index(fields=["company", "platform"]),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.platform}"

    @property
    def access_token_value(self):
        return _decrypt_token(self.access_token)

    @property
    def refresh_token_value(self):
        return _decrypt_token(self.refresh_token)

    def save(self, *args, **kwargs):
        if self.access_token:
            self.access_token = _encrypt_token(self.access_token)
        if self.refresh_token:
            self.refresh_token = _encrypt_token(self.refresh_token)
        super().save(*args, **kwargs)
