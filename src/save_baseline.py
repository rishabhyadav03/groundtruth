import json
from src.config import PRODUCTION_CONFIG
from src.run_eval import evaluate_config, average

with open("data/golden_set.json", encoding="utf-8") as f:
    golden = json.load(f)

rows = evaluate_config(PRODUCTION_CONFIG, golden)
recall10 = average(rows, "recall10")

with open("results/baseline.json", "w", encoding="utf-8") as f:
    json.dump({"config": PRODUCTION_CONFIG["name"],
               "recall10": round(recall10, 4)}, f, indent=2)

print("Saved baseline recall@10 =", round(recall10, 4))