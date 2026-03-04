from analytics.models import MetricSnapshot


def get_metrics_by_integration(integration_id):

    return MetricSnapshot.objects.filter(
        integration_id=integration_id
    )