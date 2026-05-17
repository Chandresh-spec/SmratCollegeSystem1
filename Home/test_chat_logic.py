import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Home.settings')
django.setup()

from Resource.models import Resource
from chat.rag_utils import extract_text_from_pdf, chunk_text, create_faiss_index, search_chunks
from chat.llm import ask_llm

try:
    subject_id = "1"  # "Fundamentals of Computers"
    question = "What is this?"
    
    docs = Resource.objects.filter(subject_id=subject_id, file_type='PDF', status='APPROVED')
    print("Found docs:", docs.count())
    
    if not docs.exists():
        print("No official PDFs found for this subject")
        exit()
        
    combined_text = ""
    for doc in docs:
        try:
            if doc.file:
                print(f"Reading {doc.file.path}")
                combined_text += extract_text_from_pdf(doc.file.path) + "\n"
        except Exception as e:
            print(f"Error reading {doc.file.path}: {e}")
            
    if not combined_text.strip():
        print("Could not extract text from stored PDFs")
        exit()
        
    print("Chunking...")
    chunks = chunk_text(combined_text)
    print("Creating index...")
    index, chunks = create_faiss_index(chunks)
    
    print("Searching...")
    relevant_chunks = search_chunks(question, index, chunks, top_k=5)
    print("Found relevant chunks:", len(relevant_chunks))
    
    context = "\n".join(relevant_chunks)
    print("Asking LLM...")
    answer = ask_llm(context, question)
    print("LLM Answer:", answer)
except Exception as e:
    import traceback
    traceback.print_exc()
