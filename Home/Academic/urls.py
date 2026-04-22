from rest_framework.routers import DefaultRouter
from .views import SemesterViewSet, SubjectViewSet
from django.urls import path,include

router = DefaultRouter()
router.register(r'semesters', SemesterViewSet, basename='semesters')
router.register(r'subjects', SubjectViewSet, basename='subjects')

urlpatterns = [
    path('',include(router.urls))
]