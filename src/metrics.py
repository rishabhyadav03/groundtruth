import math


def clean(text):
    # remove extra spaces/newlines and ignore upper/lower case
    return " ".join(text.split()).lower()


def chunk_has_evidence(chunk, evidence):
    # chunk is a dict: {"file": "...", "text": "..."}
    # evidence is a dict: {"file": "...", "text": "..."}
    if chunk["file"] != evidence["file"]:
        return False
    return clean(evidence["text"]) in clean(chunk["text"])


def find_ranks(retrieved, evidence_list, k):
    # For each evidence, find the position (1, 2, 3...) of the first chunk
    # in the top k that contains it. None if it is not found.
    ranks = []
    for evidence in evidence_list:
        found_rank = None
        for position, chunk in enumerate(retrieved[:k], start=1):
            if chunk_has_evidence(chunk, evidence):
                found_rank = position
                break
        ranks.append(found_rank)
    return ranks


def recall_at_k(retrieved, evidence_list, k):
    ranks = find_ranks(retrieved, evidence_list, k)
    found = 0
    for r in ranks:
        if r is not None:
            found += 1
    return found / len(evidence_list)


def mrr(retrieved, evidence_list, k=10):
    ranks = find_ranks(retrieved, evidence_list, k)
    good_ranks = [r for r in ranks if r is not None]
    if len(good_ranks) == 0:
        return 0.0
    return 1 / min(good_ranks)


def ndcg_at_k(retrieved, evidence_list, k):
    # Go through the top k chunks. A chunk scores 1 if it contains an
    # evidence sentence we have not counted yet, otherwise 0.
    already_counted = set()
    dcg = 0.0
    for position, chunk in enumerate(retrieved[:k], start=1):
        for i, evidence in enumerate(evidence_list):
            if i not in already_counted and chunk_has_evidence(chunk, evidence):
                already_counted.add(i)
                dcg += 1 / math.log2(position + 1)
                break   # one chunk earns at most one point

    # Best possible score: all evidence sentences at the very top
    ideal_dcg = 0.0
    for position in range(1, min(len(evidence_list), k) + 1):
        ideal_dcg += 1 / math.log2(position + 1)

    return dcg / ideal_dcg