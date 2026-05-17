import os
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
st.set_page_config(
    page_title="Aria - Customer Support",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Aria — Customer Support Assistant")
st.caption("Powered by LLaMA 3 via Groq · Built with LangChain & Streamlit")

with st.sidebar:
    st.header("Settings")
    model = st.selectbox(
    "Choose model",
    ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
    index=0
   )
    temperature = st.slider(
        "Temperature", #this is the creativity of the model, higher = more creative, lower = more focused. try to change and see how the responses change!
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative. Lower = more focused."
    )
    st.divider()
    st.markdown("**Tech stack**")
    st.markdown("- LLM: LLaMA 3 via Groq")
    st.markdown("- Framework: LangChain")
    st.markdown("- UI: Streamlit")
    st.markdown("- Hosting: Streamlit Cloud")

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        return_messages=True
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name=model,
    temperature=temperature,
    streaming=True
)

conversation = ConversationChain(
    llm=llm,
    memory=st.session_state.memory,
    verbose=False
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Aria anything..."):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Aria is thinking..."):
            response = conversation.predict(input=prompt)
            st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

if st.sidebar.button("🗑️ Clear conversation"):
    st.session_state.messages = []
    st.session_state.memory.clear()
    st.rerun()