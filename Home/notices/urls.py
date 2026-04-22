from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoticeViewSet
from .views_dashboard import NoticeDashboardView

router = DefaultRouter()
router.register(r'notices', NoticeViewSet, basename='notices')

urlpatterns = [
    path('dashboard/', NoticeDashboardView.as_view()),
    path('', include(router.urls)),
]