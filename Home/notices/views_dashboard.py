from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now

from .models import Notice


class NoticeDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()

        if user.role == 'student':
            queryset = Notice.objects.filter(
                semester__sem_nmbr=user.sem,
                is_active=True
            )
        else:
            queryset = Notice.objects.filter(posted_by=user)

        new_today = queryset.filter(created_at__date=today).count()
        total_active = queryset.count()
        urgent = queryset.filter(notice_type='URGENT').count()

        return Response({
            "new_today": new_today,
            "total_active": total_active,
            "urgent": urgent
        })