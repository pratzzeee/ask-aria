import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from rag import process_files, query_rag
import tempfile

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.set_page_config(
    page_title="Aria - Customer Support",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Aria — Customer Support Assistant")

# ── Mode selector ──────────────────────────────────────────
mode = st.radio(
    "Chat mode",
    ["💬 Normal Chat", "📄 Document Chat"],
    horizontal=True
)
st.caption("Powered by LLaMA 3 via Groq")

# ── Sidebar: Settings ──────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    model = st.selectbox(
        "Choose model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
        index=0
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    st.divider()
    st.markdown("**Tech stack**")
    st.markdown("- LLM: LLaMA 3 via Groq")
    st.markdown("- UI: Streamlit")
    st.markdown("- Hosting: Streamlit Cloud")
    st.divider()

    # ── Document Upload ────────────────────────────────────
    docs_ready = False

    if mode == "📄 Document Chat":
        st.header("📁 Upload Documents")
        st.caption("Supports PDF, DOCX, TXT — multiple files allowed")

        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True    # ← key change
        )

        if uploaded_files:
            with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
                try:
                    # Save all files to temp paths
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=f".{ext}"
                        ) as tmp:
                            tmp.write(uploaded_file.read())
                            tmp.flush()
                            file_paths.append((tmp.name, uploaded_file.name))

                    # Process all files
                    results = process_files(file_paths)
                    docs_ready = True

                    # Show per-file chunk counts
                    for filename, count in results.items():
                        st.success(f"✅ {filename}: {count} chunks")

                except Exception as e:
                    st.error(f"Processing failed: {str(e)}")
                    st.stop()

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ── System prompts ─────────────────────────────────────────
SYSTEM_PROMPT = """You are Aria, a friendly and helpful customer support assistant. 
You help customers with their queries clearly and concisely."""

RAG_SYSTEM_PROMPT = """You are Aria, a helpful assistant. Answer the user's question 
using ONLY the context provided. Each context chunk is labeled with its source document.
If the answer isn't in the context, say so honestly.
When relevant, mention which document the information came from."""

# ── Chat history init ──────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render existing messages ───────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat input ─────────────────────────────────────────────
if prompt := st.chat_input("Ask Aria anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        # ── Build messages list for Groq ───────────────────
        if mode == "📄 Document Chat" and docs_ready:
            with st.spinner("Searching documents..."):
                context = query_rag(prompt)
            rag_system_msg = {
                "role": "system",
                "content": f"{RAG_SYSTEM_PROMPT}\n\nCONTEXT:\n{context}"
            }
            messages_to_send = [rag_system_msg] + st.session_state.messages

        elif mode == "📄 Document Chat" and not docs_ready:
            messages_to_send = [
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                *st.session_state.messages
            ]

        else:
            messages_to_send = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *st.session_state.messages
            ]

        # ── Stream the response ─────────────────────────────
        stream = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages_to_send,
            stream=True
        )

        reply = st.write_stream(
            chunk.choices[0].delta.content or ""
            for chunk in stream
            if chunk.choices[0].delta.content
        )

    st.session_state.messages.append({"role": "assistant", "content": reply})