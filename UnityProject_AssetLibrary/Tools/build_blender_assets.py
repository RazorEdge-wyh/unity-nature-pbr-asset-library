"""Import Blender-built OBJ models into the Unity asset library.

- generates procedural PBR textures for the Blender material keys
- copies OBJ/MTL + hard-links textures into Assets/AssetLibrary/Models/<cat>/<name>/
- appends manifest entries to Documentation/models.json
"""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

BLENDER_OUT = os.path.join(lib.ROOT, "blender_out")
TEX_DIR = os.path.join(lib.CACHE, "blender_tex")

# key -> (base rgb, roughness, metallic)
MATERIALS = {
    "linen_cream":   ((0.87, 0.84, 0.78), 0.85, 0.0, "fabric"),
    "linen_gray":    ((0.52, 0.53, 0.55), 0.90, 0.0, "fabric"),
    "walnut":        ((0.21, 0.12, 0.07), 0.45, 0.0, "wood"),
    "oak":           ((0.56, 0.40, 0.24), 0.50, 0.0, "wood"),
    "black_metal":   ((0.035, 0.035, 0.04), 0.35, 0.9, "metal"),
    "brushed_steel": ((0.62, 0.63, 0.66), 0.28, 1.0, "metal"),
    "concrete":      ((0.55, 0.54, 0.52), 0.85, 0.0, "stone"),
    "ceramic_white": ((0.90, 0.90, 0.88), 0.18, 0.0, "ceramic"),
    "brass":         ((0.76, 0.58, 0.28), 0.30, 1.0, "metal"),
    "canvas_art":    ((0.93, 0.91, 0.87), 0.90, 0.0, "fabric"),
    "rug_fabric":    ((0.46, 0.44, 0.42), 0.95, 0.0, "fabric"),
    "soil":          ((0.09, 0.07, 0.05), 1.00, 0.0, "soil"),
    "lamp_shade":    ((0.94, 0.90, 0.82), 0.80, 0.0, "fabric"),
    "bulb_warm":     ((1.00, 0.93, 0.80), 0.30, 0.0, "ceramic"),
}
EMISSIVE = {"bulb_warm"}


