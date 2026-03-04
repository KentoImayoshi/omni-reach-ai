from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Insight
from .serializers import InsightSerializer


class InsightsListView(APIView):
    """
    Return insights for the authenticated user.
    """

    def get(self, request):

        insights = Insight.objects.all()[:50]

        serializer = InsightSerializer(insights, many=True)

        return Response({
            "insights": serializer.data
        })