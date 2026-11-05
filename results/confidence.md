### recall10

| Setup | average | 95% range | change vs baseline | 95% range of the change | verdict |
|---|---|---|---|---|---|
| baseline (100w, dense) | 0.87 | 0.79 to 0.93 | - | - | - |
| bigger chunks (300w, dense) | 0.84 | 0.77 to 0.91 | -0.02 | -0.10 to +0.06 | not clear |
| keyword only (100w, bm25) | 0.72 | 0.63 to 0.80 | -0.15 | -0.24 to -0.06 | worse |
| hybrid (100w) | 0.84 | 0.76 to 0.91 | -0.03 | -0.08 to +0.03 | not clear |
| dense + reranker (100w) | 0.93 | 0.87 to 0.98 | +0.06 | +0.02 to +0.11 | better |
| hybrid + reranker (100w) | 0.93 | 0.88 to 0.98 | +0.07 | +0.01 to +0.13 | better |
| dense + reranker L4 (100w) | 0.93 | 0.88 to 0.98 | +0.07 | +0.02 to +0.12 | better |

### mrr

| Setup | average | 95% range | change vs baseline | 95% range of the change | verdict |
|---|---|---|---|---|---|
| baseline (100w, dense) | 0.51 | 0.43 to 0.59 | - | - | - |
| bigger chunks (300w, dense) | 0.67 | 0.59 to 0.75 | +0.16 | +0.07 to +0.25 | better |
| keyword only (100w, bm25) | 0.48 | 0.39 to 0.57 | -0.04 | -0.14 to +0.07 | not clear |
| hybrid (100w) | 0.56 | 0.48 to 0.63 | +0.04 | -0.03 to +0.11 | not clear |
| dense + reranker (100w) | 0.71 | 0.64 to 0.78 | +0.20 | +0.13 to +0.27 | better |
| hybrid + reranker (100w) | 0.69 | 0.62 to 0.77 | +0.18 | +0.10 to +0.26 | better |
| dense + reranker L4 (100w) | 0.71 | 0.64 to 0.79 | +0.20 | +0.13 to +0.28 | better |
