import os

folder = "data/docs"
files = [f for f in os.listdir(folder) if f.endswith(".md")]

total_words = 0
for name in files:
    with open(os.path.join(folder, name), encoding="utf-8") as f:
        total_words += len(f.read().split())

print("Number of files:", len(files))
print("Total words:", total_words)
print("Average words per file:", total_words // len(files))