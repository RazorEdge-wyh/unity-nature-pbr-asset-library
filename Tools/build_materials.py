"""Build PBR material library from ambientCG (1K JPG) and Poly Haven textures (2K)."""
import json
import os
import re
import shutil
import sys
import zipfile
import concurrent.futures as cf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

PH_TEXTURES = {
    "forrest_ground_01": "Ground", "forest_ground_04": "Ground",
    "brown_mud_leaves_01": "Ground", "rocky_terrain_02": "Ground",
    "aerial_grass_rock": "Grass", "rocky_trail_02": "Ground",
    "aerial_rocks_02": "Rock", "coast_sand_rocks_02": "Rock",
    "snow_02": "Snow", "red_laterite_soil_stones": "Ground",
    "sand_01": "Sand", "coast_sand_01": "Sand", "gravelly_sand": "Sand",
    "aerial_beach_01": "Sand", "gravel_stones": "Gravel", "gravel_floor": "Gravel",
    "sandy_gravel_02": "Gravel", "bicolour_gravel": "Gravel", "rocky_gravel": "Gravel",
    "bark_brown_02": "Bark", "bark_brown_01": "Bark", "tree_bark_03": "Bark",
    "pine_bark": "Bark", "bark_willow": "Bark", "palm_tree_bark": "Bark",
    "sakura_bark": "Bark", "rock_face_03": "Rock", "rock_boulder_dry": "Rock",
    "weathered_brown_planks": "Wood", "wood_floor": "Wood",
}

ACG_CAT_FOLDER = {"Wood Floor": "WoodFloor", "Paving Stones": "PavingStones"}


def acg_texture(entry, outdir, name):
    zpath = os.path.join(lib.CACHE, "acg", entry["id"] + "_1K.zip")
    lib.download(entry["link1k"], zpath, headers={"User-Agent": lib.DL_HEADERS["User-Agent"]})
    os.makedirs(outdir, exist_ok=True)
    src = os.path.join(outdir, "_src")
    with zipfile.ZipFile(zpath) as z:
        z.extractall(src)
    col = nrm = rough = metal = ao = None
    for root, _, fs in os.walk(src):
        for f in fs:
            p = os.path.join(root, f)
            fu = f.upper()
            if "_COLOR." in fu:
                col = p
            elif "_NORMALGL." in fu:
                nrm = p
            elif "_ROUGHNESS." in fu:
                rough = p
            elif "_METALNESS." in fu:
                metal = p
            elif "_AMBIENTOCCLUSION." in fu:
                ao = p
    out = lib.build_textures(col, nrm, None, None, outdir, name, mask_size=None,
                             rough=rough, metal=metal, ao=ao)
    shutil.rmtree(src, ignore_errors=True)
    return out


def ph_texture(name, cat, outdir):
    man = lib.load_json(os.path.join(lib.MAN, "textures", name + ".json"))

    def pick(suffix, res="2k"):
        low = {k.lower(): k for k, v in man.items() if isinstance(v, dict) and res in v}
        k = low.get(suffix)
        if not k:
            return None
        entry = man[k][res]
        for fmt in ("jpg", "png"):
            if fmt in entry:
                return entry[fmt]["url"]
        return None

    os.makedirs(outdir, exist_ok=True)
    src_cache = os.path.join(lib.CACHE_TEX, name)
    os.makedirs(src_cache, exist_ok=True)
    urls = {"diff": pick("diffuse") or pick("diff"), "nor": pick("nor_gl"), "arm": pick("arm")}
    paths = {}
    for k, u in urls.items():
        if not u:
            continue
        ext = os.path.splitext(u)[1]
        p = os.path.join(src_cache, k + ext)
        lib.download(u, p)
        paths[k] = p
    files = lib.build_textures(paths.get("diff"), paths.get("nor"), paths.get("arm"),
                               None, outdir, name, mask_size=1024)
    return files


def acg_entry(e):
    folder = ACG_CAT_FOLDER.get(e["cat"], e["cat"].replace(" ", ""))
    outdir = os.path.join(lib.MATS, folder, e["id"])
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    files = acg_texture(e, outdir, e["id"])
    return {"name": e["id"], "category": folder, "type": "material",
            "source": "ambientCG", "sourceUrl": "https://ambientcg.com/view?id=%s" % e["id"],
            "license": "CC0", "resolution": 1024,
            "path": "Materials/%s/%s" % (folder, e["id"]),
            "files": files, "tags": e.get("tags", [])}


def ph_entry(name, cat):
    outdir = os.path.join(lib.MATS, cat, name)
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    files = ph_texture(name, cat, outdir)
    return {"name": name, "category": cat, "type": "material",
            "source": "Poly Haven", "sourceUrl": "https://polyhaven.com/a/%s" % name,
            "license": "CC0", "resolution": 2048,
            "path": "Materials/%s/%s" % (cat, name), "files": files}


def main():
    picks = lib.load_json(os.path.join(lib.ROOT, "acg_picks.json"))
    entries = []
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(acg_entry, e): e["id"] for e in picks}
        for f in cf.as_completed(futs):
            try:
                entries.append(f.result())
                print("acg ok", futs[f])
            except Exception as e:  # noqa: BLE001
                print("acg FAIL", futs[f], repr(e)[:200])
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(ph_entry, n, c): n for n, c in PH_TEXTURES.items()}
        for f in cf.as_completed(futs):
            try:
                entries.append(f.result())
                print("ph ok", futs[f])
            except Exception as e:  # noqa: BLE001
                print("ph FAIL", futs[f], repr(e)[:200])
    lib.dump_json(os.path.join(lib.DOCS, "materials.json"), entries)
    print("materials done:", len(entries))


if __name__ == "__main__":
    main()
