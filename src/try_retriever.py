import json
from src.retriever import Retriever
from src.metrics import chunk_has_evidence

with open("data/golden_set.json", encoding="utf-8") as f:
    golden = json.load(f)

sample = [g for g in golden if g["id"] in ("q001", "q031", "q056")]

for mode in ["dense", "bm25", "hybrid"]:
    retriever = Retriever(chunk_size=100, mode=mode)
    print("\n=== mode:", mode, "| number of chunks:", len(retriever.chunks))
    for item in sample:
        print("Q:", item["question"])
        results = retriever.search(item["question"], k=3)
        for rank, chunk in enumerate(results, start=1):
            correct = any(chunk_has_evidence(chunk, ev) for ev in item["evidence"])
            print("  ", rank, chunk["file"], "<-- CORRECT" if correct else "")