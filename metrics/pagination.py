from rest_framework.pagination import PageNumberPagination


class MetricSnapshotPagination(PageNumberPagination):
    """
    Pagination for metric snapshots to prevent large payloads.
    """

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200
