import os
import time
import requests
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
import docx

load_dotenv()

# ── Constants ──────────────────────────────────────────────
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME       = "pdf-rag-index"
CHUNK_SIZE       = 500
CHUNK_OVERLAP    = 50

# HuggingFace Inference API
HF_API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"

def get_hf_headers():
    token = os.getenv("HF_API_TOKEN")
    if not token:
        raise Exception("HF_API_TOKEN not found — check your .env file")
    return {"Authorization": f"Bearer {token}"}

# ── Embedding via HF API ───────────────────────────────────

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
            dimension=384,
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
    if ext == "pdf":
        return extract_text_from_pdf(file_path)
    elif ext == "docx":
        return extract_text_from_docx(file_path)
    elif ext == "txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")

# ── Chunking ───────────────────────────────────────────────

def chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if c.strip()]

# ── Core functions ─────────────────────────────────────────

def process_file(file_path: str, filename: str) -> int:
    """
    Full pipeline for a single file:
    extract → chunk → embed → upsert to Pinecone.
    Chunks tagged with source filename.
    """
    text   = extract_text(file_path, filename)
    chunks = chunk_text(text)

    all_vectors = []
    batch_size  = 32
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        vecs  = get_embeddings(batch)
        all_vectors.extend(vecs)

    index     = get_pinecone_index()
    safe_name = filename.replace(" ", "_").replace(".", "_")
    upsert_data = [
        (
            f"{safe_name}-chunk-{i}",
            all_vectors[i],
            {
                "text":   chunks[i],
                "source": filename
            }
        )
        for i in range(len(chunks))
    ]

    for i in range(0, len(upsert_data), 100):
        index.upsert(vectors=upsert_data[i:i+100])

    return len(chunks)

def process_files(file_paths: list[tuple[str, str]]) -> dict:
    """
    Process multiple files at once.
    file_paths: list of (tmp_path, original_filename) tuples
    Returns dict of {filename: chunk_count}
    """
    results = {}
    for file_path, filename in file_paths:
        count = process_file(file_path, filename)
        results[filename] = count
    return results

def query_rag(question: str, top_k: int = 6) -> str:
    """
    Embed question → find top_k chunks across ALL documents
    → return context string with source attribution.
    """
    question_vec = get_embedding(question)

    index   = get_pinecone_index()
    results = index.query(
        vector=question_vec,
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