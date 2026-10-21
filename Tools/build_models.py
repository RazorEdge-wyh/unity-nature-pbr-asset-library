"""Download + simplify Poly Haven models, export Unity-ready OBJ/FBX-style layout."""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
import numpy as np

CATEGORIES = {
    "Trees": ["fir_tree_01", "fir_sapling", "fir_sapling_medium", "pine_sapling_medium",
              "pine_sapling_small", "island_tree_01", "island_tree_02", "island_tree_03",
              "jacaranda_tree", "tree_small_02", "quiver_tree_01", "quiver_tree_02",
              "searsia_burchellii", "searsia_lucida", "dead_tree_trunk", "dead_tree_trunk_02",
              "dead_quiver_trunk", "single_root", "root_cluster_01"],
    "Plants": ["celandine_01", "dandelion_01", "flower_empodium", "flower_gazania",
               "flower_heliophila", "flower_stinkkruid", "flower_ursinia", "periwinkle_plant",
               "shrub_01", "shrub_02", "shrub_03", "shrub_04", "shrub_sorrel_01", "fern_02",
               "nettle_plant", "weed_plant_02", "moss_01", "grass_bermuda_01",
               "grass_medium_01", "grass_medium_02", "dry_branches_medium_01",
               "bark_debris_01", "dead_quiver_branch_01"],
    "PottedPlants": ["potted_plant_01", "potted_plant_02", "potted_plant_04",
                     "anthurium_botany_01", "calathea_orbifolia_01", "pachira_aquatica_01",
                     "planter_box_01", "planter_box_02", "planter_box_03"],
    "Rocks": ["boulder_01", "rock_07", "rock_09", "rock_moss_set_01", "rock_moss_set_02",
              "stone_01", "namaqualand_boulder_02", "sand_rocks_small_01"],
    "Lamps": ["street_lamp_01", "street_lamp_02", "Lantern_01", "wooden_lantern_01",
              "vintage_oil_lamp", "hanging_industrial_lamp", "industrial_wall_lamp",
              "industrial_wall_sconce", "modern_ceiling_lamp_01", "caged_hanging_light",
              "lantern_chandelier_01", "brass_diya_lantern", "wooden_candlestick",
              "brass_candleholders", "lightbulb_01", "security_light"],
    "Props": ["treasure_chest", "ceramic_pot", "wicker_basket_01", "wooden_bowl_01",
              "tree_stump_01", "tree_stump_02"],
}

TARGETS = {"Trees": 60000, "Plants": 15000, "PottedPlants": 18000,
           "Rocks": 8000, "Lamps": 6000, "Props": 5000}

EMISSIVE_HINTS = ("bulb", "light", "flame", "glow", "lantern")
GLASS_HINTS = ("glass", "lampshade", "shade")


def pick_map(man, part, suffixes):
    """Find a manifest map entry (1k, jpg preferred) for part+suffix."""
    low = {k.lower(): k for k, v in man.items() if isinstance(v, dict) and "1k" in v}
    cands = []
    for s in suffixes:
        if part:
            cands.append(part.lower() + "_" + s)
        cands.append(s)
    for c in cands:
        k = low.get(c)
        if not k:
            continue
        entry = man[k]["1k"]
        for fmt in ("jpg", "png"):
            if fmt in entry:
                return k, entry[fmt]["url"], entry[fmt]["size"]
    return None, None, 0


