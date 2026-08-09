import re, os, hashlib
from collections import Counter
root = r"D:\downloads\Rosealraedeh-main"
text = open(os.path.join(root, "index.html"), encoding="utf-8").read()
refs = re.findall(r'src="(images/[^"]+)"', text)
missing = [r for r in set(refs) if not os.path.isfile(os.path.join(root, r))]
print("Missing:", missing or "none")
print("Duplicates:", {k: v for k, v in Counter(refs).items() if v > 1 and k != "images/logo.png"})

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()

for a, b in [
    ("images/hall2.png", "images/halls/hall2.png"),
    ("images/granits.png", "images/granite/granits.png"),
]:
    pa, pb = os.path.join(root, a), os.path.join(root, b)
    if os.path.exists(pa) and os.path.exists(pb):
        print(a, "vs", b, ":", "SAME" if md5(pa) == md5(pb) else "DIFF")
