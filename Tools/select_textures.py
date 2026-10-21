import json, os
MAN = r"C:\Users\PC GAMER\AppData\Local\Temp\assetlib\manifests"

def load(p):
    with open(p, encoding="utf-8-sig") as f:
        return json.load(f)

ph = load(os.path.join(MAN, "ph_textures.json"))
rows = []
for name, v in ph.items():
    cats = [c.lower() for c in v.get("categories", [])]
    rows.append((name, cats, v.get("download_count", 0)))

want_cats = ["grass", "dirt", "terrain", "natural", "sand", "bark", "forest floor", "moss", "gravel", "rock", "wood"]
picked = []
for wc in want_cats:
    subset = [r for r in rows if any(wc == c for c in r[1])]
    subset.sort(key=lambda r: -r[2])
    print(f"{wc}: {len(subset)} -> {[s[0] for s in subset[:8]]}")
    for r in subset[:6]:
        picked.append(r[0])
seen = []
for p in picked:
    if p not in seen:
        seen.append(p)
print("\nTOTAL picked", len(seen))
print(seen)

hd = load(os.path.join(MAN, "ph_hdris.json"))
hrows = []
for name, v in hd.items():
    cats = [c.lower() for c in v.get("categories", [])]
    hrows.append((name, cats, v.get("download_count", 0)))
for wc in ["outdoor", "nature", "sunrise/sunset", "skies", "field", "forest", "urban"]:
    subset = [r for r in hrows if any(wc == c for c in r[1])]
    subset.sort(key=lambda r: -r[2])
    print(f"HDRI {wc}: {[s[0] for s in subset[:10]]}")
