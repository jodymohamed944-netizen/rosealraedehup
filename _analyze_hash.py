import re, os, hashlib
from collections import defaultdict

root = r"D:\downloads\Rosealraedeh-main"
text = open(os.path.join(root, "index.html"), encoding="utf-8").read()

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()

refs = []
for i, line in enumerate(text.splitlines(), 1):
    m = re.search(r'src="(images/[^"]+)"', line)
    if m:
        p = m.group(1)
        fp = os.path.join(root, p)
        h = md5(fp) if os.path.isfile(fp) else "MISSING"
        refs.append((i, p, h))

by_hash = defaultdict(list)
for line, p, h in refs:
    by_hash[h].append((line, p))

print("=== Same image content used multiple times (HTML) ===")
for h, items in sorted(by_hash.items(), key=lambda x: -len(x[1])):
    if len(items) > 1:
        print(len(items), "uses:")
        for line, p in items:
            print(f"  L{line}: {p}")
        print()
