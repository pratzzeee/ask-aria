import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.set_page_config(
    page_title="Aria - Customer Support",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Aria — Customer Support Assistant")
st.caption("Powered by LLaMA 3 via Groq")

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

SYSTEM_PROMPT = """You are Aria, a friendly and helpful customer support assistant. 
You help customers with their queries clearly and concisely."""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Aria anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Aria is thinking..."):
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *st.session_state.messages
                ]
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

if st.sidebar.button("🗑️ Clear conversation"):
    st.session_state.messages = []
    st.rerun()