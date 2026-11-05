### Overall results (90 answerable questions)

| Config | recall@5 | recall@10 | MRR | nDCG@10 | ms/query | words in top 10 |
|---|---|---|---|---|---|---|
| baseline (100w, dense) | 0.78 | 0.87 | 0.51 | 0.60 | 12 | 869 |
| bigger chunks (300w, dense) | 0.77 | 0.84 | 0.67 | 0.70 | 12 | 2450 |
| keyword only (100w, bm25) | 0.61 | 0.72 | 0.48 | 0.53 | 1 | 882 |
| hybrid (100w) | 0.77 | 0.84 | 0.56 | 0.61 | 15 | 884 |
| dense + reranker (100w) | 0.89 | 0.93 | 0.71 | 0.76 | 657 | 879 |
| hybrid + reranker (100w) | 0.84 | 0.93 | 0.69 | 0.74 | 663 | 892 |

### recall@10 by question category

| Config | simple | keyword | vague | multi_doc |
|---|---|---|---|---|
| baseline (100w, dense) | 0.83 | 1.00 | 0.76 | 0.90 |
| bigger chunks (300w, dense) | 0.90 | 0.92 | 0.72 | 0.80 |
| keyword only (100w, bm25) | 0.73 | 0.80 | 0.68 | 0.55 |
| hybrid (100w) | 0.87 | 0.96 | 0.72 | 0.75 |
| dense + reranker (100w) | 0.93 | 1.00 | 0.84 | 0.95 |
| hybrid + reranker (100w) | 0.93 | 1.00 | 0.88 | 0.90 |