from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Sem
from .serializers import SemesterSerializer
from .permission import IsAdminOnly
from .models import Subject
from .serializers import SubjectSerializer
# Create your views here.

class SemesterViewSet(ModelViewSet):
    queryset = Sem.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]







class SubjectViewSet(ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return Subject.objects.all()

        elif user.role == 'faculty':
            return Subject.objects.filter(faculty=user)

        return Subject.objects.all() 