# The configuration we ship. The regression test checks THIS one.
PRODUCTION_CONFIG = {
    "name": "production (dense + reranker L4, 100w, pool 20)",
    "chunk_size": 100,
    "mode": "dense",
    "rerank": True,
    "pool": 20,
    "rerank_model": "cross-encoder/ms-marco-MiniLM-L4-v2",
}