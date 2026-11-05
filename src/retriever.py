import re
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from src.chunker import load_docs, make_chunks

EMBED_MODEL = "all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def tokenize(text):
    # lowercase words, keeping things like add_task as one word
    return re.findall(r"[a-z0-9_]+", text.lower())


class Retriever:
    def __init__(self, chunk_size=100, mode="dense", use_reranker=False,
                 rerank_candidates=20, rerank_model=RERANK_MODEL,
                 docs_folder="data/docs"):
        self.mode = mode
        self.use_reranker = use_reranker
        self.rerank_candidates = rerank_candidates

        docs = load_docs(docs_folder)
        self.chunks = make_chunks(docs, chunk_size)
        texts = [c["text"] for c in self.chunks]

        # dense search: turn every chunk into a vector
        self.embedder = SentenceTransformer(EMBED_MODEL)
        self.chunk_vectors = self.embedder.encode(texts, normalize_embeddings=True)

        # keyword search: BM25 over the same chunks
        self.bm25 = BM25Okapi([tokenize(t) for t in texts])

        # reranker: reads (question, chunk) together and scores them
        if use_reranker:
            self.reranker = CrossEncoder(rerank_model)

    def dense_ranking(self, query):
        query_vector = self.embedder.encode(query, normalize_embeddings=True)
        scores = self.chunk_vectors @ query_vector      # cosine similarity
        return np.argsort(-scores).tolist()             # best chunk index first

    def bm25_ranking(self, query):
        scores = self.bm25.get_scores(tokenize(query))
        return np.argsort(-scores).tolist()

    def hybrid_ranking(self, query):
        # Reciprocal Rank Fusion: each list gives a chunk 1/(60 + rank) points.
        # Chunks that rank high in BOTH lists end up on top.
        scores = {}
        for ranking in (self.dense_ranking(query), self.bm25_ranking(query)):
            for rank, chunk_index in enumerate(ranking, start=1):
                scores[chunk_index] = scores.get(chunk_index, 0) + 1 / (60 + rank)
        return sorted(scores, key=scores.get, reverse=True)

    def search(self, query, k=10):
        if self.mode == "dense":
            ranking = self.dense_ranking(query)
        elif self.mode == "bm25":
            ranking = self.bm25_ranking(query)
        else:
            ranking = self.hybrid_ranking(query)

        if self.use_reranker:
            # re-score only the top 20 candidates, then re-order them
            candidates = ranking[:self.rerank_candidates]
            pairs = [(query, self.chunks[i]["text"]) for i in candidates]
            scores = self.reranker.predict(pairs)
            order = np.argsort(-scores).tolist()
            ranking = [candidates[i] for i in order]

        return [self.chunks[i] for i in ranking[:k]]