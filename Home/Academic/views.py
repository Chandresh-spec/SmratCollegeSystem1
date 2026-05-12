from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Sem, Subject
from .serializers import SemesterSerializer, SubjectSerializer, SubjectCreateSerializer
from accounts.permission import IsFacultyOrAdmin


class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sem.objects.all().order_by('sem_nmbr')
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return SubjectCreateSerializer
        return SubjectSerializer

    def get_queryset(self):
        queryset = Subject.objects.all().select_related('sem', 'faculty')
        sem = self.request.query_params.get('semester')
        if sem:
            queryset = queryset.filter(sem__sem_nmbr=sem)
        return queryset.order_by('sub_code')