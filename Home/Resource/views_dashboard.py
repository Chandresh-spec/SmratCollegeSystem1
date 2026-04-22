from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from django.db.models import Count, Sum
from datetime import timedelta

from .models import Resource
from accounts.models import User


class FacultyDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        # Total Resources (faculty uploads)
        total_resources = Resource.objects.filter(uploaded_by=user).count()

        # Pending Approvals
        pending = Resource.objects.filter(status='PENDING').count()

        # Views Today
        today = now().date()
        views_today = Resource.objects.filter(
            created_at__date=today
        ).aggregate(total=Sum('view_count'))['total'] or 0

        # Active Students (example logic: students in faculty semester)
        active_students = User.objects.filter(role='student').count()

        # Recent Uploads
        recent_uploads = Resource.objects.filter(
            uploaded_by=user
        ).order_by('-created_at')[:5]

        recent_data = [
            {
                "id": r.id,
                "title": r.title,
                "subject": r.subject.sub_code,
                "status": r.status,
                "views": r.view_count,
                "created_at": r.created_at
            }
            for r in recent_uploads
        ]

        return Response({
            "total_resources": total_resources,
            "pending_approvals": pending,
            "views_today": views_today,
            "active_students": active_students,
            "recent_uploads": recent_data
        })