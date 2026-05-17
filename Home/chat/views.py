from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import PDFDocument
from Resource.models import Resource
from .rag_utils import extract_text_from_pdf, chunk_text, create_faiss_index, search_chunks
from .llm import ask_llm
import os

# Temporary in-memory vector store (subject_id -> FAISS index + chunks)
VECTOR_STORE = {}

# Track which uploaded PDFs map to which subject_id
UPLOAD_REGISTRY = {}


def _index_pdf_file(file_path, subject_id):
    """Helper: extract text from a PDF, chunk it, index it, store in VECTOR_STORE."""
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        return False
    
    chunks = chunk_text(text)
    index, chunks_data = create_faiss_index(chunks)
    
    VECTOR_STORE[subject_id] = {
        "index": index,
        "chunks": chunks_data
    }
    print(f"[RAG] Indexed {len(chunks_data)} chunks for subject_id='{subject_id}' from {file_path}")
    return True


class UploadPDFView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        pdf = request.FILES.get("pdf")
        subject_id = request.data.get("subject_id")

        if not pdf or not subject_id:
            return Response({"error": "PDF and subject_id required"}, status=400)

        try:
            # Save the PDF to disk so it survives server restarts
            upload_dir = os.path.join("media", "rag_uploads")
            os.makedirs(upload_dir, exist_ok=True)
            
            file_name = f"{subject_id}_{pdf.name}"
            file_path = os.path.join(upload_dir, file_name)
            
            with open(file_path, "wb") as f:
                for chunk in pdf.chunks():
                    f.write(chunk)
            
            # Register this file for this subject_id
            UPLOAD_REGISTRY[subject_id] = file_path
            
            # Index it
            success = _index_pdf_file(file_path, subject_id)
            
            if not success:
                return Response({"error": "Could not extract text from PDF"}, status=400)
                
            return Response({"message": "Document processed and ready for chat."})
        except Exception as e:
            print(f"[RAG] Upload error: {e}")
            return Response({"error": str(e)}, status=500)


class ChatView(APIView):
    def post(self, request):
        subject_id = str(request.data.get("subject_id"))
        question = request.data.get("question")

        if not question or not subject_id:
            return Response({"error": "subject_id and question required"}, status=400)

        print(f"[RAG] Chat request: subject_id='{subject_id}', question='{question[:50]}'")
        print(f"[RAG] VECTOR_STORE keys: {list(VECTOR_STORE.keys())}")

        subject_data = VECTOR_STORE.get(subject_id)
        
        # If not in memory, try to re-index from saved upload file
        if not subject_data:
            saved_path = UPLOAD_REGISTRY.get(subject_id)
            if not saved_path:
                # Check if there's a file on disk for this subject_id
                upload_dir = os.path.join("media", "rag_uploads")
                if os.path.exists(upload_dir):
                    for fname in os.listdir(upload_dir):
                        if fname.startswith(subject_id):
                            saved_path = os.path.join(upload_dir, fname)
                            UPLOAD_REGISTRY[subject_id] = saved_path
                            break
            
            if saved_path and os.path.exists(saved_path):
                print(f"[RAG] Re-indexing from saved file: {saved_path}")
                _index_pdf_file(saved_path, subject_id)
                subject_data = VECTOR_STORE.get(subject_id)
        
        # If still not found, try official Resource PDFs
        if not subject_data:
            try:
                docs = Resource.objects.filter(subject_id=subject_id, file_type='PDF', status='APPROVED')
                if docs.exists():
                    combined_text = ""
                    for doc in docs:
                        try:
                            if doc.file:
                                combined_text += extract_text_from_pdf(doc.file.path) + "\n"
                        except Exception as e:
                            print(f"[RAG] Error reading {doc.file.path}: {e}")
                    
                    if combined_text.strip():
                        chunks = chunk_text(combined_text)
                        index, chunks_data = create_faiss_index(chunks)
                        VECTOR_STORE[subject_id] = {
                            "index": index,
                            "chunks": chunks_data
                        }
                        subject_data = VECTOR_STORE[subject_id]
                        print(f"[RAG] Indexed {len(chunks_data)} chunks from Resource DB")
            except Exception as e:
                print(f"[RAG] Resource lookup error: {e}")
        
        if not subject_data:
            return Response({"answer": "No documents found. Please upload a PDF first using the Upload Document button."})

        index = subject_data["index"]
        chunks_data = subject_data["chunks"]

        # Retrieve top 4 relevant chunks
        relevant_chunks = search_chunks(question, index, chunks_data, top_k=4)
        if not relevant_chunks:
            return Response({"answer": "No relevant content found in PDF notes."})

        context = "\n".join(relevant_chunks)
        print(f"[RAG] Context length: {len(context)} chars")
        print(f"[RAG] Context preview: {context[:150]}...")
        
        answer = ask_llm(context, question)

        return Response({"answer": answer})

class GenAIView(APIView):
    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "question required"}, status=400)
        
        answer = ask_llm("", question)
        return Response({"answer": answer})


# ─── Anonymous Teacher-Student Chat ──────────────────────────
from .models import AnonChatRoom, AnonMessage
from Academic.models import Subject


class AnonChatRoomListView(APIView):
    """List chat rooms available to the user."""
    def get(self, request):
        user = request.user
        if user.role in ['faculty', 'admin']:
            subjects = Subject.objects.filter(faculty=user)
        elif user.role == 'student':
            if user.sem:
                subjects = Subject.objects.filter(sem__sem_nmbr=user.sem)
            else:
                return Response([])
        else:
            return Response([])

        rooms = []
        for sub in subjects:
            room, _ = AnonChatRoom.objects.get_or_create(subject=sub)
            last_msg = room.messages.last()
            rooms.append({
                "id": room.id,
                "subject_id": sub.id,
                "subject_name": sub.sub_name,
                "subject_code": sub.sub_code,
                "last_message": last_msg.content[:60] if last_msg else "No messages yet",
                "last_time": last_msg.created_at.isoformat() if last_msg else None,
                "message_count": room.messages.count(),
            })
        return Response(rooms)


class AnonChatMessageView(APIView):
    """Get messages in a room, or post a new message."""
    def get(self, request, room_id):
        try:
            room = AnonChatRoom.objects.get(id=room_id)
        except AnonChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        messages = room.messages.all().order_by('created_at')
        data = []
        for msg in messages:
            data.append({
                "id": msg.id,
                "sender_alias": msg.anon_alias,
                "content": msg.content,
                "is_faculty": msg.sender.role in ['faculty', 'admin'],
                "is_me": msg.sender == request.user,
                "created_at": msg.created_at.isoformat(),
            })
        return Response(data)

    def post(self, request, room_id):
        try:
            room = AnonChatRoom.objects.get(id=room_id)
        except AnonChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        content = request.data.get("content", "").strip()
        if not content:
            return Response({"error": "Message content required"}, status=400)

        msg = AnonMessage.objects.create(
            room=room,
            sender=request.user,
            content=content
        )
        return Response({
            "id": msg.id,
            "sender_alias": msg.anon_alias,
            "content": msg.content,
            "is_faculty": msg.sender.role in ['faculty', 'admin'],
            "is_me": True,
            "created_at": msg.created_at.isoformat(),
        }, status=201)
