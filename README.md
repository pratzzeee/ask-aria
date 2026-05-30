# 🤖 ask-aria — Conversational AI Chatbot

A production-grade AI chatbot with multi-document RAG, hybrid search, streaming responses, MLOps evaluation pipeline, and support for PDF, DOCX, and TXT files. Built with LLaMA 3 via Groq and deployed on Streamlit Cloud.

🔗 **Live Demo:** [Click here](https://portfoliochatbot-7qfqqmjdqdxepxv3c9zdpe.streamlit.app/)

---

## 📌 Project Overview

ask-aria is an AI-powered customer support assistant that can hold multi-turn conversations, remember context within a session, and respond in a friendly, helpful tone.

This project was built as part of a portfolio to demonstrate end-to-end ML application development — from local development to cloud deployment — including RAG pipelines, hybrid vector search, production-safe dependency management, a full evaluation framework, and an MLOps pipeline to systematically measure and improve system performance.

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| LLM | LLaMA 3.1 (8B) / LLaMA 3.3 (70B) via Groq API |
| UI | Streamlit |
| Hosting | Streamlit Cloud (free tier) |
| Language | Python 3.9 |
| Embeddings | HuggingFace Inference API (all-MiniLM-L6-v2) |
| Vector DB | Pinecone (serverless, dotproduct metric) |
| Hybrid Search | BM25 sparse vectors via pinecone-text |
| PDF Parsing | pypdf |
| DOCX Parsing | python-docx |
| TXT Parsing | Python built-in |
| Charts | Plotly |

---

## ✨ Features

### 💬 Normal Chat
- Multi-turn conversation with session memory
- Model selector — switch between LLaMA 3.1 8B and 3.3 70B
- Temperature control for response creativity
- Streaming responses (token-by-token like ChatGPT)
- Clear conversation button

### 📁 Document Chat (RAG + Hybrid Search)
- Upload multiple files simultaneously (PDF, DOCX, TXT)
- **Hybrid search** — combines dense vector embeddings + BM25 sparse vectors
- Retrieves exact numbers, names and technical terms (BM25) AND semantic meaning (dense)
- Free embeddings via HuggingFace Inference API — no OpenAI key needed
- Answers grounded strictly in document context
- Source attribution — Aria tells you which document the answer came from
- Clear documents button with full Pinecone index reset
- Streaming responses for document chat too

### 📊 RAG Evaluation Dashboard
- Latency profiling — breakdown per pipeline step (embedding, Pinecone, LLM)
- Retrieval quality — keyword hit rate % per question
- LLM-as-judge — faithfulness, relevance, completeness scored 1–10
- 10 golden Q&A pairs across 5 categories (factual, numerical, technical, out-of-scope, summarisation)
- Interactive Plotly charts for non-technical stakeholders
- Run via: `streamlit run eval_dashboard.py`

### 🔬 MLOps Evaluation Pipeline
- Save any eval run as baseline for future comparisons
- Log named experiments with config and description
- Side-by-side vs Baseline comparison with green/red deltas
- Experiment tracker stores all runs in JSON for full history
- Run via: `streamlit run eval_dashboard.py`

---

## 📈 Performance Results

### Hybrid Search vs Baseline

| Metric | Baseline (dense only) | Hybrid (BM25 + dense) | Delta |
|---|---|---|---|
| Retrieval Hit % | 55.8% | 70.0% | +14.2% ✅ |
| Faithfulness | 8.1/10 | 8.6/10 | +0.5 ✅ |
| Completeness | 7.5/10 | 8.0/10 | +0.5 ✅ |
| Overall Score | 8.4/10 | 8.6/10 | +0.2 ✅ |
| Latency | 1.39s | 1.64s | +0.25s ➡️ |

### MLOps Experiments

| Experiment | CHUNK_SIZE | TOP_K | Retrieval | Overall | Verdict |
|---|---|---|---|---|---|
| Baseline | 500 | 6 | 55.8% | 8.4/10 | ✅ Optimal for 8B |
| chunk_size_800 | 800 | 6 | 66.7% | 7.4/10 | ❌ LLM confused |
| chunk_size_650 | 650 | 6 | 56.7% | 8.4/10 | ➡️ No gain |
| top_k_10 | 500 | 10 | 67.6% | 7.1/10 | ❌ Too much context |
| hybrid_search | 500 | 6 | 70.0% | 8.6/10 | ✅ Best overall |

---

## 🚀 Run Locally

1. Clone the repository
```bash
git clone https://github.com/pratzzeee/ask-aria.git
cd ask-aria
```

2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys
```bash
cp .env.example .env
# Edit .env and add your keys
```

5. Run the main app
```bash
streamlit run app.py
```

6. Run the evaluation dashboard (optional)
```bash
streamlit run eval_dashboard.py
```

---

## 🔑 Environment Variables

```
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
HF_API_TOKEN=your_huggingface_token
```

> Get your keys:
> - Groq: [console.groq.com](https://console.groq.com)
> - Pinecone: [app.pinecone.io](https://app.pinecone.io)
> - HuggingFace: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) — enable "Make calls to Inference Providers"

---

## 📁 Project Structure

```
ask-aria/
├── app.py                  # Streamlit UI — chat interface
├── rag.py                  # RAG engine (extract, chunk, embed, hybrid query, clear)
├── config.py               # Models, prompts, constants, author info
├── styles.py               # All CSS and HTML string templates
├── utils.py                # Helper functions (file handling, message building)
├── eval.py                 # Evaluation engine (latency, retrieval, LLM-judge)
├── eval_dashboard.py       # Streamlit evaluation + MLOps dashboard
├── eval_data/
│   └── test_qa.json        # 10 golden Q&A pairs for evaluation
├── mlops/
│   ├── __init__.py
│   ├── experiment_tracker.py  # Save/load/compare experiments
│   ├── baseline.json          # Saved baseline metrics
│   ├── experiments.json       # All experiment results
│   └── bm25_encoder.json      # Fitted BM25 model per document set
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
├── requirements.txt        # Minimal clean dependencies
├── CHANGELOG.md            # Full version history
├── .env                    # API keys (not committed)
├── .env.example            # Documents required API keys
├── .gitignore              # Ignores venv, .env, __pycache__
└── README.md               # This file
```

---

## 🔮 Roadmap

| Version | Feature | Status |
|---------|---------|--------|
| v1.0.0 | Core chatbot via Groq + LLaMA 3 | ✅ Complete |
| v2.1.0 | RAG PDF Chat with Pinecone | ✅ Complete |
| v3.0.0 | Streaming responses | ✅ Complete |
| v4.0.0 | Multi-document chat (PDF/DOCX/TXT) | ✅ Complete |
| v5.0.0 | UI upgrade + code refactor | ✅ Complete |
| v6.0.0 | RAG evaluation dashboard | ✅ Complete |
| v7.0.0 | MLOps evaluation pipeline | ✅ Complete |
| v8.0.0 | Hybrid search (BM25 + dense vectors) | ✅ Complete |
| v9.0.0 | Usage analytics tracker | 🔲 Planned |
| v9.1.0 | Semantic chunking strategy | 🔲 Planned |

---

## 🧠 Key Engineering Decisions

| Decision | Reason |
|----------|--------|
| No LangChain | Python 3.14 conflicts on Streamlit Cloud |
| HF Inference API over sentence-transformers | No torch dependency — works on any Python version |
| Pinecone serverless | Free tier, no infrastructure to manage |
| Groq over OpenAI | Free tier, fastest LLaMA inference available |
| Hand-written requirements.txt | pip freeze includes macOS-local paths that break Linux deploys |
| Modular file structure | config/styles/utils split for scalability and maintainability |
| Evaluation framework | Data-driven improvements — measure before optimising |
| MLOps pipeline | Systematic experimentation with baseline comparison |
| Hybrid search over pure vector | BM25 fixes exact term retrieval — improved hit rate from 55.8% to 70% |
| dotproduct metric in Pinecone | Required for hybrid dense+sparse vector search |

---

## 👤 Author

**Prathyush Maniyam**
[GitHub](https://github.com/pratzzeee) · [LinkedIn](https://linkedin.com/in/prathyushmaniyam)