def download_model_maps(name, man, gltf_js, workdir):
    """Returns {mat_name: {'diff':path,'nor':path,'arm':path,'alpha':path,...}}"""
    texdir = os.path.join(workdir, "maps")
    os.makedirs(texdir, exist_ok=True)
    mats = {}
    slug = name.lower()
    for m in gltf_js.get("materials", []):
        mn = m.get("name") or name
        part = mn
        if mn.lower().startswith(slug + "_"):
            part = mn[len(slug) + 1:]
        elif mn.lower() == slug:
            part = ""
        info = {"alphaMode": m.get("alphaMode", "OPAQUE"),
                "doubleSided": m.get("doubleSided", False),
                "metallic": m.get("pbrMetallicRoughness", {}).get("metallicFactor"),
                "roughness": m.get("pbrMetallicRoughness", {}).get("roughnessFactor"),
                "emissive": m.get("emissiveFactor"),
                "paths": {}}
        specs = [("diff", ["diff", "diffuse"]), ("nor", ["nor_gl"]), ("arm", ["arm"])]
        for key, sufs in specs:
            k, url, size = pick_map(man, part, sufs)
            if url is None and part:
                k, url, size = pick_map(man, "", sufs)
            if url:
                ext = os.path.splitext(url)[1]
                p = os.path.join(texdir, f"{name}_{mn}_{key}{ext}")
                lib.download(url, p)
                info["paths"][key] = p
        if info["alphaMode"] != "OPAQUE" or any(h in mn.lower() for h in GLASS_HINTS):
            k, url, size = pick_map(man, part, ["alpha", "opacity", "op", "mask"])
            if url is None and part:
                k, url, size = pick_map(man, "", ["alpha", "opacity", "op", "mask"])
            if url:
                ext = os.path.splitext(url)[1]
                p = os.path.join(texdir, f"{name}_{mn}_alpha{ext}")
                lib.download(url, p)
                info["paths"]["alpha"] = p
        mats[mn] = info
    return mats


