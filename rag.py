import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

load_dotenv()

# ── Constants ──────────────────────────────────────────────
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME       = "pdf-rag-index"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"
CHUNK_SIZE       = 500
CHUNK_OVERLAP    = 50

# ── Singleton: embedding model ─────────────────────────────
_embedder = None

def get_embedder():
    """Load the embedding model once and reuse it."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder

# ── Singleton: Pinecone index ──────────────────────────────
def get_pinecone_index():
    """Connect to Pinecone, create index if it doesn't exist."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,        # all-MiniLM-L6-v2 = 384 dims
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(INDEX_NAME)

# ── PDF helpers ────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF using pypdf directly."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def chunk_text(text: str) -> list[str]:
    """
    Split text into overlapping chunks manually.
    No LangChain needed — pure Python.
    """
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
    Full pipeline: extract → chunk → embed → upsert to Pinecone.
    Returns number of chunks stored.
    """
    # 1. Extract raw text
    text = extract_text_from_pdf(file_path)

    # 2. Split into chunks
    chunks = chunk_text(text)

    # 3. Embed all chunks locally
    embedder = get_embedder()
    vectors  = embedder.encode(chunks, show_progress_bar=False).tolist()

    # 4. Upsert into Pinecone
    index = get_pinecone_index()
    upsert_data = [
        (f"chunk-{i}", vectors[i], {"text": chunks[i]})
        for i in range(len(chunks))
    ]

    # Pinecone recommends batches of 100
    batch_size = 100
    for i in range(0, len(upsert_data), batch_size):
        index.upsert(vectors=upsert_data[i:i+batch_size])

    return len(chunks)

def query_rag(question: str, top_k: int = 4) -> str:
    """
    Embed the question → find top_k similar chunks → return as context string.
    """
    embedder     = get_embedder()
    question_vec = embedder.encode(question).tolist()

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