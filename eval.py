import os
import json
import time
import requests
from groq import Groq
from dotenv import load_dotenv
from rag import get_embedding, get_pinecone_index, query_rag
from config import TOP_K

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Load golden dataset ────────────────────────────────────

def load_golden_dataset(path: str = "eval_data/test_qa.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)

# ── Method 1: Latency Profiling ────────────────────────────

def measure_latency(question: str) -> dict:
    """
    Measure time taken for each step of the RAG pipeline.
    Returns dict with timing breakdown in seconds.
    """
    timings = {}

    # Step 1: Embedding latency
    t0 = time.time()
    question_vec = get_embedding(question)
    timings["embedding_s"] = round(time.time() - t0, 3)

    # Step 2: Pinecone query latency
    t0 = time.time()
    index   = get_pinecone_index()
    results = index.query(
        vector=question_vec,
        top_k=TOP_K,
        include_metadata=True
    )
    timings["pinecone_s"] = round(time.time() - t0, 3)

    # Step 3: Build context
    context = "\n\n".join(
        m.metadata["text"]
        for m in results.matches
        if m.metadata.get("text")
    )

    # Step 4: LLM latency
    t0 = time.time()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": f"Answer using only this context:\n{context}"},
            {"role": "user",   "content": question}
        ]
    )
    timings["llm_s"]   = round(time.time() - t0, 3)
    timings["total_s"] = round(sum(timings.values()), 3)
    timings["answer"]  = response.choices[0].message.content

    return timings

# ── Method 2: Retrieval Quality ────────────────────────────

def evaluate_retrieval(question: str, expected_answer: str) -> dict:
    """
    Check if the expected answer keywords appear in retrieved chunks.
    Returns hit rate and the retrieved context.
    """
    context = query_rag(question)

    # Check how many expected keywords are in the retrieved context
    keywords = [
        w.strip(".,?!").lower()
        for w in expected_answer.split()
        if len(w) > 3
    ]
    hits = sum(1 for kw in keywords if kw in context.lower())
    hit_rate = round(hits / len(keywords) * 100, 1) if keywords else 0

    return {
        "hit_rate_pct": hit_rate,
        "keywords_found": hits,
        "keywords_total": len(keywords),
        "context_preview": context[:300] + "..." if len(context) > 300 else context
    }

# ── Method 3: LLM-as-Judge ────────────────────────────────

def llm_judge(question: str, expected_answer: str, actual_answer: str) -> dict:
    """
    Use LLaMA to score the answer on 3 dimensions (1-10 each).
    Returns scores and reasoning.
    """
    judge_prompt = f"""You are an expert evaluator for RAG chatbot answers.
Score the ACTUAL ANSWER against the EXPECTED ANSWER on these 3 dimensions (1-10 each):

1. Faithfulness: Is the actual answer factually consistent with the expected answer?
2. Relevance: Does the actual answer address the question asked?
3. Completeness: Does the actual answer cover all key points in the expected answer?

Question: {question}
Expected Answer: {expected_answer}
Actual Answer: {actual_answer}

Respond ONLY in this exact JSON format with no extra text:
{{
  "faithfulness": <score 1-10>,
  "relevance": <score 1-10>,
  "completeness": <score 1-10>,
  "reasoning": "<one sentence explanation>"
}}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0.0
    )

    raw = response.choices[0].message.content.strip()

    try:
        scores = json.loads(raw)
        scores["overall"] = round(
            (scores["faithfulness"] + scores["relevance"] + scores["completeness"]) / 3, 1
        )
    except Exception:
        scores = {
            "faithfulness": 0,
            "relevance":    0,
            "completeness": 0,
            "overall":      0,
            "reasoning":    f"Parse error: {raw[:100]}"
        }

    return scores

# ── Full Evaluation Runner ─────────────────────────────────

def run_full_evaluation(dataset_path: str = "eval_data/test_qa.json") -> list[dict]:
    dataset = load_golden_dataset(dataset_path)
    results = []

    for i, item in enumerate(dataset["questions"]):
        question        = item["question"]
        expected_answer = item["expected_answer"]

        result = {
            "id":              item["id"],
            "question":        question,
            "expected_answer": expected_answer,
            "category":        item["category"],
            "difficulty":      item["difficulty"],
        }

        # Method 1: Latency
        latency = measure_latency(question)
        result["latency"]       = latency
        result["actual_answer"] = latency["answer"]

        # Method 2: Retrieval
        retrieval = evaluate_retrieval(question, expected_answer)
        result["retrieval"] = retrieval

        # Method 3: LLM judge
        scores = llm_judge(question, expected_answer, latency["answer"])
        result["llm_judge"] = scores

        results.append(result)

        # ← Rate limit protection: wait between questions
        if i < len(dataset["questions"]) - 1:
            time.sleep(15)

    return results