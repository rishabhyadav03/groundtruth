import json

with open("results/results.json", encoding="utf-8") as f:
    results = json.load(f)

rows = results["dense + reranker (100w)"]
recall10 = sum(r["recall10"] for r in rows) / len(rows)

with open("results/baseline.json", "w", encoding="utf-8") as f:
    json.dump({"config": "dense + reranker (100w, pool 20)",
               "recall10": round(recall10, 4)}, f, indent=2)

print("Saved baseline recall@10 =", round(recall10, 4))