# 🤖 Aria — Conversational AI Chatbot

A production-grade AI chatbot with multi-document RAG, streaming responses, evaluation dashboard, and support for PDF, DOCX, and TXT files. Built with LLaMA 3 via Groq and deployed on Streamlit Cloud.

🔗 **Live Demo:** [Click here](https://portfoliochatbot-7qfqqmjdqdxepxv3c9zdpe.streamlit.app/)

---

## 📌 Project Overview

Aria is an AI-powered customer support assistant that can hold multi-turn conversations, remember context within a session, and respond in a friendly, helpful tone.

This project was built as part of a portfolio to demonstrate end-to-end ML application development — from local development to cloud deployment — including RAG pipelines, vector databases, production-safe dependency management, and a full evaluation framework to measure system performance.

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

---

## 🚀 Run Locally

1. Clone the repository
```bash
git clone https://github.com/pratzzeee/portfolio_chatbot.git
cd portfolio_chatbot
```

2. Create and activate a virtual environment
```bash
python3.9 -m venv venv
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
portfolio_chatbot/
├── app.py                  # Streamlit UI — chat interface
├── rag.py                  # RAG engine (extract, chunk, embed, query, clear)
├── config.py               # Models, prompts, constants, author info
├── styles.py               # All CSS and HTML string templates
├── utils.py                # Helper functions (file handling, message building)
├── eval.py                 # Evaluation engine (latency, retrieval, LLM-judge)
├── eval_dashboard.py       # Streamlit evaluation dashboard
├── eval_data/
│   └── test_qa.json        # 10 golden Q&A pairs for evaluation
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
| v7.0.0 | Performance & caching improvements | 🔲 Planned |
| v7.1.0 | Add more LLM models (Mixtral, Gemma) | 🔲 Planned |

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

---

## 👤 Author

**Prathyush Maniyam**
[GitHub](https://github.com/pratzzeee) · [LinkedIn](https://linkedin.com/in/prathyushmaniyam)
