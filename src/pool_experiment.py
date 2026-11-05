import json
from src.run_eval import evaluate_config, average

POOL_CONFIGS = [
    {"name": "dense + reranker, pool 20",  "chunk_size": 100, "mode": "dense", "rerank": True, "pool": 20},
    {"name": "dense + reranker, pool 50",  "chunk_size": 100, "mode": "dense", "rerank": True, "pool": 50},
    {"name": "dense + reranker, pool 100", "chunk_size": 100, "mode": "dense", "rerank": True, "pool": 100},
]

with open("data/golden_set.json", encoding="utf-8") as f:
    golden = json.load(f)

lines = ["| Config | recall@5 | recall@10 | MRR | nDCG@10 | ms/query |",
         "|---|---|---|---|---|---|"]

for config in POOL_CONFIGS:
    print("Running:", config["name"])
    rows = evaluate_config(config, golden)
    lines.append("| %s | %.2f | %.2f | %.2f | %.2f | %.0f |" % (
        config["name"], average(rows, "recall5"), average(rows, "recall10"),
        average(rows, "mrr"), average(rows, "ndcg10"), average(rows, "ms")))

table = "\n".join(lines)
print()
print(table)

with open("results/pool_results.md", "w", encoding="utf-8") as f:
    f.write(table)