import os


def load_docs(folder):
    # read every .md file in the folder
    docs = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".md"):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                docs.append({"file": name, "text": f.read()})
    return docs


def make_chunks(docs, max_words):
    # Split each document into paragraphs (blank line = new paragraph).
    # Then group paragraphs together until the chunk reaches max_words.
    # A paragraph is never cut in half, so a sentence is never split.
    chunks = []
    for doc in docs:
        paragraphs = doc["text"].split("\n\n")
        current = []
        current_words = 0
        for para in paragraphs:
            if para.strip() == "":
                continue
            n_words = len(para.split())
            if current and current_words + n_words > max_words:
                chunks.append({"file": doc["file"], "text": "\n\n".join(current)})
                current = []
                current_words = 0
            current.append(para)
            current_words += n_words
        if current:
            chunks.append({"file": doc["file"], "text": "\n\n".join(current)})
    return chunks