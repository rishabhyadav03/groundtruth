import os

folder = "data/docs"

for name in sorted(os.listdir(folder)):
    if not name.endswith(".md"):
        continue
    print("\n=== " + name + " ===")
    in_code = False
    with open(os.path.join(folder, name), encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("```"):
                in_code = not in_code      # skip lines inside code blocks
            elif not in_code and line.startswith("#"):
                print(line.strip())