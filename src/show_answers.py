import json
import random

random.seed(1)

with open("results/generation_cache.json", encoding="utf-8") as f:
    cache = json.load(f)
with open("data/golden_set.json", encoding="utf-8") as f:
    golden = json.load(f)
reference = {item["id"]: item["reference_answer"] for item in golden}

rows = [r for r in cache.values() if r["category"] != "unanswerable"]
wrong = [r for r in rows if not r["correct"]]
right = [r for r in rows if r["correct"]]
sample = random.sample(right, 10)


def show(r):
    print("-" * 60)
    print(r["id"], r["category"], "| evidence in top 5:", r["retrieval_hit"],
          "| judge says correct:", r["correct"])
    print("Q:", r["question"])
    print("Reference:", reference[r["id"]])
    print("Answer:", r["answer"])


print("=== ALL WRONG ANSWERS ===")
for r in wrong:
    show(r)

print()
print("=== 10 RANDOM ANSWERS THE JUDGE CALLED CORRECT ===")
for r in sample:
    show(r)