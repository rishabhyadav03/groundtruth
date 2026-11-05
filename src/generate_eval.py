import json
import os
import re
import time

from groq import Groq

from src.config import PRODUCTION_CONFIG
from src.metrics import recall_at_k
from src.retriever import Retriever

ANSWER_MODEL = "qwen/qwen3.8-27b"          # writes the answers
JUDGE_MODEL = "openai/gpt-oss-120b"        # checks the answers (a different model family)

# Both models can "think" before answering, which uses extra tokens.
# We turn the thinking down so each call is short and cheap.
REASONING = {
    "qwen/qwen3.8-27b": "none",
    "openai/gpt-oss-120b": "low",
}
CACHE_FILE = "results/generation_cache.json"
PAUSE_SECONDS = 10                         # pause after each call to stay under the free limits

ANSWER_PROMPT = """Answer the question using ONLY the context below.
If the context does not contain the answer, reply exactly: I don't know

Context:
{context}

Question: {question}
Answer in one or two sentences."""

JUDGE_PROMPT = """You are checking an answer from a question-answering system.

Question: {question}
Reference answer: {reference}

Context given to the system:
{context}

System answer: {answer}

Reply with only JSON that has two true/false fields:
"correct": true if the system answer says the same thing as the reference answer (different wording is fine)
"supported": true if every claim in the system answer is supported by the context
Example: {{"correct": true, "supported": true}}"""


def ask_groq(model, prompt, max_tokens):
    # Call Groq. If something goes wrong (for example a rate limit), wait and try again.
    client = Groq()          # reads the key from the GROQ_API_KEY environment variable
    options = {}
    if model in REASONING:
        options["reasoning_effort"] = REASONING[model]

    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=max_tokens,
                **options,
            )
            text = response.choices[0].message.content
            if not text or text.strip() == "":
                raise ValueError("empty reply")
            time.sleep(PAUSE_SECONDS)
            return text.strip()
        except Exception as error:
            message = str(error)
            if "404" in message or "400" in message:
                # wrong model name or a bad setting: waiting will not help
                raise RuntimeError("Groq rejected the request for " + model + ": " + message[:300])
            print("Groq error, waiting 30 seconds:", message[:120])
            time.sleep(30)
    raise RuntimeError("Groq kept failing, try again later")


def parse_json(text):
    # the judge should reply with only JSON, but remove code fences just in case
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(match.group(0))


def judge(question, reference, context, answer):
    prompt = JUDGE_PROMPT.format(question=question, reference=reference,
                                 context=context, answer=answer)
    for attempt in range(2):
        try:
            reply = ask_groq(JUDGE_MODEL, prompt, 1500)
            verdict = parse_json(reply)
            return bool(verdict["correct"]), bool(verdict["supported"])
        except Exception as error:
            print("Could not read the judge reply, trying again:", str(error)[:80])
    return None, None


def said_dont_know(answer):
    text = answer.lower().replace("\u2019", "'")
    return "i don't know" in text


def percent(part, total):
    if total == 0:
        return "n/a"
    return "%d/%d (%.0f%%)" % (part, total, 100 * part / total)


def make_report(cache):
    rows = list(cache.values())
    answerable = [r for r in rows if r["category"] != "unanswerable" and r["correct"] is not None]
    unanswerable = [r for r in rows if r["category"] == "unanswerable"]

    correct = [r for r in answerable if r["correct"]]
    wrong = [r for r in answerable if not r["correct"]]
    hit = [r for r in answerable if r["retrieval_hit"]]
    miss = [r for r in answerable if not r["retrieval_hit"]]
    hit_correct = [r for r in hit if r["correct"]]
    miss_correct = [r for r in miss if r["correct"]]
    wrong_retrieval = [r for r in wrong if not r["retrieval_hit"]]
    wrong_generation = [r for r in wrong if r["retrieval_hit"]]

    not_refused = [r for r in answerable if not r["refused"] and r["supported"] is not None]
    supported = [r for r in not_refused if r["supported"]]
    refused = [r for r in unanswerable if r["refused"]]

    lines = []
    lines.append("Answer model: " + ANSWER_MODEL + " | Judge model: " + JUDGE_MODEL)
    lines.append("")
    lines.append("- Correct answers: " + percent(len(correct), len(answerable)))
    lines.append("- Correct when retrieval found all the evidence in the top 5: " + percent(len(hit_correct), len(hit)))
    lines.append("- Correct when retrieval missed the evidence: " + percent(len(miss_correct), len(miss)))
    lines.append("- Wrong answers caused by retrieval (evidence not in top 5): " + percent(len(wrong_retrieval), len(wrong)))
    lines.append("- Wrong answers caused by generation (evidence was in top 5): " + percent(len(wrong_generation), len(wrong)))
    lines.append("- Answers fully supported by the context: " + percent(len(supported), len(not_refused)))
    lines.append("- Said I don't know on unanswerable questions: " + percent(len(refused), len(unanswerable)))
    return "\n".join(lines)


def main():
    with open("data/golden_set.json", encoding="utf-8") as f:
        golden = json.load(f)

    os.makedirs("results", exist_ok=True)
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            cache = json.load(f)          # so we can stop and continue later

    retriever = Retriever(
        chunk_size=PRODUCTION_CONFIG["chunk_size"],
        mode=PRODUCTION_CONFIG["mode"],
        use_reranker=PRODUCTION_CONFIG["rerank"],
        rerank_candidates=PRODUCTION_CONFIG["pool"],
        rerank_model=PRODUCTION_CONFIG["rerank_model"],
    )

    for item in golden:
        if item["id"] in cache:
            continue

        top_chunks = retriever.search(item["question"], k=5)
        context = "\n\n".join("[" + c["file"] + "]\n" + c["text"] for c in top_chunks)
        answer = ask_groq(ANSWER_MODEL,
                          ANSWER_PROMPT.format(context=context, question=item["question"]), 300)

        row = {"id": item["id"], "category": item["category"], "question": item["question"],
               "answer": answer, "refused": said_dont_know(answer),
               "retrieval_hit": None, "correct": None, "supported": None}

        if item["category"] != "unanswerable":
            row["retrieval_hit"] = recall_at_k(top_chunks, item["evidence"], 5) == 1.0
            if row["refused"]:
                row["correct"] = False
            else:
                row["correct"], row["supported"] = judge(
                    item["question"], item["reference_answer"], context, answer)

        cache[item["id"]] = row
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
        print(item["id"], item["category"], "| correct:", row["correct"],
              "| supported:", row["supported"], "| refused:", row["refused"])

    report = make_report(cache)
    with open("results/generation_results.md", "w", encoding="utf-8") as f:
        f.write(report)
    print()
    print(report)


if __name__ == "__main__":
    main()