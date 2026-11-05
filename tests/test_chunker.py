import json
from src.chunker import load_docs, make_chunks
from src.metrics import chunk_has_evidence


def test_every_evidence_sentence_is_inside_a_chunk():
    docs = load_docs("data/docs")
    with open("data/golden_set.json", encoding="utf-8") as f:
        golden = json.load(f)

    for size in (100, 300):
        chunks = make_chunks(docs, size)
        for item in golden:
            for ev in item["evidence"]:
                found = any(chunk_has_evidence(c, ev) for c in chunks)
                assert found, item["id"] + " evidence missing at size " + str(size)