import json
from src.config import PRODUCTION_CONFIG
from src.run_eval import evaluate_config, average

ALLOWED_DROP = 0.01   # one point


def test_recall_at_10_has_not_dropped():
    with open("data/golden_set.json", encoding="utf-8") as f:
        golden = json.load(f)
    with open("results/baseline.json", encoding="utf-8") as f:
        baseline = json.load(f)

    rows = evaluate_config(PRODUCTION_CONFIG, golden)
    current = average(rows, "recall10")

    print("baseline recall@10:", baseline["recall10"], "| current:", round(current, 3))
    assert current >= baseline["recall10"] - ALLOWED_DROP, (
        "recall@10 dropped from %.3f to %.3f" % (baseline["recall10"], current))