import json

with open("results/results.json", encoding="utf-8") as f:
    results = json.load(f)
with open("data/golden_set.json", encoding="utf-8") as f:
    golden = json.load(f)

questions = {item["id"]: item["question"] for item in golden}

baseline_name = "baseline (100w, dense)"
baseline = {row["id"]: row["recall10"] for row in results[baseline_name]}

print("Question-by-question comparison with the baseline (recall@10)")
for name, rows in results.items():
    if name == baseline_name:
        continue
    better = 0
    worse = 0
    same = 0
    for row in rows:
        diff = row["recall10"] - baseline[row["id"]]
        if diff > 0:
            better += 1
        elif diff < 0:
            worse += 1
        else:
            same += 1
    print("%-30s better: %2d | worse: %2d | same: %2d" % (name, better, worse, same))

best_name = "dense + reranker (100w)"
print()
print("Questions that", best_name, "still misses (recall@10 below 1):")
for row in results[best_name]:
    if row["recall10"] < 1:
        print(row["id"], row["category"], round(row["recall10"], 2), "|", questions[row["id"]])