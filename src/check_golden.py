import json
import os
from collections import Counter

def clean(text):
    # remove extra spaces/newlines and ignore upper/lower case
    return " ".join(text.split()).lower()

with open("data/golden_set.json", encoding="utf-8") as f:
    golden = json.load(f)

seen_ids = set()
problems = 0

for item in golden:
    if item["id"] in seen_ids:
        print("Duplicate id:", item["id"])
        problems += 1
    seen_ids.add(item["id"])

    if item["category"] != "unanswerable" and len(item["evidence"]) == 0:
        print(item["id"], "has no evidence")
        problems += 1

    for ev in item["evidence"]:
        path = os.path.join("data/docs", ev["file"])
        if not os.path.exists(path):
            print(item["id"], "file not found:", ev["file"])
            problems += 1
            continue
        with open(path, encoding="utf-8") as f:
            doc_text = clean(f.read())
        if clean(ev["text"]) not in doc_text:
            print(item["id"], "evidence text not found in", ev["file"])
            problems += 1

counts = Counter(item["category"] for item in golden)
print("Total questions:", len(golden))
print("Per category:", dict(counts))
print("Problems found:", problems)