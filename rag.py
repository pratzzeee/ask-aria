import os
import time
import requests
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
import docx
from config import (
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K,
    INDEX_NAME, EMBEDDING_DIM, HF_API_URL
)

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


def get_hf_headers():
    token = os.getenv("HF_API_TOKEN")
    if not token:
        raise Exception("HF_API_TOKEN not found — check your .env file")
    return {"Authorization": f"Bearer {token}"}


# ── Embeddings ─────────────────────────────────────────────

def get_embeddings(texts: list[str]) -> list[list[float]]:
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


def get_embedding(text: str) -> list[float]:
    return get_embeddings([text])[0]


# ── Pinecone ───────────────────────────────────────────────

def get_pinecone_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(INDEX_NAME)


# ── Text extractors ────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text(file_path: str, filename: str) -> str:
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

def chunk_text(text: str) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if c.strip()]


# ── Core functions ─────────────────────────────────────────

def process_file(file_path: str, filename: str) -> int:
    text   = extract_text(file_path, filename)
    chunks = chunk_text(text)

    all_vectors = []
    for i in range(0, len(chunks), 32):
        all_vectors.extend(get_embeddings(chunks[i:i+32]))

    index     = get_pinecone_index()
    safe_name = filename.replace(" ", "_").replace(".", "_")
    upsert_data = [
        (f"{safe_name}-chunk-{i}", all_vectors[i], {"text": chunks[i], "source": filename})
        for i in range(len(chunks))
    ]
    for i in range(0, len(upsert_data), 100):
        index.upsert(vectors=upsert_data[i:i+100])

    return len(chunks)


def process_files(file_paths: list[tuple[str, str]]) -> dict:
    return {filename: process_file(fp, filename) for fp, filename in file_paths}


def query_rag(question: str, top_k: int = TOP_K) -> str:
    results = get_pinecone_index().query(
        vector=get_embedding(question),
        top_k=top_k,
        include_metadata=True
    )
    return "\n\n---\n\n".join(
        f"[Source: {m.metadata.get('source', 'Unknown')}]\n{m.metadata['text']}"
        for m in results.matches
        if m.metadata.get("text")
    )

def clear_index():
    """Delete all vectors from the Pinecone index."""
    try:
        index = get_pinecone_index()
        index.delete(delete_all=True, namespace="")
    except Exception:
        # Index may already be empty — that's fine
        pass