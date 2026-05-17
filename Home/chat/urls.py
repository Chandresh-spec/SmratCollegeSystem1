from django.urls import path
from .views import UploadPDFView, ChatView, GenAIView, AnonChatRoomListView, AnonChatMessageView

urlpatterns = [
    path('upload/', UploadPDFView.as_view(), name='pdf-upload'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('genai/', GenAIView.as_view(), name='genai'),
    path('anon-rooms/', AnonChatRoomListView.as_view(), name='anon-rooms'),
    path('anon-rooms/<int:room_id>/messages/', AnonChatMessageView.as_view(), name='anon-messages'),
]