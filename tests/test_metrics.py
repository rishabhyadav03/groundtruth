import pytest
from src.metrics import recall_at_k, mrr, ndcg_at_k

EVIDENCE = [{"file": "a.md", "text": "Pydantic does the validation"}]

WRONG = {"file": "a.md", "text": "something unrelated"}
RIGHT = {"file": "a.md", "text": "Yes, Pydantic does the validation here."}
RIGHT_TEXT_WRONG_FILE = {"file": "b.md", "text": "Pydantic does the validation"}


def test_correct_chunk_at_rank_2():
    retrieved = [WRONG, RIGHT]
    assert recall_at_k(retrieved, EVIDENCE, 1) == 0.0
    assert recall_at_k(retrieved, EVIDENCE, 2) == 1.0
    assert mrr(retrieved, EVIDENCE) == 0.5
    assert ndcg_at_k(retrieved, EVIDENCE, 5) == pytest.approx(0.6309, abs=0.001)


def test_correct_chunk_at_rank_1():
    retrieved = [RIGHT, WRONG]
    assert mrr(retrieved, EVIDENCE) == 1.0
    assert ndcg_at_k(retrieved, EVIDENCE, 5) == 1.0


def test_nothing_found():
    retrieved = [WRONG, WRONG]
    assert recall_at_k(retrieved, EVIDENCE, 5) == 0.0
    assert mrr(retrieved, EVIDENCE) == 0.0
    assert ndcg_at_k(retrieved, EVIDENCE, 5) == 0.0


def test_same_text_wrong_file_does_not_count():
    retrieved = [RIGHT_TEXT_WRONG_FILE]
    assert recall_at_k(retrieved, EVIDENCE, 5) == 0.0


def test_two_evidence_one_found():
    evidence = [
        {"file": "a.md", "text": "first sentence"},
        {"file": "b.md", "text": "second sentence"},
    ]
    retrieved = [{"file": "a.md", "text": "the first sentence is here"}]
    assert recall_at_k(retrieved, evidence, 5) == 0.5