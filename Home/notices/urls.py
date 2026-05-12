from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoticeViewSet

router = DefaultRouter()
router.register(r'notices', NoticeViewSet, basename='notices')

urlpatterns = [
    path('', include(router.urls)),
]