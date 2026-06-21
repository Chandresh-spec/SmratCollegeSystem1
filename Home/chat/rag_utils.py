import os
import requests
import numpy as np
from pypdf import PdfReader


# ── Hugging Face Inference API for embeddings ────────────────────
HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


def _hf_embed(texts):
    """
    Get embeddings from Hugging Face Inference API.
    Uses the same all-MiniLM-L6-v2 model, but running on HF servers
    instead of locally — no PyTorch / sentence-transformers needed.
    """
    api_key = os.environ.get("HUGGINGFACE_API_KEY", "")
    headers = {}
    if api_key and api_key != "your_huggingface_key_here":
        headers["Authorization"] = f"Bearer {api_key}"

    # HF Inference API accepts a list of strings and returns a list of embeddings
    payload = {"inputs": texts, "options": {"wait_for_model": True}}
    resp = requests.post(HF_API_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return np.array(resp.json(), dtype="float32")


# ── PDF / text utilities ─────────────────────────────────────────

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# ── Vector index (numpy cosine similarity, replaces FAISS) ───────

def _cosine_similarity(a, b):
    """Cosine similarity between matrix a and vector b."""
    # a: (N, D)  b: (1, D)
    dot = np.dot(a, b.T).squeeze()
    norm_a = np.linalg.norm(a, axis=1)
    norm_b = np.linalg.norm(b)
    return dot / (norm_a * norm_b + 1e-10)


def create_faiss_index(chunks):
    """
    Same signature as before so views.py needs zero changes.
    Returns (embeddings_matrix, chunks_list).
    """
    # Batch in groups of 64 to stay within API payload limits
    all_embeddings = []
    for i in range(0, len(chunks), 64):
        batch = chunks[i : i + 64]
        emb = _hf_embed(batch)
        all_embeddings.append(emb)
    embeddings = np.vstack(all_embeddings)
    return embeddings, chunks


def search_chunks(query, index, chunks, top_k=5):
    """
    Same signature as before.
    `index` is now a numpy embeddings matrix instead of a FAISS index.
    """
    query_embedding = _hf_embed([query])
    scores = _cosine_similarity(index, query_embedding)
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [chunks[i] for i in top_indices]
