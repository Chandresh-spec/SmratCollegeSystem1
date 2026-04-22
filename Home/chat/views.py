from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import PDFDocument
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

        # Extract text, chunk, and create FAISS index
        text = extract_text_from_pdf(doc.file.path)
        chunks = chunk_text(text)
        index, chunks = create_faiss_index(chunks)

        VECTOR_STORE[subject_id] = {
            "index": index,
            "chunks": chunks
        }

        return Response({"message": "PDF uploaded and processed successfully."})


class ChatView(APIView):
    def post(self, request):
        subject_id = str(request.data.get("subject_id"))
        question = request.data.get("question")

        if not question or not subject_id:
            return Response({"error": "subject_id and question required"}, status=400)

        subject_data = VECTOR_STORE.get(subject_id)
        if not subject_data:
            return Response({"error": "No PDF found for this subject"}, status=400)

        index = subject_data["index"]
        chunks_data = subject_data["chunks"]

        # Retrieve top 5 relevant chunks
        relevant_chunks = search_chunks(question, index, chunks_data, top_k=5)
        if not relevant_chunks:
            return Response({"answer": "No relevant content found in PDF."})

        context = "\n".join(relevant_chunks)
        answer = ask_llm(context, question)

        print(VECTOR_STORE)

        return Response({"answer": answer})
