# The configuration we ship. The regression test checks THIS one.
PRODUCTION_CONFIG = {
    "name": "production (bm25 + reranker, 100w, pool 20)",
    "chunk_size": 100,
    "mode": "bm25",
    "rerank": False,
    "pool": 20,
}