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
]

# Always serve media files (works in both DEBUG and production/Railway).
# Django's static() helper only works in DEBUG mode, so we add an explicit
# media-serving pattern that works regardless.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Catch-all MUST be last — serves frontend HTML/JS/CSS files
urlpatterns += [
    re_path(r'^(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR.parent, 'frontend'),
    }),
]
