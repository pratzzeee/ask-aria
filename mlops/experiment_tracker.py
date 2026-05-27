import os
import json
from datetime import datetime
from typing import Optional

MLOPS_DIR        = "mlops"
BASELINE_PATH    = os.path.join(MLOPS_DIR, "baseline.json")
EXPERIMENTS_PATH = os.path.join(MLOPS_DIR, "experiments.json")

def compute_summary(results):
    n = len(results)
    return {
        "avg_latency_s":    round(sum(r["latency"]["total_s"]        for r in results) / n, 3),
        "avg_embedding_s":  round(sum(r["latency"]["embedding_s"]    for r in results) / n, 3),
        "avg_pinecone_s":   round(sum(r["latency"]["pinecone_s"]     for r in results) / n, 3),
        "avg_llm_s":        round(sum(r["latency"]["llm_s"]          for r in results) / n, 3),
        "avg_hit_rate_pct": round(sum(r["retrieval"]["hit_rate_pct"] for r in results) / n, 1),
        "avg_faithfulness": round(sum(r["llm_judge"]["faithfulness"] for r in results) / n, 1),
        "avg_relevance":    round(sum(r["llm_judge"]["relevance"]    for r in results) / n, 1),
        "avg_completeness": round(sum(r["llm_judge"]["completeness"] for r in results) / n, 1),
        "avg_overall":      round(sum(r["llm_judge"]["overall"]      for r in results) / n, 1),
        "num_questions":    n
    }

def save_baseline(results, config):
    baseline = {
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "config":   config,
        "summary":  compute_summary(results),
        "results":  results
    }
    with open(BASELINE_PATH, "w") as f:
        json.dump(baseline, f, indent=2)

def load_baseline():
    if not os.path.exists(BASELINE_PATH):
        return None
    with open(BASELINE_PATH, "r") as f:
        return json.load(f)

def save_experiment(name, description, results, config):
    experiment = {
        "name":        name,
        "description": description,
        "saved_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "config":      config,
        "summary":     compute_summary(results),
        "results":     results
    }
    if os.path.exists(EXPERIMENTS_PATH):
        with open(EXPERIMENTS_PATH, "r") as f:
            all_experiments = json.load(f)
    else:
        all_experiments = []
    all_experiments.append(experiment)
    with open(EXPERIMENTS_PATH, "w") as f:
        json.dump(all_experiments, f, indent=2)

def load_experiments():
    if not os.path.exists(EXPERIMENTS_PATH):
        return []
    with open(EXPERIMENTS_PATH, "r") as f:
        return json.load(f)

def compare_to_baseline(experiment_summary):
    baseline = load_baseline()
    if not baseline:
        return {}
    b = baseline["summary"]
    e = experiment_summary
    return {
        "latency_delta":      round(e["avg_latency_s"]    - b["avg_latency_s"],    3),
        "hit_rate_delta":     round(e["avg_hit_rate_pct"] - b["avg_hit_rate_pct"], 1),
        "faithfulness_delta": round(e["avg_faithfulness"] - b["avg_faithfulness"], 1),
        "relevance_delta":    round(e["avg_relevance"]    - b["avg_relevance"],    1),
        "completeness_delta": round(e["avg_completeness"] - b["avg_completeness"], 1),
        "overall_delta":      round(e["avg_overall"]      - b["avg_overall"],      1),
    }

def get_best_experiment():
    experiments = load_experiments()
    if not experiments:
        return None
    return max(experiments, key=lambda e: e["summary"]["avg_overall"])
