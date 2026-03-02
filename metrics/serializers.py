from rest_framework import serializers
from .models import MetricSnapshot
from datetime import date

class MetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricSnapshot
        fields = "__all__"

class MetricsSummarySerializer(serializers.Serializer):
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    total_spend = serializers.FloatField()
    ctr = serializers.FloatField()

class MetricsSummaryFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")

        if start and end and start > end:
            raise serializers.ValidationError(
                "start_date must be before end_date"
            )

        return attrs