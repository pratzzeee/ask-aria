import os
import time
import requests
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader

load_dotenv()

# ── Constants ──────────────────────────────────────────────
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
HF_API_TOKEN     = os.getenv("HF_API_TOKEN")
INDEX_NAME       = "pdf-rag-index"
CHUNK_SIZE       = 500
CHUNK_OVERLAP    = 50

# HuggingFace Inference API — free, no torch needed
HF_API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# ── Embedding via HF API ───────────────────────────────────

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Call HuggingFace Inference API to embed a list of texts.
    Returns a list of 384-dim float vectors.
    """
    # HF API can be cold — retry up to 3 times
    for attempt in range(3):
        response = requests.post(
            HF_API_URL,
            headers=HF_HEADERS,
            json={"inputs": texts, "options": {"wait_for_model": True}}
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 503:
            # Model is loading — wait and retry
            time.sleep(10)
        else:
            raise Exception(f"HF API error {response.status_code}: {response.text}")

    raise Exception("HF API failed after 3 attempts — model may be unavailable")

def get_embedding(text: str) -> list[float]:
    """Embed a single string."""
    return get_embeddings([text])[0]

# ── Pinecone ───────────────────────────────────────────────

def get_pinecone_index():
    """Connect to Pinecone, create index if it doesn't exist."""
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

# ── PDF helpers ────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF using pypdf."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if c.strip()]

# ── Core functions ─────────────────────────────────────────

def process_pdf(file_path: str) -> int:
    """
    Full pipeline: extract → chunk → embed via HF API → upsert to Pinecone.
    Returns number of chunks stored.
    """
    text   = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)

    # Embed in batches of 32 (HF API limit)
    all_vectors = []
    batch_size  = 32
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        vecs  = get_embeddings(batch)
        all_vectors.extend(vecs)

    # Upsert to Pinecone in batches of 100
    index = get_pinecone_index()
    upsert_data = [
        (f"chunk-{i}", all_vectors[i], {"text": chunks[i]})
        for i in range(len(chunks))
    ]
    for i in range(0, len(upsert_data), 100):
        index.upsert(vectors=upsert_data[i:i+100])

    return len(chunks)

def query_rag(question: str, top_k: int = 4) -> str:
    """
    Embed question via HF API → find top_k chunks → return context string.
    """
    question_vec = get_embedding(question)

    index   = get_pinecone_index()
    results = index.query(
        vector=question_vec,
        top_k=top_k,
        include_metadata=True
    )

    context_chunks = [
        match.metadata["text"]
        for match in results.matches
        if match.metadata.get("text")
    ]

    return "\n\n---\n\n".join(context_chunks)