import os
import time
import requests
import json
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from pypdf import PdfReader
import docx
from config import (
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K,
    INDEX_NAME, EMBEDDING_DIM, HF_API_URL
)

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# ── BM25 encoder path ──────────────────────────────────────
BM25_PATH = "mlops/bm25_encoder.json"

# ── HuggingFace headers ────────────────────────────────────
def get_hf_headers():
    token = os.getenv("HF_API_TOKEN")
    if not token:
        raise Exception("HF_API_TOKEN not found — check your .env file")
    return {"Authorization": f"Bearer {token}"}

# ── Embeddings ─────────────────────────────────────────────
def get_embeddings(texts):
    for attempt in range(3):
        response = requests.post(
            HF_API_URL,
            headers=get_hf_headers(),
            json={"inputs": texts, "options": {"wait_for_model": True}}
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 503:
            time.sleep(10)
        else:
            raise Exception(f"HF API error {response.status_code}: {response.text}")
    raise Exception("HF API failed after 3 attempts")

def get_embedding(text):
    return get_embeddings([text])[0]

# ── BM25 ───────────────────────────────────────────────────

def get_bm25_encoder(chunks=None):
    """
    Load BM25 encoder from disk if exists.
    If chunks provided and no encoder exists, fit and save a new one.
    """
    if os.path.exists(BM25_PATH):
        encoder = BM25Encoder()
        encoder.load(BM25_PATH)
        return encoder

    if chunks is None:
        raise Exception("No BM25 encoder found — upload a document first")

    encoder = BM25Encoder()
    encoder.fit(chunks)
    encoder.dump(BM25_PATH)
    return encoder

# ── Pinecone ───────────────────────────────────────────────

def get_pinecone_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="dotproduct",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(INDEX_NAME)

# ── Text extractors ────────────────────────────────────────

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_text(file_path, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    extractors = {
        "pdf":  extract_text_from_pdf,
        "docx": extract_text_from_docx,
        "txt":  extract_text_from_txt,
    }
    if ext not in extractors:
        raise ValueError(f"Unsupported file type: .{ext}")
    return extractors[ext](file_path)

# ── Chunking ───────────────────────────────────────────────

def chunk_text(text):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if c.strip()]

# ── Core functions ─────────────────────────────────────────

def process_file(file_path, filename):
    """
    Full pipeline: extract → chunk → embed (dense + sparse) → upsert.
    Both dense (HF) and sparse (BM25) vectors stored per chunk.
    """
    text   = extract_text(file_path, filename)
    chunks = chunk_text(text)

    # Dense embeddings
    all_dense = []
    for i in range(0, len(chunks), 32):
        all_dense.extend(get_embeddings(chunks[i:i+32]))

    # Sparse BM25 — fit on this document's chunks
    encoder    = BM25Encoder()
    encoder.fit(chunks)
    encoder.dump(BM25_PATH)
    all_sparse = encoder.encode_documents(chunks)

    # Upsert dense + sparse vectors
    index     = get_pinecone_index()
    safe_name = filename.replace(" ", "_").replace(".", "_")

    upsert_data = [
        {
            "id":     f"{safe_name}-chunk-{i}",
            "values": all_dense[i],
            "sparse_values": {
                "indices": all_sparse[i]["indices"],
                "values":  all_sparse[i]["values"]
            },
            "metadata": {
                "text":   chunks[i],
                "source": filename
            }
        }
        for i in range(len(chunks))
    ]

    for i in range(0, len(upsert_data), 100):
        index.upsert(vectors=upsert_data[i:i+100])

    return len(chunks)


def process_files(file_paths):
    return {filename: process_file(fp, filename) for fp, filename in file_paths}


def query_rag(question, top_k=TOP_K, alpha=0.5):
    """
    Hybrid search: dense (semantic) + sparse (BM25 keyword).
    alpha: 0=pure keyword, 1=pure semantic, 0.5=balanced
    """
    dense_vec = get_embedding(question)
    encoder   = get_bm25_encoder()
    sparse    = encoder.encode_queries(question)

    scaled_dense  = [v * alpha for v in dense_vec]
    scaled_sparse = {
        "indices": sparse["indices"],
        "values":  [v * (1 - alpha) for v in sparse["values"]]
    }

    index   = get_pinecone_index()
    results = index.query(
        vector=scaled_dense,
        sparse_vector=scaled_sparse,
        top_k=top_k,
        include_metadata=True
    )

    context_parts = []
    for match in results.matches:
        if match.metadata.get("text"):
            source = match.metadata.get("source", "Unknown")
            text   = match.metadata["text"]
            context_parts.append(f"[Source: {source}]\n{text}")

    return "\n\n---\n\n".join(context_parts)


def clear_index():
    """Delete all vectors and BM25 encoder."""
    try:
        index = get_pinecone_index()
        index.delete(delete_all=True, namespace="")
    except Exception:
        pass  # Index may be empty — that's fine

    if os.path.exists(BM25_PATH):
        os.remove(BM25_PATH)