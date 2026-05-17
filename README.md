# 🤖 Aria — Conversational AI Chatbot

A lightweight customer support chatbot built with LLaMA 3 and deployed on Streamlit Cloud.

🔗 **Live Demo:** [Click here](https://portfoliochatbot-7qfqqmjdqdxepxv3c9zdpe.streamlit.app/)

---

## 📌 Project Overview

Aria is an AI-powered customer support assistant that can hold multi-turn conversations, remember context within a session, and respond in a friendly, helpful tone.

This project was built as part of a portfolio to demonstrate end-to-end ML application development — from local development to cloud deployment.

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| LLM | LLaMA 3.1 (8B) via Groq API |
| UI | Streamlit |
| Hosting | Streamlit Cloud (free tier) |
| Language | Python 3.9 |
| API Client | Groq SDK |

---

## ✨ Features

- Multi-turn conversation with session memory
- Model selector — switch between LLaMA 3.1 8B and 70B
- Temperature control for response creativity
- Clear conversation button
- Fully deployed and publicly accessible

---

## 🚀 Run Locally

1. Clone the repository
```bash
   git clone https://github.com/YOUR_USERNAME/portfolio-chatbot.git
   cd portfolio-chatbot
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

4. Create a `.env` file and add your Groq API key

5. Run the app
```bash
   streamlit run app.py
```

---

## 📁 Project Structure
portfolio-chatbot/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── .env                # API key (not committed)
├── .gitignore          # Ignores venv and .env
└── README.md           # This file
---

## 🔮 Roadmap

- [ ] Add RAG — let users upload a PDF and chat with it
- [ ] Add intent recognition for customer support routing
- [ ] Connect to a knowledge base for domain-specific answers
- [ ] Deploy on custom domain

---

## 👤 Author

**Prathyush**  
[GitHub](https://github.com/pratzzeee) · [LinkedIn](https://linkedin.com/in/prathyushmaniyam)