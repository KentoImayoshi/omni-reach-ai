from .selectors import get_metrics_summary


def get_company_metrics_summary(*, company, start_date=None, end_date=None):
    summary = get_metrics_summary(
        company=company,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "total_impressions": summary["total_impressions"] or 0,
        "total_clicks": summary["total_clicks"] or 0,
        "total_spend": summary["total_spend"] or 0,
    }