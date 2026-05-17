import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Home.settings')
django.setup()

from chat.rag_utils import create_faiss_index
import traceback

try:
    chunks = ["Hello world", "This is a test"]
    index, c = create_faiss_index(chunks)
    print("Success! Index created:", index.ntotal)
except Exception as e:
    traceback.print_exc()
