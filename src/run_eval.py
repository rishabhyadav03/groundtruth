import json
import os
import time

from src.retriever import Retriever,RERANK_MODEL
from src.metrics import recall_at_k, mrr, ndcg_at_k

# Each config changes ONE thing compared to the baseline (first row)
CONFIGS = [
    {"name": "baseline (100w, dense)",      "chunk_size": 100, "mode": "dense",  "rerank": False},
    {"name": "bigger chunks (300w, dense)", "chunk_size": 300, "mode": "dense",  "rerank": False},
    {"name": "keyword only (100w, bm25)",   "chunk_size": 100, "mode": "bm25",   "rerank": False},
    {"name": "hybrid (100w)",               "chunk_size": 100, "mode": "hybrid", "rerank": False},
    {"name": "dense + reranker (100w)",     "chunk_size": 100, "mode": "dense",  "rerank": True},
    {"name": "hybrid + reranker (100w)",    "chunk_size": 100, "mode": "hybrid", "rerank": True},
    {"name": "dense + reranker L4 (100w)", "chunk_size": 100, "mode": "dense", "rerank": True,
    "rerank_model": "cross-encoder/ms-marco-MiniLM-L4-v2"},
]

CATEGORIES = ["simple", "keyword", "vague", "multi_doc"]


def evaluate_config(config, golden):
    retriever = Retriever(
        chunk_size=config["chunk_size"],
        mode=config["mode"],
        use_reranker=config["rerank"],
        rerank_candidates=config.get("pool", 20),
        rerank_model=config.get("rerank_model", RERANK_MODEL),
    )
    rows = []
    for item in golden:
        if len(item["evidence"]) == 0:
            continue                      # unanswerable questions have no evidence
        start = time.perf_counter()
        retrieved = retriever.search(item["question"], k=10)
        elapsed_ms = (time.perf_counter() - start) * 1000

        rows.append({
            "id": item["id"],
            "category": item["category"],
            "recall5": recall_at_k(retrieved, item["evidence"], 5),
            "recall10": recall_at_k(retrieved, item["evidence"], 10),
            "mrr": mrr(retrieved, item["evidence"], 10),
            "ndcg10": ndcg_at_k(retrieved, item["evidence"], 10),
            "ms": elapsed_ms,
            "words": sum(len(c["text"].split()) for c in retrieved),
        })
    return rows


def average(rows, key):
    return sum(r[key] for r in rows) / len(rows)


def make_tables(all_results):
    lines = []

    lines.append("### Overall results (90 answerable questions)")
    lines.append("")
    lines.append("| Config | recall@5 | recall@10 | MRR | nDCG@10 | ms/query | words in top 10 |")
    lines.append("|---|---|---|---|---|---|---|")
    for name, rows in all_results.items():
        lines.append("| %s | %.2f | %.2f | %.2f | %.2f | %.0f | %.0f |" % (
            name, average(rows, "recall5"), average(rows, "recall10"),
            average(rows, "mrr"), average(rows, "ndcg10"),
            average(rows, "ms"), average(rows, "words")))

    lines.append("")
    lines.append("### recall@10 by question category")
    lines.append("")
    lines.append("| Config | " + " | ".join(CATEGORIES) + " |")
    lines.append("|---|" + "---|" * len(CATEGORIES))
    for name, rows in all_results.items():
        cells = []
        for cat in CATEGORIES:
            cat_rows = [r for r in rows if r["category"] == cat]
            cells.append("%.2f" % average(cat_rows, "recall10"))
        lines.append("| " + name + " | " + " | ".join(cells) + " |")

    return "\n".join(lines)


def main():
    with open("data/golden_set.json", encoding="utf-8") as f:
        golden = json.load(f)

    all_results = {}
    for config in CONFIGS:
        print("Running:", config["name"])
        all_results[config["name"]] = evaluate_config(config, golden)

    os.makedirs("results", exist_ok=True)
    with open("results/results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    tables = make_tables(all_results)
    with open("results/results.md", "w", encoding="utf-8") as f:
        f.write(tables)

    print()
    print(tables)


if __name__ == "__main__":
    main()