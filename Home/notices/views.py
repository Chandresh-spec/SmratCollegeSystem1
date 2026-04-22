from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now

from .models import Notice, NoticeDismiss
from .serializers import NoticeSerializer, NoticeCreateSerializer
# Create your views here.

class NoticeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return NoticeCreateSerializer
        return NoticeSerializer

    def get_queryset(self):
        user = self.request.user

        # Faculty sees notices they posted
        if user.role == 'faculty':
            return Notice.objects.filter(posted_by=user)

        # Students see only their semester notices
        if user.role == 'student':
            return Notice.objects.filter(
                semester__sem_nmbr=user.sem,
                is_active=True
            ).exclude(
                noticedismiss__student=user
            )

        # Admin sees all
        if user.role == 'admin':
            return Notice.objects.all()

        return Notice.objects.none()

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    # Dismiss notice
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        notice = self.get_object()

        if request.user.role != 'student':
            return Response({"error": "Only students can dismiss"}, status=403)

        NoticeDismiss.objects.get_or_create(
            notice=notice,
            student=request.user
        )

        return Response({"message": "Notice dismissed"})

