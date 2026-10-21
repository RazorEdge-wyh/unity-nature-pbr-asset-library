"""Merge per-type manifests into one library manifest + CSV index."""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

DOCS = lib.DOCS


def load_or(path, default):
    if os.path.exists(path):
        return lib.load_json(path)
    return default


def main():
    models = load_or(os.path.join(DOCS, "models.json"), [])
    materials = load_or(os.path.join(DOCS, "materials.json"), [])
    hdris = load_or(os.path.join(DOCS, "hdris.json"), [])

    data = {
        "version": "1.0.0",
        "name": "Unity Nature & Interior Asset Library",
        "license": "CC0 1.0 Universal (models, materials, HDRIs)",
        "generated": "2026-10-21",
        "models": models,
        "materials": materials,
        "hdris": hdris,
    }
    lib.dump_json(os.path.join(DOCS, "asset_library.json"), data)
    lib.dump_json(os.path.join(lib.ROOT, "asset_library.json"), data)

    # ---- CSV index
    rows = []
    for m in models:
        rows.append({
            "type": "3D Model", "name": m["name"], "category": m["category"],
            "file": m["file"], "tris": m["tris"], "tris_source": m["trisOriginal"],
            "materials": len(m.get("materials", [])),
            "source": m["source"], "license": m["license"], "source_url": m["sourceUrl"],
        })
    for m in materials:
        rows.append({
            "type": "PBR Material", "name": m["name"], "category": m["category"],
            "file": m["path"], "tris": "", "tris_source": "",
            "materials": "", "source": m["source"], "license": m["license"],
            "source_url": m["sourceUrl"],
        })
    for h in hdris:
        rows.append({
            "type": "HDRI Sky", "name": h["name"], "category": "HDRI",
            "file": h["path"], "tris": "", "tris_source": "",
            "materials": "", "source": h["source"], "license": h["license"],
            "source_url": h["sourceUrl"],
        })
    cols = ["type", "name", "category", "file", "tris", "tris_source", "materials",
            "source", "license", "source_url"]
    for path in (os.path.join(DOCS, "AssetIndex.csv"), os.path.join(lib.ROOT, "AssetIndex.csv")):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)

    total_tris = sum(m["tris"] for m in models)
    print("models", len(models), "materials", len(materials), "hdris", len(hdris),
          "TOTAL", len(rows), "tris", total_tris)
    cats = {}
    for m in models:
        cats[m["category"]] = cats.get(m["category"], 0) + 1
    print("model cats", cats)
    mc = {}
    for m in materials:
        mc[m["category"]] = mc.get(m["category"], 0) + 1
    print("material cats", mc)


if __name__ == "__main__":
    main()
