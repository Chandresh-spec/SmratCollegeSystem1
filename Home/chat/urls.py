from django.urls import path
from .views import UploadPDFView, ChatView

urlpatterns = [
    path("upload/", UploadPDFView.as_view()),
    path("chat/", ChatView.as_view()),
]