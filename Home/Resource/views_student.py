from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils.timezone import now

from .models import Resource, ResourceDownload
from accounts.models import User
from Academic.models import Subject
from .serializers import ResourceSerializer


class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'student':
            return Response({"error": "Only students allowed"}, status=403)

        semester = user.sem

        # Recent Resources
        recent_resources = Resource.objects.filter(
            subject__sem__sem_nmbr=semester,
            status='APPROVED'
        ).order_by('-created_at')[:5]

        recent_data = ResourceSerializer(recent_resources, many=True).data

        # My Activity
        downloads = ResourceDownload.objects.filter(student=user).count()
        my_uploads = Resource.objects.filter(uploaded_by=user).count()
        pending = Resource.objects.filter(uploaded_by=user, status='PENDING').count()
        approved = Resource.objects.filter(uploaded_by=user, status='APPROVED').count()

        # Resources by Subject
        subjects = Subject.objects.filter(sem__sem_nmbr=semester)
        subject_stats = []

        for subject in subjects:
            count = Resource.objects.filter(
                subject=subject,
                status='APPROVED'
            ).count()

            subject_stats.append({
                "subject": subject.sub_name,
                "code": subject.sub_code,
                "total_files": count
            })

        return Response({
            "student": {
                "name": user.username,
                "usn": user.usn,
                "semester": semester
            },
            "recent_resources": recent_data,
            "activity": {
                "downloads": downloads,
                "my_uploads": my_uploads,
                "pending": pending,
                "approved": approved
            },
            "resources_by_subject": subject_stats
        })