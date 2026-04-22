from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Resource
from .serializers import ResourceSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from accounts.permission import IsAdmin
from rest_framework import viewsets
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Resource
from .serializers import ResourceSerializer, ResourceCreateSerializer
from accounts.permission import IsFacultyOrAdmin
from rest_framework.views import APIView
from .models import  ResourceDownload

class ResourceViewSet(ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Resource.objects.all()

        # Students see only approved
        if user.role == 'student':
            queryset = queryset.filter(status='APPROVED')

        # Faculty sees their subject resources
        elif user.role == 'faculty':
            queryset = queryset.filter(subject__faculty=user)

        # Filtering
        subject_code = self.request.query_params.get('subject_code')
        semester = self.request.query_params.get('semester')
        professor = self.request.query_params.get('professor')

        if subject_code:
            queryset = queryset.filter(subject__sub_code=subject_code)

        if semester:
            queryset = queryset.filter(subject__sem__sem_nmbr=semester)

        if professor:
            queryset = queryset.filter(subject__faculty__username=professor)

        return queryset

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




class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ResourceCreateSerializer
        return ResourceSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Resource.objects.all()

        if user.role == 'student':
            queryset = queryset.filter(Q(status='APPROVED') | Q(uploaded_by=user))  # Show approved + my own (any status)

        elif user.role == 'faculty':
            queryset = queryset.filter(subject__faculty=user)
    






from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response

class StudentResourceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resource.objects.filter(
            subject__sem__sem_nmbr=self.request.user.sem,
            status='APPROVED'
        )

    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        resource = self.get_object()

        resource.view_count += 1
        resource.save()

        ResourceDownload.objects.get_or_create(
            student=request.user,
            resource=resource
        )

        return Response({"message": "Download recorded"})
    






class ResourceSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q')

        queryset = Resource.objects.filter(
            subject__sem__sem_nmbr=request.user.sem,
            status='APPROVED',
            title__icontains=query
        )

        serializer = ResourceSerializer(queryset, many=True)
        return Response(serializer.data)




    



from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.db.models import Count, Sum, Q
from django.utils.timezone import now

from .models import Resource, ResourceDownload
from .serializers import ResourceSerializer, ResourceCreateSerializer
from accounts.permission import IsAdmin, IsFacultyOrAdmin
from accounts.models import User
from Academic.models import Subject


# ============================================================
# STUDENT VIEWS
# ============================================================

class StudentResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Student can only view APPROVED resources from their semester.
    Teacher uploads are automatically approved, so they appear instantly.
    """
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Only students can use this viewset
        if user.role != 'student':
            return Resource.objects.none()
        
        # Get student's semester
        student_semester = user.sem
        
        if not student_semester:
            return Resource.objects.none()
        
        # Return APPROVED resources from subjects in student's semester
        return Resource.objects.filter(
            subject_sem_sem_nmbr=student_semester,
            status='APPROVED'
        ).select_related(
            'subject', 
            'subject__sem', 
            'subject__faculty',
            'uploaded_by'
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Record download and increment view count"""
        resource = self.get_object()

        # Increment view count
        resource.view_count += 1
        resource.save(update_fields=['view_count'])

        # Create download record (get_or_create prevents duplicates)
        ResourceDownload.objects.get_or_create(
            student=request.user,
            resource=resource
        )

        return Response({
            "message": "Download recorded",
            "view_count": resource.view_count
        })


class StudentDashboardView(APIView):
    """
    GET /resource/api/student/dashboard/
    Returns: student info, recent resources, activity stats, subject stats
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'student':
            return Response(
                {"error": "Only students allowed"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        semester = user.sem

        if not semester:
            return Response({
                "error": "Student semester not set"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Recent Resources (approved, from student's semester)
        recent_resources = Resource.objects.filter(
            subject_sem_sem_nmbr=semester,
            status='APPROVED'
        ).select_related(
            'subject',
            'subject__sem',
            'subject__faculty',
            'uploaded_by'
        ).order_by('-created_at')[:10]

        recent_data = ResourceSerializer(recent_resources, many=True).data

        # My Activity
        downloads = ResourceDownload.objects.filter(student=user).count()
        my_uploads = Resource.objects.filter(uploaded_by=user).count()
        pending = Resource.objects.filter(
            uploaded_by=user, 
            status='PENDING'
        ).count()
        approved = Resource.objects.filter(
            uploaded_by=user, 
            status='APPROVED'
        ).count()

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
                "usn": user.usn or "N/A",
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


class ResourceFilterView(APIView):
    """
    GET /resource/api/student/filter/
    Query params: subject (sub_code), professor (username), type (file_type)
    Returns filtered resources for student's semester
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'student':
            return Response(
                {"error": "Only students allowed"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        semester = user.sem
        
        if not semester:
            return Response([])

        # Base queryset: approved resources from student's semester
        queryset = Resource.objects.filter(
            subject_sem_sem_nmbr=semester,
            status='APPROVED'
        ).select_related(
            'subject',
            'subject__sem',
            'subject__faculty',
            'uploaded_by'
        )

        # Apply filters
        subject_code = request.GET.get('subject')
        professor = request.GET.get('professor')
        file_type = request.GET.get('type')

        if subject_code:
            queryset = queryset.filter(subject__sub_code=subject_code)

        if professor:
            queryset = queryset.filter(uploaded_by__username=professor)

        if file_type:
            queryset = queryset.filter(file_type=file_type)

        queryset = queryset.order_by('-created_at')
        serializer = ResourceSerializer(queryset, many=True)
        return Response(serializer.data)


class ResourceSearchView(APIView):
    """
    GET /resource/api/student/search/?q=...
    Search resources by title in student's semester
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if user.role != 'student':
            return Response(
                {"error": "Only students allowed"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        query = request.GET.get('q', '').strip()
        semester = user.sem

        if not semester or not query:
            return Response([])

        queryset = Resource.objects.filter(
            subject_sem_sem_nmbr=semester,
            status='APPROVED',
            title__icontains=query
        ).select_related(
            'subject',
            'subject__sem',
            'subject__faculty',
            'uploaded_by'
        ).order_by('-created_at')

        serializer = ResourceSerializer(queryset, many=True)
        return Response(serializer.data)