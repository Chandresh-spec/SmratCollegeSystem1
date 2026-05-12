from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import PDFDocument
from Resource.models import Resource
from .rag_utils import extract_text_from_pdf, chunk_text, create_faiss_index, search_chunks
from .llm import ask_llm

# Temporary in-memory vector store (subject_id -> FAISS index + chunks)
VECTOR_STORE = {}

class UploadPDFView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        pdf = request.FILES.get("pdf")
        subject_id = request.data.get("subject_id")

        if not pdf or not subject_id:
            return Response({"error": "PDF and subject_id required"}, status=400)

        # Save PDF in DB
        doc = PDFDocument.objects.create(
            subject_id=subject_id,
            file=pdf
        )

        return Response({"message": "Legacy prototype Endpoint. Use Resource module."})


class ChatView(APIView):
    def post(self, request):
        subject_id = str(request.data.get("subject_id"))
        question = request.data.get("question")

        if not question or not subject_id:
            return Response({"error": "subject_id and question required"}, status=400)

        subject_data = VECTOR_STORE.get(subject_id)
        
        # Lazy-load if not in cache but exists in DB
        if not subject_data:
            # Check if we have official Resource PDFs for this subject in the DB
            docs = Resource.objects.filter(subject_id=subject_id, file_type='PDF', status='APPROVED')
            
            if not docs.exists():
                return Response({"error": "No official PDFs found for this subject"}, status=400)
            
            # Combine all texts from PDFs for this subject
            combined_text = ""
            for doc in docs:
                try:
                    if doc.file:
                        combined_text += extract_text_from_pdf(doc.file.path) + "\n"
                except Exception as e:
                    print(f"Error reading {doc.file.path}: {e}")
            
            if not combined_text.strip():
                return Response({"error": "Could not extract text from stored PDFs"}, status=400)
                
            chunks = chunk_text(combined_text)
            index, chunks = create_faiss_index(chunks)
            
            VECTOR_STORE[subject_id] = {
                "index": index,
                "chunks": chunks
            }
            subject_data = VECTOR_STORE[subject_id]

        index = subject_data["index"]
        chunks_data = subject_data["chunks"]

        # Retrieve top 5 relevant chunks
        relevant_chunks = search_chunks(question, index, chunks_data, top_k=5)
        if not relevant_chunks:
            return Response({"answer": "No relevant content found in PDF notes."})

        context = "\n".join(relevant_chunks)
        answer = ask_llm(context, question)

        return Response({"answer": answer})

class GenAIView(APIView):
    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "question required"}, status=400)
        
        answer = ask_llm("", question)
        return Response({"answer": answer})
