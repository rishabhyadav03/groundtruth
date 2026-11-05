import json
from src.run_eval import evaluate_config, average

MODELS = [
    ("MiniLM L6 (current)", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
    ("MiniLM L4", "cross-encoder/ms-marco-MiniLM-L4-v2"),
    ("MiniLM L2", "cross-encoder/ms-marco-MiniLM-L2-v2"),
]

with open("data/golden_set.json", encoding="utf-8") as f:
    golden = json.load(f)

lines = ["| Reranker | recall@10 | MRR | nDCG@10 | ms/query |",
         "|---|---|---|---|---|"]

for name, model_id in MODELS:
    print("Running:", name)
    config = {"name": name, "chunk_size": 100, "mode": "dense",
              "rerank": True, "pool": 20, "rerank_model": model_id}
    rows = evaluate_config(config, golden)
    lines.append("| %s | %.2f | %.2f | %.2f | %.0f |" % (
        name, average(rows, "recall10"), average(rows, "mrr"),
        average(rows, "ndcg10"), average(rows, "ms")))

table = "\n".join(lines)
print()
print(table)
with open("results/speed_results.md", "w", encoding="utf-8") as f:
    f.write(table)