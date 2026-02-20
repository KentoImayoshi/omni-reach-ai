from rest_framework import serializers
from .models import IntegrationAccount


class IntegrationAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationAccount
        fields = [
            "id",
            "platform",
            "access_token",
            "refresh_token",
            "token_expires_at",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]