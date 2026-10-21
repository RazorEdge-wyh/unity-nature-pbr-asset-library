"""Shared helpers for the Unity asset-library build pipeline."""
import io
import json
import os
import shutil
import struct
import subprocess
import time
import urllib.request
import urllib.error
import zipfile

from PIL import Image
import numpy as np

ROOT = r"C:\Users\PC GAMER\AppData\Local\Temp\assetlib"
MAN = os.path.join(ROOT, "manifests")
CACHE = os.path.join(ROOT, "cache")
PROJ = os.path.join(ROOT, "out", "AssetLibrary")
ASSETS = os.path.join(PROJ, "Assets", "AssetLibrary")
LIB = os.path.join(ASSETS, "Models")
MATS = os.path.join(ASSETS, "Materials")
ENV = os.path.join(ASSETS, "Environment")
DOCS = os.path.join(ASSETS, "Documentation")
CACHE_TEX = os.path.join(CACHE, "tex")
GLTFPACK = os.path.join(ROOT, "bin", "gltfpack.exe")

DL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://polyhaven.com/",
}

for d in (CACHE, CACHE_TEX, DOCS):
    os.makedirs(d, exist_ok=True)


def load_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def http_get(url, headers=None, retries=4, timeout=300):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or DL_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def download(url, path, headers=None):
    """Download url -> path (cached, atomic-ish)."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = http_get(url, headers=headers)
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
    return path


# ---------------------------------------------------------------- glTF / GLB
def load_gltf(path):
    """Return (json_dict, binary_buffer_bytes)."""
    if path.lower().endswith(".glb"):
        with open(path, "rb") as f:
            data = f.read()
        magic, ver, length = struct.unpack("<III", data[:12])
        assert magic == 0x46546C67, "not a glb"
        off = 12
        js = None
        binc = b""
        while off < length:
            clen, ctype = struct.unpack("<II", data[off:off + 8])
            chunk = data[off + 8:off + 8 + clen]
            if ctype == 0x4E4F534A:
                js = json.loads(chunk.decode("utf-8"))
            elif ctype == 0x004E4942:
                binc = chunk
            off += 8 + clen
        return js, binc
    with open(path, encoding="utf-8") as f:
        js = json.load(f)
    binc = b""
    for b in js.get("buffers", []):
        uri = b.get("uri")
        if uri and not uri.startswith("data:"):
            with open(os.path.join(os.path.dirname(path), uri), "rb") as f2:
                binc = f2.read()
    return js, binc


_CT = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2),
       5125: ("I", 4), 5126: ("f", 4)}
_NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
_NPF = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read_accessor(js, binc, idx):
    acc = js["accessors"][idx]
    n = acc["count"]
    ctype = acc["componentType"]
    typ = acc["type"]
    fmt, size = _CT[ctype]
    ncomp = _NC[typ]
    if "bufferView" not in acc:
        return np.zeros((n, ncomp), dtype=np.float32)
    bv = js["bufferViews"][acc["bufferView"]]
    base = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = bv.get("byteStride") or (size * ncomp)
    if stride == size * ncomp:
        arr = np.frombuffer(binc, dtype=np.dtype("<" + fmt), count=n * ncomp, offset=base)
        out = arr.reshape(n, ncomp)
    else:
        out = np.empty((n, ncomp), dtype=np.dtype("<" + fmt))
        for i in range(n):
            out[i] = np.frombuffer(binc, dtype=np.dtype("<" + fmt), count=ncomp,
                                   offset=base + i * stride)
    if acc.get("normalized") and fmt != "f":
        maxv = float(np.iinfo(np.dtype(fmt)).max)
        out = out.astype(np.float32) / maxv
    return out


def _mat_mul(a, b):
    return a @ b


def node_matrix(node):
    if "matrix" in node:
        return np.array(node["matrix"], dtype=np.float64).reshape(4, 4).T
    m = np.eye(4)
    t = node.get("translation", [0, 0, 0])
    r = node.get("rotation", [0, 0, 0, 1])
    s = node.get("scale", [1, 1, 1])
    x, y, z, w = r
    rm = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])
    sm = np.diag(s)
    m[:3, :3] = rm @ sm
    m[:3, 3] = t
    return m


def walk_nodes(js, binc):
    """Yield (mesh_index, world_matrix, node_name) for every mesh node."""
    nodes = js.get("nodes", [])
    scenes = js.get("scenes", [])
    roots = scenes[js.get("scene", 0)]["nodes"] if scenes else list(range(len(nodes)))
    out = []

    def rec(i, parent):
        nd = nodes[i]
        world = parent @ node_matrix(nd)
        if "mesh" in nd:
            out.append((nd["mesh"], world, nd.get("name", f"node{i}")))
        for c in nd.get("children", []):
            rec(c, world)

    for r in roots:
        rec(r, np.eye(4))
    return out


def gltf_tri_count(js):
    tris = 0
    for m in js.get("meshes", []):
        for pr in m["primitives"]:
            if "indices" in pr:
                tris += js["accessors"][pr["indices"]]["count"] // 3
            else:
                tris += js["accessors"][pr["attributes"]["POSITION"]]["count"] // 3
    return tris


def export_obj(js, binc, obj_path, mtl_path, mat_names, texture_basenames):
    """Write OBJ + MTL. texture_basenames: {material_name: {'albedo':..., 'normal':...}}"""
    lines = ["# Generated by AssetLibrary pipeline", "mtllib " + os.path.basename(mtl_path)]
    voff = 1
    vtoff = 1
    vnoff = 1
    mat_order = []
    for mesh_idx, world, node_name in walk_nodes(js, binc):
        mesh = js["meshes"][mesh_idx]
        rot = world[:3, :3]
        trans = world[:3, 3]
        for pi, prim in enumerate(mesh["primitives"]):
            attrs = prim["attributes"]
            pos = read_accessor(js, binc, attrs["POSITION"]).astype(np.float64)
            pos = pos @ rot.T + trans
            has_n = "NORMAL" in attrs
            has_uv = "TEXCOORD_0" in attrs
            nor = read_accessor(js, binc, attrs["NORMAL"]).astype(np.float64) if has_n else None
            if nor is not None:
                nor = nor @ np.linalg.inv(rot).T
                n = np.linalg.norm(nor, axis=1, keepdims=True)
                nor = nor / np.where(n == 0, 1, n)
            uv = read_accessor(js, binc, attrs["TEXCOORD_0"]).astype(np.float64) if has_uv else None
            if "indices" in prim:
                idx = read_accessor(js, binc, prim["indices"]).reshape(-1).astype(np.int64)
            else:
                idx = np.arange(len(pos), dtype=np.int64)
            mi = prim.get("material")
            mname = mat_names[mi] if mi is not None else "default"
            if mname not in mat_order:
                mat_order.append(mname)
            lines.append("o %s_%d" % (node_name.replace(" ", "_"), pi))
            lines.append("usemtl " + mname)
            for p in pos:
                lines.append("v %.6f %.6f %.6f" % (p[0], p[1], p[2]))
            if uv is not None:
                for t in uv:
                    lines.append("vt %.6f %.6f" % (t[0], 1.0 - t[1]))
            if nor is not None:
                for nn in nor:
                    lines.append("vn %.6f %.6f %.6f" % (nn[0], nn[1], nn[2]))
            for i in range(0, len(idx), 3):
                a, b, c = idx[i], idx[i + 1], idx[i + 2]
                if has_uv and has_n:
                    lines.append("f %d/%d/%d %d/%d/%d %d/%d/%d" % (
                        a + voff, a + vtoff, a + vnoff,
                        b + voff, b + vtoff, b + vnoff,
                        c + voff, c + vtoff, c + vnoff))
                elif has_uv:
                    lines.append("f %d/%d %d/%d %d/%d" % (
                        a + voff, a + vtoff, b + voff, b + vtoff, c + voff, c + vtoff))
                elif has_n:
                    lines.append("f %d//%d %d//%d %d//%d" % (
                        a + voff, a + vnoff, b + voff, b + vnoff, c + voff, c + vnoff))
                else:
                    lines.append("f %d %d %d" % (a + voff, b + voff, c + voff))
            voff += len(pos)
            if uv is not None:
                vtoff += len(uv)
            if nor is not None:
                vnoff += len(nor)
    os.makedirs(os.path.dirname(obj_path), exist_ok=True)
    with open(obj_path, "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines))
        f.write("\n")

    mtl = ["# Generated by AssetLibrary pipeline", "newmtl default", "Kd 0.8 0.8 0.8"]
    for name in mat_names:
        tex = texture_basenames.get(name, {})
        mtl += ["", "newmtl " + name, "Kd 1 1 1", "Ka 1 1 1", "Ks 0.2 0.2 0.2", "d 1", "illum 2"]
        if tex.get("albedo"):
            mtl.append("map_Kd " + tex["albedo"])
        if tex.get("normal"):
            mtl.append("map_Bump -bm 1 " + tex["normal"])
    with open(mtl_path, "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(mtl))
        f.write("\n")
    return mat_order


# ---------------------------------------------------------------- images
def _open_rgb(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (0, 0, 0))
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def _resize(im, size):
    if im.size != size:
        return im.resize(size, Image.LANCZOS)
    return im


def build_textures(diff, nor, arm, alpha, outdir, base, mask_size=None,
                   rough=None, metal=None, ao=None):
    """Create Albedo / Normal / Mask files for one material. Returns dict of file names."""
    os.makedirs(outdir, exist_ok=True)
    out = {}
    albedo_name = base + "_Albedo"
    if diff:
        if alpha:
            dim = _open_rgb(diff)
            am = Image.open(alpha)
            if am.mode != "L":
                am = am.convert("L")
            am = _resize(am, dim.size)
            rgba = dim.convert("RGBA")
            rgba.putalpha(am)
            fn = albedo_name + ".png"
            rgba.save(os.path.join(outdir, fn), optimize=True)
        else:
            fn = albedo_name + ".jpg"
            shutil.copyfile(diff, os.path.join(outdir, fn))
        out["albedo"] = fn
    if nor:
        fn = base + "_Normal.jpg"
        shutil.copyfile(nor, os.path.join(outdir, fn))
        out["normal"] = fn
    # ---- packed mask: R=metallic, G=AO, B=roughness, A=smoothness
    size = None
    if arm:
        im = Image.open(arm).convert("RGB")
        size = im.size
        a = np.asarray(im, dtype=np.uint8)
        ao_c = a[:, :, 0]
        rough_c = a[:, :, 1]
        metal_c = a[:, :, 2]
    else:
        size = Image.open(diff).size if diff else (512, 512)
        rough_val = rough if isinstance(rough, (int, float)) and rough is not None else 0.6
        metal_val = metal if isinstance(metal, (int, float)) and metal is not None else 0.0
        rough_c = np.full((size[1], size[0]), max(0, min(255, int(rough_val * 255))), np.uint8)
        metal_c = np.full((size[1], size[0]), max(0, min(255, int(metal_val * 255))), np.uint8)
        if ao and isinstance(ao, str):
            ao_c = np.asarray(Image.open(ao).convert("L"), dtype=np.uint8)
            if ao_c.shape != rough_c.shape:
                ao_c = np.asarray(Image.fromarray(ao_c).resize((size[0], size[1]), Image.LANCZOS))
        else:
            ao_c = np.full((size[1], size[0]), 255, np.uint8)
    if mask_size and size[0] > mask_size:
        ao_c = np.asarray(Image.fromarray(ao_c).resize((mask_size, mask_size), Image.LANCZOS))
        rough_c = np.asarray(Image.fromarray(rough_c).resize((mask_size, mask_size), Image.LANCZOS))
        metal_c = np.asarray(Image.fromarray(metal_c).resize((mask_size, mask_size), Image.LANCZOS))
        size = (mask_size, mask_size)
    smooth = 255 - rough_c
    mask = np.dstack([metal_c, ao_c, rough_c, smooth]).astype(np.uint8)
    fn = base + "_Mask.png"
    Image.fromarray(mask, "RGBA").save(os.path.join(outdir, fn), optimize=True)
    out["mask"] = fn
    return out
