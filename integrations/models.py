from django.db import models
import uuid


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