def process_model(name, category, man):
    src = os.path.join(lib.CACHE, "models", name)
    os.makedirs(src, exist_ok=True)
    g = man["gltf"]["1k"]["gltf"]
    gltf_path = os.path.join(src, "%s_1k.gltf" % name)
    lib.download(g["url"], gltf_path)
    js = json.load(open(gltf_path, encoding="utf-8"))
    bin_path = None
    for k, v in g.get("include", {}).items():
        if k.endswith(".bin"):
            bin_path = os.path.join(src, os.path.basename(k))
            lib.download(v["url"], bin_path)
    tris0 = lib.gltf_tri_count(js)
    target = TARGETS[category]
    if tris0 > 3_000_000:
        target = int(target * 2)

    mats = download_model_maps(name, man, js, src)
    use_js, use_bin = js, None

    if tris0 > target * 1.05:
        # strip texture references then simplify with gltfpack
        staged = json.loads(json.dumps(js))
        for k in ("images", "textures", "samplers"):
            staged.pop(k, None)
        for m in staged.get("materials", []):
            pbr = m.get("pbrMetallicRoughness", {})
            for key in ("baseColorTexture", "metallicRoughnessTexture"):
                pbr.pop(key, None)
            m["pbrMetallicRoughness"] = pbr
            for key in ("normalTexture", "occlusionTexture", "emissiveTexture"):
                m.pop(key, None)
        staged_path = os.path.join(src, "%s_staged.gltf" % name)
        with open(staged_path, "w", encoding="utf-8") as f:
            json.dump(staged, f)
        glb_path = os.path.join(src, "%s_sim.glb" % name)
        ratio = max(0.004, min(1.0, target / float(tris0)))
        cmd = [lib.GLTFPACK, "-i", staged_path, "-o", glb_path, "-si", "%.4f" % ratio,
               "-vp", "16", "-vt", "16", "-vn", "16", "-kn"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(glb_path):
            raise RuntimeError("gltfpack failed %s: %s %s" % (name, r.stdout, r.stderr))
        use_js, use_bin = lib.load_gltf(glb_path)
    else:
        with open(bin_path, "rb") as f:
            use_bin = f.read()

    tris1 = lib.gltf_tri_count(use_js)

    # ---- write final asset folder
    outdir = os.path.join(lib.LIB, category, name)
    texdir = os.path.join(outdir, "Textures")
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(texdir, exist_ok=True)

    mat_names = []
    for i, m in enumerate(use_js.get("materials", [])):
        mn = m.get("name") or "%s_%d" % (name, i)
        safe = re.sub(r"[^A-Za-z0-9_\-]+", "_", mn)
        while safe in mat_names:
            safe += "_"
        mat_names.append(safe)

    tex_manifest = {}
    material_entries = []
    for i, m in enumerate(use_js.get("materials", [])):
        mn = m.get("name") or "%s_%d" % (name, i)
        safe = mat_names[i]
        info = mats.get(mn, {"alphaMode": "OPAQUE", "doubleSided": False, "paths": {}})
        p = info["paths"]
        files = lib.build_textures(p.get("diff"), p.get("nor"), p.get("arm"),
                                   p.get("alpha"), texdir, safe, mask_size=512,
                                   rough=info.get("roughness"), metal=info.get("metallic"))
        tex_manifest[safe] = {"albedo": files.get("albedo"), "normal": files.get("normal")}
        lname = mn.lower()
        if any(h in lname for h in GLASS_HINTS):
            render = "transparent"
        elif files.get("albedo", "").endswith(".png") and p.get("alpha"):
            render = "cutout"
        else:
            render = "opaque"
        emissive = bool(any(h in lname for h in EMISSIVE_HINTS)) and category == "Lamps"
        material_entries.append({
            "name": safe,
            "sourceName": mn,
            "albedo": files.get("albedo"),
            "normal": files.get("normal"),
            "mask": files.get("mask"),
            "renderMode": render,
            "doubleSided": bool(m.get("doubleSided", True)),
            "emissive": emissive,
            "metallic": info.get("metallic"),
            "roughness": info.get("roughness"),
        })

    obj_path = os.path.join(outdir, name + ".obj")
    mtl_path = os.path.join(outdir, name + ".mtl")
    lib.export_obj(use_js, use_bin, obj_path, mtl_path, mat_names, tex_manifest)

    # bounds
    allpos = []
    for mesh_idx, world, _ in lib.walk_nodes(use_js, use_bin):
        for prim in use_js["meshes"][mesh_idx]["primitives"]:
            pos = lib.read_accessor(use_js, use_bin, prim["attributes"]["POSITION"])
            pos = pos @ world[:3, :3].T + world[:3, 3]
            allpos.append(pos)
    if allpos:
        pos = np.concatenate(allpos)
        bmin = pos.min(axis=0).round(3).tolist()
        bmax = pos.max(axis=0).round(3).tolist()
    else:
        bmin = bmax = [0, 0, 0]

    entry = {
        "name": name,
        "category": category,
        "type": "model",
        "source": "Poly Haven",
        "sourceUrl": "https://polyhaven.com/a/%s" % name,
        "license": "CC0",
        "file": "%s/%s/%s.obj" % (category, name, name),
        "trisOriginal": int(tris0),
        "tris": int(tris1),
        "boundsMin": bmin,
        "boundsMax": bmax,
        "materials": material_entries,
    }
    print("  %-24s %-18s tris %8d -> %6d  mats %d" % (name, category, tris0, tris1, len(material_entries)))
    return entry


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    index_path = os.path.join(lib.DOCS, "models.json")
    entries = lib.load_json(index_path) if os.path.exists(index_path) else []
    done = {e["name"] for e in entries}
    for cat, names in CATEGORIES.items():
        for name in names:
            if only and name not in only:
                continue
            if name in done and not only:
                continue
            man_path = os.path.join(lib.MAN, "models", name + ".json")
            if not os.path.exists(man_path):
                print("MISSING manifest", name)
                continue
            man = lib.load_json(man_path)
            try:
                entry = process_model(name, cat, man)
                entries = [e for e in entries if e["name"] != name] + [entry]
                lib.dump_json(index_path, entries)
            except Exception as e:  # noqa: BLE001
                print("FAIL", name, repr(e)[:300])
    print("models done:", len(entries))


if __name__ == "__main__":
    main()
