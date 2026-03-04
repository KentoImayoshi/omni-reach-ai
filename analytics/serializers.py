from rest_framework import serializers
from .models import Insight


class InsightSerializer(serializers.ModelSerializer):
    """
    Serializer for Insight objects.
    """

    class Meta:
        model = Insight
        fields = "__all__"