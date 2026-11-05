import json
import random

random.seed(0)                 # same answer every time you run it
N_RESAMPLES = 1000
BASELINE = "baseline (100w, dense)"
METRICS = ["recall10", "mrr"]

with open("results/results.json", encoding="utf-8") as f:
    results = json.load(f)


def mean(values):
    return sum(values) / len(values)


def bootstrap_range(values):
    # Pretend we ran the test again many times: pick 90 questions at random
    # (the same question can be picked twice), take the average, repeat.
    # The middle 95% of those averages is our range.
    means = []
    for _ in range(N_RESAMPLES):
        sample = [random.choice(values) for _ in range(len(values))]
        means.append(mean(sample))
    means.sort()
    low = means[int(0.025 * N_RESAMPLES)]
    high = means[int(0.975 * N_RESAMPLES)]
    return low, high


lines = []
for metric in METRICS:
    base_by_id = {row["id"]: row[metric] for row in results[BASELINE]}

    lines.append("### " + metric)
    lines.append("")
    lines.append("| Setup | average | 95% range | change vs baseline | 95% range of the change | verdict |")
    lines.append("|---|---|---|---|---|---|")

    for name, rows in results.items():
        values = [row[metric] for row in rows]
        low, high = bootstrap_range(values)
        text = "| %s | %.2f | %.2f to %.2f |" % (name, mean(values), low, high)

        if name == BASELINE:
            text += " - | - | - |"
        else:
            diffs = [row[metric] - base_by_id[row["id"]] for row in rows]
            d_low, d_high = bootstrap_range(diffs)
            if d_low > 0:
                verdict = "better"
            elif d_high < 0:
                verdict = "worse"
            else:
                verdict = "not clear"
            text += " %+.2f | %+.2f to %+.2f | %s |" % (mean(diffs), d_low, d_high, verdict)
        lines.append(text)
    lines.append("")

table = "\n".join(lines)
print(table)
with open("results/confidence.md", "w", encoding="utf-8") as f:
    f.write(table)