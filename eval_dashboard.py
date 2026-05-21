import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from eval import run_full_evaluation, load_golden_dataset
from rag import process_file, clear_index
import tempfile

st.set_page_config(
    page_title="Aria — Eval Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Header ─────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 1rem;">
    <h1 style="font-size:28px;font-weight:600;margin:0;">📊 Aria — RAG Evaluation Dashboard</h1>
    <p style="font-size:15px;opacity:0.5;margin:6px 0 0;">
        Measure retrieval quality, answer accuracy and latency
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Setup")

    st.markdown("**Step 1: Upload your test PDF**")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        with st.spinner("Indexing PDF..."):
            try:
                clear_index()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp.flush()
                    tmp_path = tmp.name
                count = process_file(tmp_path, uploaded_file.name)
                st.success(f"✅ Indexed {count} chunks")
            except Exception as e:
                st.error(f"Failed: {str(e)}")

    st.divider()
    st.markdown("**Step 2: Run evaluation**")
    run_btn = st.button("🚀 Run Full Evaluation", use_container_width=True)

    st.divider()
    st.markdown("""
    **What this measures:**
    - ⚡ Latency per pipeline step
    - 🎯 Retrieval keyword hit rate
    - 🤖 LLM-as-judge scores
    """)

# ── Main area ──────────────────────────────────────────────
if run_btn:
    if not uploaded_file:
        st.warning("⚠️ Please upload a PDF first.")
        st.stop()

    with st.spinner("Running evaluation on 10 questions... this takes ~2 mins"):
        results = run_full_evaluation()

    st.success("✅ Evaluation complete!")
    st.divider()

    # ── Summary metrics ────────────────────────────────────
    st.subheader("📈 Summary")

    avg_latency    = round(sum(r["latency"]["total_s"] for r in results) / len(results), 2)
    avg_hit_rate   = round(sum(r["retrieval"]["hit_rate_pct"] for r in results) / len(results), 1)
    avg_faithful   = round(sum(r["llm_judge"]["faithfulness"] for r in results) / len(results), 1)
    avg_relevance  = round(sum(r["llm_judge"]["relevance"] for r in results) / len(results), 1)
    avg_complete   = round(sum(r["llm_judge"]["completeness"] for r in results) / len(results), 1)
    avg_overall    = round(sum(r["llm_judge"]["overall"] for r in results) / len(results), 1)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Avg Latency",      f"{avg_latency}s")
    col2.metric("Retrieval Hit %",  f"{avg_hit_rate}%")
    col3.metric("Faithfulness",     f"{avg_faithful}/10")
    col4.metric("Relevance",        f"{avg_relevance}/10")
    col5.metric("Completeness",     f"{avg_complete}/10")
    col6.metric("Overall Score",    f"{avg_overall}/10")

    st.divider()

    # ── Latency chart ──────────────────────────────────────
    st.subheader("⚡ Latency Breakdown")

    lat_df = pd.DataFrame([
        {
            "Question": f"Q{r['id'][1:]}",
            "Embedding": r["latency"]["embedding_s"],
            "Pinecone":  r["latency"]["pinecone_s"],
            "LLM":       r["latency"]["llm_s"],
        }
        for r in results
    ])

    fig_lat = go.Figure()
    fig_lat.add_trace(go.Bar(name="Embedding", x=lat_df["Question"], y=lat_df["Embedding"], marker_color="#5856d6"))
    fig_lat.add_trace(go.Bar(name="Pinecone",  x=lat_df["Question"], y=lat_df["Pinecone"],  marker_color="#34c759"))
    fig_lat.add_trace(go.Bar(name="LLM",       x=lat_df["Question"], y=lat_df["LLM"],       marker_color="#ff9500"))
    fig_lat.update_layout(
        barmode="stack",
        height=350,
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", y=1.1),
        yaxis_title="Seconds"
    )
    st.plotly_chart(fig_lat, use_container_width=True)

    st.divider()

    # ── Retrieval quality chart ────────────────────────────
    st.subheader("🎯 Retrieval Hit Rate by Question")

    ret_df = pd.DataFrame([
        {
            "Question":  f"Q{r['id'][1:]}: {r['question'][:40]}...",
            "Hit Rate":  r["retrieval"]["hit_rate_pct"],
            "Category":  r["category"]
        }
        for r in results
    ])

    fig_ret = px.bar(
        ret_df,
        x="Question",
        y="Hit Rate",
        color="Category",
        height=350,
        labels={"Hit Rate": "Keyword Hit Rate (%)"}
    )
    fig_ret.update_layout(margin=dict(t=20, b=80), yaxis_range=[0, 100])
    st.plotly_chart(fig_ret, use_container_width=True)

    st.divider()

    # ── LLM judge scores ───────────────────────────────────
    st.subheader("🤖 LLM-as-Judge Scores")

    score_df = pd.DataFrame([
        {
            "Question":     f"Q{r['id'][1:]}",
            "Faithfulness": r["llm_judge"]["faithfulness"],
            "Relevance":    r["llm_judge"]["relevance"],
            "Completeness": r["llm_judge"]["completeness"],
            "Overall":      r["llm_judge"]["overall"],
        }
        for r in results
    ])

    fig_scores = go.Figure()
    fig_scores.add_trace(go.Scatter(name="Faithfulness", x=score_df["Question"], y=score_df["Faithfulness"], mode="lines+markers", marker_color="#5856d6"))
    fig_scores.add_trace(go.Scatter(name="Relevance",    x=score_df["Question"], y=score_df["Relevance"],    mode="lines+markers", marker_color="#34c759"))
    fig_scores.add_trace(go.Scatter(name="Completeness", x=score_df["Question"], y=score_df["Completeness"], mode="lines+markers", marker_color="#ff9500"))
    fig_scores.add_trace(go.Scatter(name="Overall",      x=score_df["Question"], y=score_df["Overall"],      mode="lines+markers", marker_color="#ff3b30", line=dict(dash="dash", width=2)))
    fig_scores.update_layout(
        height=350,
        margin=dict(t=20, b=20),
        yaxis=dict(range=[0, 10], title="Score (out of 10)"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_scores, use_container_width=True)

    st.divider()

    # ── Detailed results table ─────────────────────────────
    st.subheader("📋 Detailed Results")

    for r in results:
        with st.expander(f"Q{r['id'][1:]}: {r['question']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Expected Answer**")
                st.info(r["expected_answer"])
                st.markdown("**Actual Answer**")
                st.success(r["actual_answer"])
            with col2:
                st.markdown("**Latency**")
                st.markdown(f"- Embedding: `{r['latency']['embedding_s']}s`")
                st.markdown(f"- Pinecone: `{r['latency']['pinecone_s']}s`")
                st.markdown(f"- LLM: `{r['latency']['llm_s']}s`")
                st.markdown(f"- **Total: `{r['latency']['total_s']}s`**")
                st.markdown("**LLM Judge**")
                st.markdown(f"- Faithfulness: `{r['llm_judge']['faithfulness']}/10`")
                st.markdown(f"- Relevance: `{r['llm_judge']['relevance']}/10`")
                st.markdown(f"- Completeness: `{r['llm_judge']['completeness']}/10`")
                st.markdown(f"- Overall: `{r['llm_judge']['overall']}/10`")
                st.markdown(f"*{r['llm_judge']['reasoning']}*")
            st.markdown("**Retrieved Context Preview**")
            st.code(r["retrieval"]["context_preview"], language=None)

else:
    # ── Empty state ────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:4rem 0;opacity:0.4;">
        <p style="font-size:48px;">📊</p>
        <p style="font-size:18px;font-weight:500;">Upload a PDF and run evaluation to see results</p>
        <p style="font-size:14px;">Tests retrieval quality, answer accuracy and latency across 10 questions</p>
    </div>
    """, unsafe_allow_html=True)