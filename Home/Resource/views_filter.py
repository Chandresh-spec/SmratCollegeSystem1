from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Resource
from .serializers import ResourceSerializer


class ResourceFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        queryset = Resource.objects.filter(
            subject__sem__sem_nmbr=user.sem,
            status='APPROVED'
        )

        subject = request.GET.get('subject')
        professor = request.GET.get('professor')
        file_type = request.GET.get('type')

        if subject:
            queryset = queryset.filter(subject__sub_code=subject)

        if professor:
            queryset = queryset.filter(subject__faculty__username=professor)

        if file_type:
            queryset = queryset.filter(file_type=file_type)

        serializer = ResourceSerializer(queryset, many=True)
        return Response(serializer.data)