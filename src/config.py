# The configuration we ship. The regression test checks THIS one.
PRODUCTION_CONFIG = {
    "name": "production (dense + reranker, 100w, pool 20)",
    "chunk_size": 100,
    "mode": "dense",
    "rerank": True,
    "pool": 20,
}