from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
import os

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('admin/', admin.site.urls),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    path('api/', include('accounts.urls')),
    path('academic/api/', include('Academic.urls')),
    path('resource/api/', include('Resource.urls')),
    path('notice/api/', include('notices.urls')),
    path('Genai/api/', include('chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    # Catch-all MUST be last — serves frontend HTML/JS/CSS files
    re_path(r'^(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR.parent, 'frontend'),
    }),
]