def fbm(shape, octaves=4, seed=0):
    rng = np.random.default_rng(seed)
    h, w = shape
    acc = np.zeros((h, w), np.float32)
    amp = 1.0
    total = 0.0
    for o in range(octaves):
        size = max(2, int(2 ** (o + 2)))
        low = rng.random((size, size)).astype(np.float32)
        im = Image.fromarray((low * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += amp * (np.asarray(im, np.float32) / 255.0)
        total += amp
        amp *= 0.5
    return acc / total


def normal_from_height(height, strength=3.0):
    gy, gx = np.gradient(height.astype(np.float32))
    nx = -gx * strength
    ny = -gy * strength
    nz = np.ones_like(height)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / ln, ny / ln, nz / ln
    rgb = np.dstack([(nx * 0.5 + 0.5) * 255, (ny * 0.5 + 0.5) * 255, (nz * 0.5 + 0.5) * 255])
    return rgb.astype(np.uint8)


def make_material_textures(key):
    base, rough, metal, kind = MATERIALS[key]
    os.makedirs(TEX_DIR, exist_ok=True)
    alb = os.path.join(TEX_DIR, key + "_Albedo.jpg")
    nrm = os.path.join(TEX_DIR, key + "_Normal.jpg")
    msk = os.path.join(TEX_DIR, key + "_Mask.png")
    if os.path.exists(alb) and os.path.exists(nrm) and os.path.exists(msk):
        return alb, nrm, msk

    N = 1024
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N
    seed = sum(ord(c) for c in key)

    if kind == "wood":
        grain = np.sin((yy * 26.0 + fbm((N, N), 4, seed) * 3.2) * np.pi * 2.0)
        grain = 0.5 + 0.5 * grain
        fine = fbm((N, N), 5, seed + 7)
        v = 0.82 + 0.18 * grain * (0.7 + 0.3 * fine)
        height = grain * 0.6 + fine * 0.4
        height_img = height
        nstrength = 1.1
    elif kind == "fabric":
        weave = (np.sin(xx * 420.0) * np.sin(yy * 420.0))
        noise = fbm((N, N), 4, seed)
        v = 0.90 + 0.06 * weave + 0.06 * (noise - 0.5)
        height_img = weave * 0.5 + noise * 0.5
        nstrength = 0.7
    elif kind == "metal":
        streak = fbm((N, N), 3, seed)
        streak = np.asarray(Image.fromarray((streak * 255).astype(np.uint8)).resize((N // 64, 1), Image.BOX).resize((N, N), Image.BICUBIC), np.float32) / 255.0
        fine = fbm((N, N), 5, seed + 3)
        v = 0.92 + 0.08 * (streak - 0.5) + 0.03 * (fine - 0.5)
        height_img = fine * 0.3
        nstrength = 0.35
    elif kind == "stone":
        m = fbm((N, N), 5, seed)
        pits = (fbm((N, N), 3, seed + 5) > 0.62).astype(np.float32)
        v = 0.86 + 0.24 * (m - 0.5) - 0.08 * pits
        height_img = m * 0.8 + pits * 0.2
        nstrength = 1.4
    elif kind == "soil":
        m = fbm((N, N), 5, seed + 9)
        v = 0.8 + 0.4 * (m - 0.5)
        height_img = m
        nstrength = 2.0
    elif kind == "ceramic":
        m = fbm((N, N), 3, seed + 11)
        v = 0.985 + 0.03 * (m - 0.5)
        height_img = m * 0.2
        nstrength = 0.25
    else:
        v = np.ones((N, N), np.float32)
        height_img = v * 0.5
        nstrength = 0.5

    rgb = np.dstack([np.clip(base[0] * v, 0, 1) * 255,
                     np.clip(base[1] * v, 0, 1) * 255,
                     np.clip(base[2] * v, 0, 1) * 255]).astype(np.uint8)
    Image.fromarray(rgb).save(alb, quality=92)

    hsmall = np.asarray(Image.fromarray((np.clip(height_img, 0, 1) * 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS), np.float32) / 255.0
    Image.fromarray(normal_from_height(hsmall, nstrength)).save(nrm, quality=95)

    rough_map = np.clip(rough + (fbm((512, 512), 3, seed + 21) - 0.5) * 0.10, 0.02, 1.0)
    metal_c = np.full((512, 512), int(metal * 255), np.uint8)
    ao_c = np.full((512, 512), 255, np.uint8)
    rough_c = (rough_map * 255).astype(np.uint8)
    smooth = 255 - rough_c
    mask = np.dstack([metal_c, ao_c, rough_c, smooth]).astype(np.uint8)
    Image.fromarray(mask, "RGBA").save(msk)
    return alb, nrm, msk


def obj_stats(path):
    tris = 0
    mn = [1e9, 1e9, 1e9]
    mx = [-1e9, -1e9, -1e9]
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                p = line.split()
                for i in range(3):
                    val = float(p[i + 1])
                    if val < mn[i]:
                        mn[i] = val
                    if val > mx[i]:
                        mx[i] = val
            elif line.startswith("f "):
                tris += len(line.split()) - 3
    return tris, [round(v, 3) for v in mn], [round(v, 3) for v in mx]


def main():
    man_path = os.path.join(BLENDER_OUT, "manifest.json")
    models = lib.load_json(man_path)
    index_path = os.path.join(lib.DOCS, "models.json")
    entries = lib.load_json(index_path) if os.path.exists(index_path) else []
    names = {e["name"] for e in entries}

    # material textures are generated once and hard-linked per model
    for key in MATERIALS:
        make_material_textures(key)
    print("textures generated for", len(MATERIALS), "materials")

    added = 0
    for m in models:
        name, category = m["name"], m["category"]
        src = os.path.join(BLENDER_OUT, name, name + ".obj")
        if not os.path.exists(src):
            print("MISSING", src)
            continue
        outdir = os.path.join(lib.LIB, category, name)
        texdir = os.path.join(outdir, "Textures")
        if os.path.isdir(outdir):
            shutil.rmtree(outdir)
        os.makedirs(texdir, exist_ok=True)
        shutil.copy2(src, os.path.join(outdir, name + ".obj"))
        mtl = src[:-4] + ".mtl"
        if os.path.exists(mtl):
            shutil.copy2(mtl, os.path.join(outdir, name + ".mtl"))
        tris, bmin, bmax = obj_stats(src)

        mats = []
        for key in m["materials"]:
            alb, nrm, msk = make_material_textures(key)
            for f in (alb, nrm, msk):
                dst = os.path.join(texdir, os.path.basename(f))
                if os.path.exists(dst):
                    os.remove(dst)
                try:
                    os.link(f, dst)
                except OSError:
                    shutil.copy2(f, dst)
            mats.append({
                "name": key, "sourceName": key,
                "albedo": os.path.basename(alb),
                "normal": os.path.basename(nrm),
                "mask": os.path.basename(msk),
                "renderMode": "opaque", "doubleSided": False,
                "emissive": key in EMISSIVE, "metallic": None, "roughness": None,
            })
        entry = {
            "name": name, "category": category, "type": "model",
            "source": "Blender (self-made)", "sourceUrl": "https://github.com/RazorEdge-wyh/unity-nature-pbr-asset-library",
            "license": "CC0",
            "file": "%s/%s/%s.obj" % (category, name, name),
            "trisOriginal": int(tris), "tris": int(tris),
            "boundsMin": bmin, "boundsMax": bmax, "materials": mats,
        }
        entries = [e for e in entries if e["name"] != name] + [entry]
        added += 1
        print("added %-24s %s %6d tris mats=%d" % (name, category, tris, len(mats)))
    lib.dump_json(index_path, entries)
    print("blender models imported:", added, "| total models:", len(entries))


if __name__ == "__main__":
    main()
