# Changelog

All notable changes to Aria — AI Customer Support Chatbot are documented here.

---

## [v5.0.0] - 2026-05-21 — Feature 4: UI Upgrade + Code Refactor

### Added
- Apple-inspired UI with clean typography and generous spacing
- Welcome screen with 4 suggestion cards on empty chat
- Footer with author name and links
- Clear documents button with full UI and Pinecone reset
- `uploader_key` trick to reset Streamlit file uploader UI
- `.streamlit/config.toml` for consistent base theme

### Changed
- Refactored monolithic `app.py` into:
  - `config.py` — models, prompts, constants, author info
  - `styles.py` — all CSS and HTML string templates
  - `utils.py` — helper functions (file handling, message building)
- Bigger fonts across all components (13px → 15–16px)
- Header changed to "How can I help you?" with larger icon
- `app.py` reduced to UI-only logic (~90 lines)

### Fixed
- Pinecone namespace error on `clear_index()` (added `namespace=""`)
- File uploader not resetting visually after clear documents
- Old vectors from previous sessions mixing with new uploads

---

## [v4.0.0] - 2026-05-20 — Feature 3: Multi-Document Chat

### Added
- Support for DOCX files via `python-docx`
- Support for TXT files via built-in Python
- Multiple file uploads simultaneously
- Per-file chunk count display in sidebar
- Source attribution in RAG context `[Source: filename]`
- Aria mentions which document answers came from

### Changed
- `process_pdf()` → `process_file()` supporting PDF/DOCX/TXT
- Added `process_files()` for batch processing
- Mode renamed from "PDF Chat" to "Document Chat"
- `top_k` increased from 4 to 6 for better multi-doc coverage

### Tech Stack Addition
- `python-docx` for Word document parsing

---

## [v3.0.0] - 2026-05-20 — Feature 2: Streaming Responses

### Added
- Token-by-token streaming via Groq `stream=True`
- `st.write_stream()` for live rendering in Streamlit
- Spinner scoped to RAG document search only

### Changed
- Removed full-response blocking spinner
- Response now appears progressively like ChatGPT

---

## [v2.1.0] - 2026-05-19 — Feature 1: RAG PDF Chat

### Added
- PDF upload via Streamlit sidebar
- Text extraction using `pypdf` directly (no LangChain)
- Chunking with configurable size (500) and overlap (50)
- Embeddings via HuggingFace Inference API (`all-MiniLM-L6-v2`, 384-dim)
- Vector storage and semantic search via Pinecone serverless
- PDF Chat mode toggle alongside existing Normal Chat
- Context injection into LLaMA prompt as system message
- Error handling for PDF processing shown in UI

### Fixed
- Removed LangChain entirely (Python 3.14 compatibility on Streamlit Cloud)
- Replaced `sentence-transformers` + `torch` with HF Inference API (no heavy ML deps)
- Fixed HuggingFace router URL migration (`api-inference` → `router.huggingface.co`)
- Fixed tempfile flush issue causing empty file reads
- Cleaned `requirements.txt` of macOS-specific local `.whl` paths

### Tech Stack Addition
- `pypdf` for PDF parsing
- `pinecone` for vector database
- `requests` for HF Inference API calls

---

## [v1.0.0] - 2026-05-01 — Phase 1: Core Chatbot

### Added
- Streamlit chat UI with session memory
- LLaMA 3.1 8B and LLaMA 3.3 70B model selection via Groq SDK
- Temperature control slider
- Clear conversation button
- Deployed on Streamlit Cloud (free tier)

### Tech Stack
- `streamlit` for UI
- `groq` SDK for LLaMA inference
- `python-dotenv` for environment management

---

## Roadmap

| Version | Feature | Status |
|---|---|---|
| v1.0.0 | Core chatbot via Groq | ✅ Complete |
| v2.1.0 | RAG PDF Chat with Pinecone | ✅ Complete |
| v3.0.0 | Streaming responses | ✅ Complete |
| v4.0.0 | Multi-document chat (PDF/DOCX/TXT) | ✅ Complete |
| v5.0.0 | UI upgrade + code refactor | ✅ Complete |
| v6.0.0 | Performance & caching | 🔲 Planned |
| v6.1.0 | Usage analytics | 🔲 Planned |