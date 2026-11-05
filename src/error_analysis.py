import json
from src.retriever import Retriever
from src.metrics import chunk_has_evidence

FAILED_IDS = ["q003", "q010", "q059", "q065", "q066", "q076", "q086"]

with open("data/golden_set.json", encoding="utf-8") as f:
    golden = json.load(f)
by_id = {item["id"]: item for item in golden}

with open("results/results.json", encoding="utf-8") as f:
    results = json.load(f)

# Part 1: did the reranker make any question worse than the baseline?
baseline = {row["id"]: row["recall10"] for row in results["baseline (100w, dense)"]}
print("Questions the reranker made WORSE than the baseline:")
for row in results["dense + reranker (100w)"]:
    if row["recall10"] < baseline[row["id"]]:
        print(" ", row["id"], by_id[row["id"]]["question"],
              "| before:", round(baseline[row["id"]], 2), "after:", round(row["recall10"], 2))

# Part 2: look closely at each failed question
retriever = Retriever(chunk_size=100, mode="dense", use_reranker=True)

for qid in FAILED_IDS:
    item = by_id[qid]
    print()
    print("=" * 70)
    print(qid, item["category"], "|", item["question"])
    for ev in item["evidence"]:
        print("EXPECTED in", ev["file"], ":", ev["text"][:100])

    # where is the evidence in the plain dense ranking (before the reranker)?
    ranking = retriever.dense_ranking(item["question"])
    for ev in item["evidence"]:
        position = None
        for rank, chunk_index in enumerate(ranking, start=1):
            if chunk_has_evidence(retriever.chunks[chunk_index], ev):
                position = rank
                break
        print("dense rank of the evidence chunk:", position, "(out of", len(ranking), "chunks)")

    # what did the full system return?
    top3 = retriever.search(item["question"], k=3)
    for rank, chunk in enumerate(top3, start=1):
        print("  top", rank, chunk["file"], "|", chunk["text"][:120].replace("\n", " "))