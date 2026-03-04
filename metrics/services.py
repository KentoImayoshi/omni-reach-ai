from .selectors import (
    get_metrics_summary,
    get_metrics_daily_breakdown,
)
from django.core.cache import cache


def get_company_metrics_summary(*, company, start_date=None, end_date=None):
    """
    Returns formatted summary response.
    Converts None values to zero.
    """
    summary = get_metrics_summary(
        company=company,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "total_impressions": summary["total_impressions"] or 0,
        "total_clicks": summary["total_clicks"] or 0,
        "total_spend": float(summary["total_spend"] or 0),
    }


def get_company_daily_breakdown(*, company, start_date=None, end_date=None):
    """
    Returns formatted daily breakdown for frontend charts.
    """
    data = get_metrics_daily_breakdown(
        company=company,
        start_date=start_date,
        end_date=end_date,
    )

    return [
        {
            "date": item["date"],
            "impressions": item["impressions"] or 0,
            "clicks": item["clicks"] or 0,
            "spend": float(item["spend"] or 0),
        }
        for item in data
    ]

def invalidate_metrics_cache(company_id):
    """
    Clear cached metric summaries when new data arrives.
    This prevents stale dashboard data.
    """

    cache.delete_pattern(f"metrics_summary:{company_id}:*")
    cache.delete_pattern(f"metrics_daily:{company_id}:*")