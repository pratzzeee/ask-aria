# Changelog

All notable changes to Aria — AI Customer Support Chatbot are documented here.

---

## [v8.0.0] - 2026-05-29 — Feature 7: Hybrid Search (BM25 + Dense Vectors)

### Added
- `pinecone-text` library for BM25 sparse vector encoding
- `BM25Encoder` fitted on document corpus at upload time
- `mlops/bm25_encoder.json` — persisted BM25 model per document set
- Hybrid query in `query_rag()` — combines dense + sparse vectors with `alpha` parameter:
  - `alpha=0` → pure keyword (BM25)
  - `alpha=1` → pure semantic (dense)
  - `alpha=0.5` → balanced (default)

### Changed
- Pinecone index metric changed from `cosine` → `dotproduct` (required for hybrid)
- `process_file()` now upserts both `values` (dense) and `sparse_values` (BM25) per chunk
- `clear_index()` also deletes BM25 encoder so it refits on next upload
- Updated `eval_data/test_qa.json` to match updated resume content

### Results vs Baseline

| Metric | Baseline | Hybrid (α=0.5) | Delta |
|---|---|---|---|
| Retrieval Hit % | 55.8% | 70.0% | +14.2% ✅ |
| Faithfulness | 8.1/10 | 8.6/10 | +0.5 ✅ |
| Relevance | 9.7/10 | 9.1/10 | -0.6 ⚠️ |
| Completeness | 7.5/10 | 8.0/10 | +0.5 ✅ |
| Overall | 8.4/10 | 8.6/10 | +0.2 ✅ |
| Latency | 1.39s | 1.64s | +0.25s ➡️ |

### Key Finding
- Hybrid search fixes the exact term retrieval weakness — numerical questions (52%, 16%, 25%) now retrieved correctly
- BM25 excels at exact numbers and technical terms; dense vectors handle semantic questions
- Combined approach improves both retrieval quality and overall LLM score

### Tech Stack Addition
- `pinecone-text` for BM25 sparse vector generation

---

## [v7.0.0] - 2026-05-26 — Feature 6: MLOps Evaluation Pipeline

### Added
- `mlops/experiment_tracker.py` — core MLOps engine:
  - `save_baseline()` — saves current eval as ground truth
  - `save_experiment()` — logs named experiments with config
  - `load_baseline()` / `load_experiments()` — retrieval functions
  - `compute_summary()` — aggregates metrics across all questions
  - `compare_to_baseline()` — computes deltas per metric
  - `get_best_experiment()` — finds highest scoring config
- `mlops/baseline.json` — saved baseline metrics
- `mlops/experiments.json` — all experiment results logged
- Updated `eval_dashboard.py`:
  - Session state for results (survives button clicks)
  - **Save as Baseline** button
  - **Save as Experiment** button with name + description
  - **vs Baseline** comparison row with green/red deltas
  - Baseline status shown in sidebar with key metrics

### Experiments Run

| Experiment | CHUNK_SIZE | TOP_K | Retrieval | Overall |
|---|---|---|---|---|
| Baseline | 500 | 6 | 55.8% | 8.4/10 |
| chunk_size_800 | 800 | 6 | 66.7% | 7.4/10 |
| chunk_size_650 | 650 | 6 | 56.7% | 8.4/10 |
| top_k_10 | 500 | 10 | 67.6% | 7.1/10 |

### Key Finding
- Baseline config (CHUNK_SIZE=500, TOP_K=6) is optimal for `llama-3.1-8b-instant`
- Consistent trade-off: more context = +12% retrieval but -1.3 overall LLM quality
- Root cause: 8B model capacity — larger context confuses smaller models

---

## [v6.0.0] - 2026-05-21 — Feature 5: RAG Evaluation Dashboard

### Added
- `eval.py` — 3 evaluation methods:
  - Latency profiling (embedding, Pinecone, LLM breakdown)
  - Retrieval quality (keyword hit rate %)
  - LLM-as-judge (faithfulness, relevance, completeness scored 1-10)
- `eval_dashboard.py` — standalone Streamlit evaluation UI
  - Summary metric cards
  - Interactive latency stacked bar chart
  - Retrieval hit rate bar chart by category
  - LLM judge line chart across all questions
  - Detailed expandable results per question
- `eval_data/test_qa.json` — 10 golden Q&A pairs across 5 categories:
  - factual, numerical, technical, out_of_scope, summarisation

### Evaluation Results (on Prathyush Maniyam resume)
- Avg Latency: 3.68s (embedding is main bottleneck)
- Retrieval Hit Rate: 55.8%
- Faithfulness: 8.1/10
- Relevance: 9.5/10

### Tech Stack Addition
- `plotly` for interactive charts

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
- Cleaned `requirements.txt` of macOS-local `.whl` paths

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
| v6.0.0 | RAG evaluation dashboard | ✅ Complete |
| v7.0.0 | MLOps evaluation pipeline | ✅ Complete |
| v8.0.0 | Hybrid search (BM25 + dense vectors) | ✅ Complete |
| v9.0.0 | Usage analytics tracker | 🔲 Planned |
| v9.1.0 | Semantic chunking strategy | 🔲 Planned |