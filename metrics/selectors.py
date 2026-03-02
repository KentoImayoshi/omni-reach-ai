from django.db.models import Sum
from .models import MetricSnapshot


def get_company_metrics_queryset(company):
    return MetricSnapshot.objects.filter(
        integration__company=company
    )


def get_metrics_summary(*, company, start_date=None, end_date=None):
    queryset = MetricSnapshot.objects.filter(
        integration__company=company
    )

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)

    return queryset.aggregate(
        total_impressions=Sum("impressions"),
        total_clicks=Sum("clicks"),
        total_spend=Sum("spend"),
    )