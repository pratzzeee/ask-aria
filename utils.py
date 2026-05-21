import tempfile
import streamlit as st
from rag import process_files, clear_index    # ← add clear_index here


def save_uploaded_files(uploaded_files) -> list[tuple[str, str]]:
    file_paths = []
    for f in uploaded_files:
        ext = f.name.rsplit(".", 1)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(f.read())
            tmp.flush()
            file_paths.append((tmp.name, f.name))
    return file_paths


def handle_file_upload(uploaded_files) -> bool:
    with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
        try:
            clear_index()                          # ← wipe old vectors first
            file_paths = save_uploaded_files(uploaded_files)
            results    = process_files(file_paths)
            for filename, count in results.items():
                st.success(f"✅ {filename}: {count} chunks")
            return True
        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
            st.stop()


def build_messages(
    mode: str,
    docs_ready: bool,
    prompt: str,
    messages: list,
    system_prompt: str,
    rag_system_prompt: str,
    context: str = ""
) -> list:
    if mode == "📁 Document Chat" and docs_ready:
        rag_system_msg = {
            "role": "system",
            "content": f"{rag_system_prompt}\n\nCONTEXT:\n{context}"
        }
        return [rag_system_msg] + messages

    elif mode == "📁 Document Chat" and not docs_ready:
        return [
            {"role": "system", "content": rag_system_prompt},
            *messages
        ]

    else:
        return [
            {"role": "system", "content": system_prompt},
            *messages
        ]