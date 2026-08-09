import re, os, hashlib
from collections import Counter, defaultdict

root = r"D:\downloads\Rosealraedeh-main"
text = open(os.path.join(root, "index.html"), encoding="utf-8").read()
css = open(os.path.join(root, "style.css"), encoding="utf-8").read()

refs_html = re.findall(r'src="(images/[^"]+)"', text)
refs_css = re.findall(r"url\(['\"]?(images/[^'\"\)]+)['\"]?\)", css)

print("=== HTML ===")
print("Total img tags:", len(refs_html))
c = Counter(refs_html)
print("Unique src paths:", len(c))
print("\nRepetitions in HTML:")
for p, n in sorted(c.items(), key=lambda x: (-x[1], x[0])):
    if n > 1:
        print(f"  {n}x  {p}")

print("\n=== CSS backgrounds ===")
cc = Counter(refs_css)
for p, n in sorted(cc.items(), key=lambda x: (-x[1], x[0])):
    print(f"  {n}x  {p}")

out = open(os.path.join(root, "_analyze_lines.txt"), "w", encoding="utf-8")
out.write("=== Line-by-line HTML ===\n")
for i, line in enumerate(text.splitlines(), 1):
    m = re.search(r'src="(images/[^"]+)"', line)
    if m:
        out.write(f"  L{i}: {m.group(1)}\n")
out.close()

# Group duplicate files by content hash (same image, different path)
def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()

hashes = defaultdict(list)
for dirpath, _, files in os.walk(os.path.join(root, "images")):
    for fn in files:
        if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace("\\", "/")
            try:
                hashes[md5(os.path.join(root, rel))].append(rel)
            except OSError:
                pass

print("\n=== Duplicate files (same bytes, different paths) ===")
for h, paths in sorted(hashes.items(), key=lambda x: -len(x[1])):
    if len(paths) > 1:
        print(" ", paths)

used = set(refs_html) | set(refs_css)
all_imgs = []
for dirpath, _, files in os.walk(os.path.join(root, "images")):
    for fn in files:
        if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace("\\", "/")
            all_imgs.append(rel)

# unused by path (consider content hash - if duplicate path points to same file, one path used = both "used")
used_hashes = set()
for p in used:
    fp = os.path.join(root, p)
    if os.path.isfile(fp):
        used_hashes.add(md5(fp))

unused_unique = []
for rel in sorted(all_imgs):
    fp = os.path.join(root, rel)
    h = md5(fp)
    if h not in used_hashes:
        unused_unique.append(rel)

print("\n=== Unused image files (by content, not referenced in html/css) ===")
for p in unused_unique:
    print(" ", p)
