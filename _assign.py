# Greedy unique assignment for index.html img src (by file content hash)
import re, os, hashlib
from collections import defaultdict

root = r"D:\downloads\Rosealraedeh-main"

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()

# All image files
files = []
for dirpath, _, fns in os.walk(os.path.join(root, "images")):
    for fn in fns:
        if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace("\\", "/")
            files.append(rel)

by_hash = defaultdict(list)
for rel in files:
    by_hash[md5(os.path.join(root, rel))].append(rel)

# Preferred path: subdirectory version when exists
def pick_path(h):
    paths = by_hash[h]
    paths.sort(key=lambda p: (p.count("/"), len(p), p))
    return paths[0]

hash_to_canonical = {h: pick_path(h) for h in by_hash}

# Slot definitions: (line_hint, category, current_src)
# We'll build replacements manually after analysis
text = open(os.path.join(root, "index.html"), encoding="utf-8").read()
slots = []
for i, line in enumerate(text.splitlines(), 1):
    m = re.search(r'src="(images/[^"]+)"', line)
    if m:
        p = m.group(1)
        fp = os.path.join(root, p)
        h = md5(fp) if os.path.isfile(fp) else None
        slots.append((i, p, h))

used = set()
logo_hash = md5(os.path.join(root, "images/logo.png"))

# Categories for preference scoring
def score(rel, cat):
    r = rel.lower()
    if cat == "marble":
        return 10 if "marble" in r or "marbles" in r or "kalakata" in r or "183112" in r or "183122" in r or "183155" in r or "\u0627" in r else 0
    if cat == "granite":
        return 10 if "granit" in r or "galaxy" in r or "ubatua" in r or "183223" in r or "183229" in r or "183236" in r else 0
    if cat == "travertine":
        return 10 if "trav" in r else 0
    if cat == "quartz":
        return 10 if "quartz" in r or "183200" in r or "183206" in r or "183216" in r else 0
    if cat == "onyx":
        return 10 if "onyx" in r or "183241" in r or "183303" in r or "183309" in r else 0
    if cat == "hall":
        return 10 if "hall" in r else 0
    if cat == "stairs":
        return 10 if "stair" in r else 0
    if cat == "entrance":
        return 10 if "entrance" in r or "entranc" in r else 0
    if cat == "wall":
        return 10 if "wall" in r else 0
    if cat == "wash":
        return 10 if "wash" in r else 0
    if cat == "slab":
        return 10 if "slab" in r else 0
    if cat == "gallery":
        return 5  # flexible
    if cat == "brand":
        return 10 if "logo" in r else 0
    if cat == "general":
        return 3 if rel in ("images/intro.png", "images/about.png", "images/hallrose.png", "images/download.jpg") else 0
    return 0

# Map line ranges to categories
def cat_for_line(ln):
    if ln in (16, 757): return "brand"
    if ln in (52, 68): return "general"
    if 85 <= ln <= 127: return "marble"
    if 157 <= ln <= 199: return "quartz"
    if 229 <= ln <= 271: return "granite"
    if 301 <= ln <= 343: return "onyx"
    if 393 <= ln <= 402: return "marble"
    if 417 <= ln <= 426: return "granite"
    if 446 <= ln <= 451: return "travertine"
    if 467 <= ln <= 479: return "onyx"
    if 501 <= ln <= 506: return "quartz"
    if ln == 521: return "slab"
    if ln == 541: return "hall"
    if ln == 556: return "stairs"
    if ln == 576: return "entrance"
    if ln == 591: return "wall"
    if ln == 610: return "wash"
    if ln == 634: return "general"
    if 647 <= ln <= 659: return "gallery"  # products - mixed
    if 674 <= ln <= 710: return "gallery"
    return "gallery"

# Greedy assign each slot best unused hash for category
assignments = {}
for ln, cur, cur_h in slots:
    cat = cat_for_line(ln)
    if cur_h == logo_hash:
        assignments[ln] = cur  # logo twice OK
        if ln == 16:
            used.add(logo_hash)
        continue
    best = None
    best_sc = -1
    for h, paths in by_hash.items():
        if h in used:
            continue
        rel = hash_to_canonical[h]
        sc = score(rel, cat)
        if sc > best_sc:
            best_sc = sc
            best = rel
    if best is None:
        # must repeat - pick best scoring even if used
        for h, paths in by_hash.items():
            rel = hash_to_canonical[h]
            sc = score(rel, cat)
            if sc > best_sc:
                best_sc = sc
                best = rel
        assignments[ln] = best + "  # REPEAT"
    else:
        used.add(md5(os.path.join(root, best)))
        assignments[ln] = best

for ln, cur, _ in slots:
    new = assignments[ln].split("  #")[0]
    if new != cur:
        print(f"L{ln}: {cur} -> {new}")

print("\n--- Repeats after greedy ---")
from collections import Counter
chosen = [assignments[ln].split("  #")[0] for ln, _, _ in slots]
ch = Counter()
for ln, _, _ in slots:
    p = assignments[ln].split("  #")[0]
    fp = os.path.join(root, p)
    if os.path.isfile(fp):
        ch[md5(fp)] += 1
for h, c in ch.items():
    if c > 1:
        print(c, hash_to_canonical[h])
