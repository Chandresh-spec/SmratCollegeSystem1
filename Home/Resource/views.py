from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from .models import Resource, ResourceDownload
from .serializers import ResourceSerializer, ResourceCreateSerializer
from accounts.permission import IsAdmin
from Academic.models import Subject


# ─── Main Resource ViewSet (Faculty + Student + Admin) ────────────────

class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ResourceCreateSerializer
        return ResourceSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Resource.objects.all()

        if user.role == 'student':
            queryset = queryset.filter(Q(status='APPROVED') | Q(uploaded_by=user))
        elif user.role == 'faculty':
            queryset = queryset.filter(subject__faculty=user)

        subject_code = self.request.query_params.get('subject_code')
        semester = self.request.query_params.get('semester')
        professor = self.request.query_params.get('professor')

        if subject_code:
            queryset = queryset.filter(subject__sub_code=subject_code)
        if semester:
            queryset = queryset.filter(subject__sem__sem_nmbr=semester)
        if professor:
            queryset = queryset.filter(subject__faculty__username=professor)

        return queryset.select_related(
            'subject', 'subject__sem', 'subject__faculty', 'uploaded_by'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        resource = self.get_object()
        if request.user.role not in ['admin', 'faculty']:
            return Response({"error": "Not allowed"}, status=403)
        resource.status = 'APPROVED'
        resource.save()
        return Response({"message": "Resource Approved"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        resource = self.get_object()
        if request.user.role not in ['admin', 'faculty']:
            return Response({"error": "Not allowed"}, status=403)
        resource.status = 'REJECTED'
        resource.save()
        return Response({"message": "Resource Rejected"})


# ─── Review ViewSet (Admin — pending resources) ──────────────────────

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.filter(status='PENDING')
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        resource = self.get_object()
        resource.status = 'APPROVED'
        resource.save()
        return Response({"message": "Approved"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        resource = self.get_object()
        resource.status = 'REJECTED'
        resource.save()
        return Response({"message": "Rejected"})


# ─── Student Resource ViewSet ────────────────────────────────────────

class StudentResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """Students see only APPROVED resources from their semester."""
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'student':
            return Resource.objects.none()

        semester = user.sem
        if not semester:
            return Resource.objects.none()

        return Resource.objects.filter(
            subject__sem__sem_nmbr=semester,
            status='APPROVED'
        ).select_related(
            'subject', 'subject__sem', 'subject__faculty', 'uploaded_by'
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        resource = self.get_object()
        resource.view_count += 1
        resource.save(update_fields=['view_count'])
        ResourceDownload.objects.get_or_create(student=request.user, resource=resource)
        return Response({"message": "Download recorded", "view_count": resource.view_count})


# ─── Student Dashboard ───────────────────────────────────────────────

class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'student':
            return Response({"error": "Only students allowed"}, status=403)

        semester = user.sem
        if not semester:
            return Response({"error": "Student semester not set"}, status=400)

        recent = Resource.objects.filter(
            subject__sem__sem_nmbr=semester, status='APPROVED'
        ).select_related(
            'subject', 'subject__sem', 'subject__faculty', 'uploaded_by'
        ).order_by('-created_at')[:10]

        downloads = ResourceDownload.objects.filter(student=user).count()
        my_uploads = Resource.objects.filter(uploaded_by=user).count()
        pending = Resource.objects.filter(uploaded_by=user, status='PENDING').count()
        approved = Resource.objects.filter(uploaded_by=user, status='APPROVED').count()

        subjects = Subject.objects.filter(sem__sem_nmbr=semester)
        subject_stats = [{
            "subject": s.sub_name,
            "code": s.sub_code,
            "total_files": Resource.objects.filter(subject=s, status='APPROVED').count()
        } for s in subjects]

        return Response({
            "student": {"name": user.username, "usn": user.usn or "N/A", "semester": semester},
            "recent_resources": ResourceSerializer(recent, many=True).data,
            "activity": {
                "downloads": downloads,
                "my_uploads": my_uploads,
                "pending": pending,
                "approved": approved
            },
            "resources_by_subject": subject_stats
        })


# ─── Resource Filter ─────────────────────────────────────────────────

class ResourceFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'student':
            return Response({"error": "Only students allowed"}, status=403)

        semester = user.sem
        if not semester:
            return Response([])

        queryset = Resource.objects.filter(
            subject__sem__sem_nmbr=semester, status='APPROVED'
        ).select_related('subject', 'subject__sem', 'subject__faculty', 'uploaded_by')

        subject_code = request.GET.get('subject')
        professor = request.GET.get('professor')
        file_type = request.GET.get('type')

        if subject_code:
            queryset = queryset.filter(subject__sub_code=subject_code)
        if professor:
            queryset = queryset.filter(uploaded_by__username=professor)
        if file_type:
            queryset = queryset.filter(file_type=file_type)

        return Response(ResourceSerializer(queryset.order_by('-created_at'), many=True).data)


# ─── Resource Search ─────────────────────────────────────────────────

class ResourceSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'student':
            return Response({"error": "Only students allowed"}, status=403)

        query = request.GET.get('q', '').strip()
        semester = user.sem

        if not semester or not query:
            return Response([])

        queryset = Resource.objects.filter(
            subject__sem__sem_nmbr=semester,
            status='APPROVED',
            title__icontains=query
        ).select_related(
            'subject', 'subject__sem', 'subject__faculty', 'uploaded_by'
        ).order_by('-created_at')

        return Response(ResourceSerializer(queryset, many=True).data)