# ── Models ─────────────────────────────────────────────────
MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]
DEFAULT_MODEL       = "llama-3.1-8b-instant"
DEFAULT_TEMPERATURE = 0.7

# ── RAG settings ───────────────────────────────────────────
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 50
TOP_K         = 6
INDEX_NAME    = "pdf-rag-index"
EMBEDDING_DIM = 384
HF_API_URL    = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"

# ── Supported file types ───────────────────────────────────
SUPPORTED_TYPES = ["pdf", "docx", "txt"]

# ── System prompts ─────────────────────────────────────────
SYSTEM_PROMPT = """You are Aria, a friendly and helpful customer support assistant.
You help customers with their queries clearly and concisely."""

RAG_SYSTEM_PROMPT = """You are Aria, a helpful assistant. Answer the user's question
using ONLY the context provided. Each context chunk is labeled with its source document.
If the answer isn't in the context, say so honestly.
When relevant, mention which document the information came from."""

# ── Welcome screen suggestions ─────────────────────────────
SUGGESTIONS = [
    ("📄", "Summarise a document", "Upload a file and ask questions"),
    ("✍️", "Review my resume",     "Get feedback and suggestions"),
    ("💡", "Explain a concept",    "Break down complex topics"),
    ("💻", "Help with code",       "Debug or explain code"),
]

# ── Author ─────────────────────────────────────────────────
AUTHOR_NAME    = "Prathyush Maniyam"
AUTHOR_GITHUB  = "https://github.com/pratzzeee"
AUTHOR_LINKEDIN = "https://linkedin.com/in/prathyushmaniyam"