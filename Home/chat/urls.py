from django.urls import path
from .views import UploadPDFView, ChatView, GenAIView

urlpatterns = [
    path('upload/', UploadPDFView.as_view(), name='pdf-upload'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('genai/', GenAIView.as_view(), name='genai'),
]