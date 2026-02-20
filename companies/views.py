from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Company.objects.filter(id=self.request.user.company_id)

    def perform_create(self, serializer):
        company = serializer.save()
        self.request.user.company = company
        self.request.user.save()