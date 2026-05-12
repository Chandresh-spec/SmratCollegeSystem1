from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    path('api/', include('accounts.urls')),
    path('academic/api/', include('Academic.urls')),
    path('resource/api/', include('Resource.urls')),
    path('notice/api/', include('notices.urls')),
    path('Genai/api/', include('chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
