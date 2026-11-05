# Groundtruth

A small tool that checks whether a change to a retrieval system (the search part of RAG) really makes it better, using numbers instead of trying a few questions by hand.

I tested it on the FastAPI tutorial docs. The best setup I found was dense search plus a reranker. It raised recall@10 from 0.87 to 0.93 and MRR from 0.51 to 0.71, but each query takes about 650 ms on my CPU instead of 12 ms.

## What is in the repo

- 40 FastAPI doc files used as the corpus
- 100 questions with the sentence that answers each one
- recall@k, MRR and nDCG, written by hand and unit tested
- 6 retriever setups compared on the same questions
- a GitHub Action that fails a pull request if recall@10 drops by more than 1 point

## Results

Scored on the 90 questions that have an answer in the docs. Each setup changes one thing from the baseline.

| Setup | recall@10 | MRR | nDCG@10 | ms per query |
|---|---|---|---|---|
| baseline (100-word chunks, dense) | 0.87 | 0.51 | 0.60 | 12 |
| bigger chunks (300 words, dense) | 0.84 | 0.67 | 0.70 | 12 |
| keyword only (BM25) | 0.72 | 0.48 | 0.53 | 1 |
| hybrid (dense + BM25) | 0.84 | 0.56 | 0.61 | 15 |
| dense + reranker | 0.93 | 0.71 | 0.76 | 657 |
| hybrid + reranker | 0.93 | 0.69 | 0.74 | 663 |

Compared with the baseline, question by question, dense + reranker got 7 questions better, 1 worse and 82 the same.

I only have 90 scored questions, so one question is about 1 point. A gap of 2 or 3 points is not proof of anything.

## What I would use

Dense search (all-MiniLM-L6-v2) on 100-word chunks, then a cross-encoder reranker on the top 20. It is slow, but it was the only change that clearly helped. For something that needs instant answers I would skip the reranker.

## What did not work

- Hybrid search did not beat plain dense search (recall@10 0.84 vs 0.87). It helped 3 questions and hurt 6.
- 300-word chunks ranked results better (MRR 0.67 vs 0.51) but recall did not improve, and it sends almost 3 times more text.
- I tried letting the reranker look at 50 and 100 chunks instead of 20. recall@10 stayed about the same (0.92 and 0.94) and queries got 2 to 4 times slower. I tried this after looking at the failures, so take it with care.

## How the questions were made

There are 100 questions: 30 simple, 25 with exact keywords, 25 vaguely worded, 10 that need two files, and 10 that the docs cannot answer.

For every answerable question I saved the exact sentence from the docs that answers it. A retrieved chunk counts as correct if it comes from the right file and contains that sentence. This way the same questions work for any chunk size. A script checks that every sentence really exists in the docs.

[EDIT: say how you made the questions. For example: I used an LLM to draft them, then read all 100 and changed N of them.]

The 10 unanswerable questions are not used in the scores yet.

## The CI check

A test runs the best setup on every pull request. It fails if recall@10 is more than 0.01 below the saved baseline (0.9278).

To test it I opened a pull request that switched to keyword-only search. recall@10 fell to 0.717 and the check blocked it.

![failing check on the pull request](docs/ci-fail-pr.png)
![test log](docs/ci-fail-log.png)
![passing run on main and failing run on the bad branch](docs/ci-pass-vs-fail.png)

## Where it still fails

7 questions are still missed. For all of them the right file was in the top 3, but the right chunk was not. These are my guesses from reading the results:

- q003 (which HTTP methods send data): got a nearby chunk of the right file, and a chunk about HTTP methods from another file ranked first.
- q059 (stop extra values in the URL): the header, query and form model docs say almost the same thing, so they get mixed up.
- q065 (output does not match the declared type): the file has many similar chunks and the wrong one came first.
- q076 (what the editor helps with): a neighbouring chunk ranked higher.
- q086 (organize files so tests can import the app): the only question the reranker made worse. It picked another relevant chunk instead of the one with my exact sentence.

q010 and q066 look like the same problems.

## Limits

- Only 90 scored questions, and one set of docs.
- Matching one exact sentence is strict. A chunk that answers well but does not contain that sentence still counts as a miss.
- Times are from my laptop CPU.
- I only test retrieval. I did not measure how good the final generated answers are.

## Run it

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python src/check_golden.py      # check the questions against the docs
python -m pytest tests -v       # tests and the regression check
python -m src.run_eval          # run all 6 setups, saves to results/
python -m src.analyze           # compare with the baseline question by question
python -m src.error_analysis    # look at the failed questions
```

## Folders

```
data/docs/            FastAPI tutorial docs
data/golden_set.json  the 100 questions
src/                  chunker, retriever, metrics, run_eval, analysis scripts
tests/                metric tests, chunker test, regression check
results/              result tables and baseline.json
.github/workflows/    CI
```

The docs in `data/docs/` are from the FastAPI project (MIT license).
