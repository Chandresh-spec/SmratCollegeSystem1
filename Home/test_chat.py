import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Home.settings')
django.setup()

from chat.models import AnonChatRoom
from Resource.models import Resource
from Academic.models import Subject
from chat.views import ChatView
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.post('/Genai/api/chat/', {'subject_id': 1, 'question': 'What is this?'}, format='json')
view = ChatView.as_view()

try:
    response = view(request)
    print("STATUS:", response.status_code)
    print("DATA:", response.data)
except Exception as e:
    import traceback
    traceback.print_exc()
