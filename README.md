# 🤖 ask-aria — Conversational AI Chatbot

A production-grade AI chatbot with multi-document RAG, streaming responses, MLOps evaluation pipeline, and support for PDF, DOCX, and TXT files. Built with LLaMA 3 via Groq and deployed on Streamlit Cloud.

🔗 **Live Demo:** [Click here](https://portfoliochatbot-7qfqqmjdqdxepxv3c9zdpe.streamlit.app/)

---

## 📌 Project Overview

ask-aria is an AI-powered customer support assistant that can hold multi-turn conversations, remember context within a session, and respond in a friendly, helpful tone.

This project was built as part of a portfolio to demonstrate end-to-end ML application development — from local development to cloud deployment — including RAG pipelines, vector databases, production-safe dependency management, a full evaluation framework, and an MLOps pipeline to systematically measure and improve system performance.

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| LLM | LLaMA 3.1 (8B) / LLaMA 3.3 (70B) via Groq API |
| UI | Streamlit |
| Hosting | Streamlit Cloud (free tier) |
| Language | Python 3.9 |
| Embeddings | HuggingFace Inference API (all-MiniLM-L6-v2) |
| Vector DB | Pinecone (serverless) |
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

### 📁 Document Chat (RAG)
- Upload multiple files simultaneously (PDF, DOCX, TXT)
- Semantic search via Pinecone vector database
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
- 4 experiments run — finding: baseline config optimal for 8B model
- Run via: `streamlit run eval_dashboard.py`

---

## 🔬 MLOps Findings

| Experiment | CHUNK_SIZE | TOP_K | Retrieval | Overall | Verdict |
|---|---|---|---|---|---|
| Baseline | 500 | 6 | 55.8% | 8.4/10 | ✅ Optimal |
| chunk_size_800 | 800 | 6 | 66.7% | 7.4/10 | ❌ LLM confused |
| chunk_size_650 | 650 | 6 | 56.7% | 8.4/10 | ➡️ No gain |
| top_k_10 | 500 | 10 | 67.6% | 7.1/10 | ❌ Too much context |

**Key insight:** More context improves retrieval (+12%) but hurts 8B LLM quality (-1.3 pts). Baseline config is optimal for `llama-3.1-8b-instant`.

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
├── rag.py                  # RAG engine (extract, chunk, embed, query, clear)
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
│   └── experiments.json       # All experiment results
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
| v8.0.0 | Semantic chunking strategy | 🔲 Planned |
| v8.1.0 | Usage analytics tracker | 🔲 Planned |

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

---

## 👤 Author

**Prathyush Maniyam**
[GitHub](https://github.com/pratzzeee) · [LinkedIn](https://linkedin.com/in/prathyushmaniyam)
