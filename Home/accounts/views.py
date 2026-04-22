
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer,CustomObtainPair_Serializer
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ModelViewSet
from Academic.models import Subject
# Create your views here.

User=get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
       
        return Response({
            "success": True,
            "message":"User created sucessfuly",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)
      

class Login_view(TokenObtainPairView):
    serializer_class=CustomObtainPair_Serializer
    permission_classes=[AllowAny]




class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'usn': user.usn,
            'sem': user.sem,
            'mobile_number': user.mobile_number
        })


class SubjectViewSet(ModelViewSet):
    # ... existing

    def get_queryset(self):
        queryset = Subject.objects.all()
        user = self.request.user
        sem = self.request.query_params.get('sem')

        if sem:
            queryset = queryset.filter(sem__sem_nmbr=sem)

        if user.role == 'admin':
            return queryset

        elif user.role == 'faculty':
            return queryset.filter(faculty=user)

        return queryset
    