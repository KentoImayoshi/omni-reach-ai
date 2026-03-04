from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.db.models.functions import TruncMonth

from .models import MetricSnapshot


def get_company_metrics_queryset(company):
    """
    Returns the base queryset filtered by company (multi-tenant safe).
    """
    return MetricSnapshot.objects.filter(
        integration__company=company
    )


def get_metrics_summary(*, company, start_date=None, end_date=None):
    """
    Returns aggregated totals for impressions, clicks, and spend.
    Optional date range filtering.
    """
    queryset = get_company_metrics_queryset(company)

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)

    return queryset.aggregate(
        total_impressions=Sum("impressions"),
        total_clicks=Sum("clicks"),
        total_spend=Sum("spend"),
    )


def get_metrics_daily_breakdown(*, company, start_date=None, end_date=None):
    """
    Returns daily grouped metrics using TruncDate for dashboard charts.
    """
    queryset = get_company_metrics_queryset(company)

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)

    return (
        queryset
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(
            impressions=Sum("impressions"),
            clicks=Sum("clicks"),
            spend=Sum("spend"),
        )
        .order_by("date")
    )

def get_company_monthly_metrics(company, start_date=None, end_date=None):
    """
    Aggregate metrics per month for dashboard charts.
    """

    queryset = MetricSnapshot.objects.filter(
        integration__company=company
    )

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)

    queryset = (
        queryset
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            total_clicks=Sum("clicks"),
            total_impressions=Sum("impressions"),
            total_spend=Sum("spend"),
        )
        .order_by("month")
    )

    return list(queryset)