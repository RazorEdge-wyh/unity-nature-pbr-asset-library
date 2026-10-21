import json, os
MAN = r"C:\Users\PC GAMER\AppData\Local\Temp\assetlib\manifests"
OUT = r"C:\Users\PC GAMER\AppData\Local\Temp\assetlib"

def load(p):
    with open(p, encoding="utf-8-sig") as f:
        return json.load(f)

acg = load(os.path.join(MAN, "ambientcg.json"))
assets = acg["foundAssets"]
plan = {"Wood": 6, "Wood Floor": 4, "Planks": 3, "Ground": 10, "Grass": 5, "Gravel": 5,
        "Rock": 5, "Metal": 7, "Bricks": 5, "Fabric": 4, "Concrete": 3, "Tiles": 3}
picked = []
for cat, n in plan.items():
    out = []
    sub = [a for a in assets if a.get("displayCategory") == cat]
    for a in sub:
        if len(out) >= n:
            break
        zips = a["downloadFolders"]["default"]["downloadFiletypeCategories"]["zip"]["downloads"]
        attrs = {z.get("attribute"): z for z in zips}
        if "1K-JPG" in attrs and "2K-JPG" in attrs:
            out.append({"id": a["assetId"], "cat": cat,
                        "tags": [t for t in a.get("tags", []) if not t.startswith(a["assetId"].lower())][:6],
                        "link1k": attrs["1K-JPG"]["downloadLink"],
                        "size1k": attrs["1K-JPG"].get("size"),
                        "link2k": attrs["2K-JPG"]["downloadLink"],
                        "size2k": attrs["2K-JPG"].get("size")})
    print(f"{cat:14s} {len(sub):3d} avail -> {len(out):2d} picked: {[o['id'] for o in out]}")
    picked += out
print("TOTAL", len(picked), "sum MB", round(sum(p["size1k"] for p in picked) / 1e6, 1))
with open(os.path.join(OUT, "acg_picks.json"), "w", encoding="utf-8") as f:
    json.dump(picked, f, indent=1)
