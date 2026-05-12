from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notice, NoticeDismiss
from .serializers import NoticeSerializer, NoticeCreateSerializer
from accounts.permission import IsFacultyOrAdmin


class NoticeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return NoticeCreateSerializer
        return NoticeSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == 'student':
            # Students see notices for their semester, excluding dismissed
            dismissed_ids = NoticeDismiss.objects.filter(
                student=user
            ).values_list('notice_id', flat=True)

            queryset = Notice.objects.exclude(id__in=dismissed_ids)

            if user.sem:
                queryset = queryset.filter(
                    semester__isnull=True
                ) | queryset.filter(semester=user.sem)

            return queryset.order_by('-created_at')

        elif user.role in ['faculty', 'admin']:
            return Notice.objects.filter(posted_by=user).order_by('-created_at')

        return Notice.objects.none()

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        notice = self.get_object()
        NoticeDismiss.objects.get_or_create(notice=notice, student=request.user)
        return Response({"message": "Notice dismissed"})
