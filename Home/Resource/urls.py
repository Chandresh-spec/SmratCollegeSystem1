from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_student import StudentDashboardView
from .views_filter import ResourceFilterView
from .views import StudentResourceViewSet
from .views import ResourceSearchView

from .views import StudentDashboardView,ResourceFilterView,ResourceViewSet
from .views_dashboard import FacultyDashboardView

router = DefaultRouter()
router.register(r'student/resources', StudentResourceViewSet, basename='student-resource')

router.register(r'resources', ResourceViewSet, basename='resources')

urlpatterns = [
    path('faculty/dashboard/',FacultyDashboardView.as_view()),
    path('student/dashboard/', StudentDashboardView.as_view()),
    path('student/filter/', ResourceFilterView.as_view()),
    path('student/search/', ResourceSearchView.as_view()),
    path('', include(router.urls)),
]