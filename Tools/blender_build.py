"""Procedurally build a modern furniture / prop set in Blender and export OBJ.

Run:  blender --background --python blender_build.py
Output: <OUT>/<model>/<model>.obj + <OUT>/manifest.json
All units are meters, models sit on Z=0 in Blender, exported as Y-up OBJ.
"""
import bpy
import bmesh
import json
import math
import os
import shutil

OUT = r"C:\Users\PC GAMER\AppData\Local\Temp\assetlib\blender_out"

MATERIALS = {
    # key: (base color, roughness, metallic)
    "linen_cream":   ((0.87, 0.84, 0.78), 0.85, 0.0),
    "linen_gray":    ((0.52, 0.53, 0.55), 0.90, 0.0),
    "walnut":        ((0.21, 0.12, 0.07), 0.45, 0.0),
    "oak":           ((0.56, 0.40, 0.24), 0.50, 0.0),
    "black_metal":   ((0.035, 0.035, 0.04), 0.35, 0.9),
    "brushed_steel": ((0.62, 0.63, 0.66), 0.28, 1.0),
    "concrete":      ((0.55, 0.54, 0.52), 0.85, 0.0),
    "ceramic_white": ((0.90, 0.90, 0.88), 0.18, 0.0),
    "brass":         ((0.76, 0.58, 0.28), 0.30, 1.0),
    "canvas_art":    ((0.93, 0.91, 0.87), 0.90, 0.0),
    "rug_fabric":    ((0.46, 0.44, 0.42), 0.95, 0.0),
    "soil":          ((0.09, 0.07, 0.05), 1.00, 0.0),
    "lamp_shade":    ((0.94, 0.90, 0.82), 0.80, 0.0),
    "bulb_warm":     ((1.00, 0.93, 0.80), 0.30, 0.0),
}

_mats = {}
_parts = []


def reset():
    global _mats, _parts
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats = {}
    _parts = []


def mat(key):
    if key in _mats:
        return _mats[key]
    col, rough, metal = MATERIALS[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if key == "bulb_warm":
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.82, 0.55, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 8.0
    _mats[key] = m
    return m


def finish(ob, key, bevel=0.0, smooth=False, segments=3):
    if bevel > 0:
        b = ob.modifiers.new("bev", "BEVEL")
        b.width = bevel
        b.segments = segments
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(30)
    if smooth:
        for p in ob.data.polygons:
            p.use_smooth = True
        es = ob.modifiers.new("es", "EDGE_SPLIT")
        es.use_edge_angle = True
        es.split_angle = math.radians(40)
    ob.data.materials.append(mat(key))
    _parts.append(ob)
    return ob


def box(name, size, loc, key, rot=(0, 0, 0), bevel=0.0, smooth=False, segments=3):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0] / 2.0 * 2.0, size[1] / 2.0 * 2.0, size[2] / 2.0 * 2.0)
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, key, bevel, smooth, segments)


def cyl(name, radius, depth, loc, key, rot=(0, 0, 0), verts=48, bevel=0.0, smooth=True, radius2=None):
    if radius2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                            location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=radius, radius2=radius2,
                                        depth=depth, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    return finish(ob, key, bevel, smooth)


def torus(name, major, minor, loc, key, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     location=loc, rotation=rot,
                                     major_segments=48, minor_segments=12)
    ob = bpy.context.active_object
    ob.name = name
    return finish(ob, key, 0.0, True)


def sphere(name, radius, loc, key, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=radius, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, key, 0.0, True)


def lathe(name, profile, key, steps=48):
    """profile: [(radius, z), ...] rotated around Z."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0.0, z)) for r, z in profile]
    edges = []
    for i in range(len(verts) - 1):
        edges.append(bm.edges.new((verts[i], verts[i + 1])))
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1),
                   angle=math.radians(360), steps=steps, use_merge=True)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    return finish(ob, key, 0.0, True)


# ---------------------------------------------------------------- models
def modern_sofa():
    box("sofa_base", (2.10, 0.88, 0.18), (0, 0, 0.36), "walnut", bevel=0.03)
    for x in (-1.00, 1.00):
        for y in (-0.36, 0.36):
            cyl("leg", 0.028, 0.18, (x, y, 0.20), "black_metal", verts=24)
    for i, x in enumerate((-0.66, 0.0, 0.66)):
        box("seat_cushion_%d" % i, (0.64, 0.80, 0.16), (x, 0.02, 0.53), "linen_cream",
            bevel=0.055, smooth=True, segments=4)
    box("back_frame", (2.10, 0.16, 0.52), (0, -0.37, 0.66), "walnut", bevel=0.03)
    for i, x in enumerate((-0.66, 0.0, 0.66)):
        box("back_cushion_%d" % i, (0.62, 0.16, 0.46), (x, -0.27, 0.72), "linen_cream",
            bevel=0.06, smooth=True, segments=4)
    for x in (-1.00, 1.00):
        box("armrest", (0.14, 0.88, 0.34), (x, 0.0, 0.66), "linen_cream", bevel=0.05,
            smooth=True, segments=4)


def modern_armchair():
    box("chair_base", (0.92, 0.84, 0.16), (0, 0, 0.34), "walnut", bevel=0.03)
    for x in (-0.38, 0.38):
        for y in (-0.34, 0.34):
            cyl("leg", 0.025, 0.16, (x, y, 0.18), "black_metal", verts=24)
    box("seat", (0.78, 0.76, 0.16), (0, 0.02, 0.50), "linen_cream", bevel=0.06,
        smooth=True, segments=4)
    box("back", (0.92, 0.16, 0.48), (0, -0.35, 0.64), "walnut", bevel=0.03)
    box("back_cushion", (0.76, 0.16, 0.42), (0, -0.25, 0.70), "linen_cream", bevel=0.06,
        smooth=True, segments=4)
    for x in (-0.44, 0.44):
        box("armrest", (0.10, 0.84, 0.28), (x, 0.0, 0.62), "linen_cream", bevel=0.045,
            smooth=True, segments=4)


def modern_coffee_table():
    box("table_top", (1.20, 0.62, 0.055), (0, 0, 0.40), "walnut", bevel=0.012, smooth=True)
    for x in (-0.52, 0.52):
        for y in (-0.24, 0.24):
            cyl("leg", 0.022, 0.375, (x, y, 0.19), "black_metal", verts=32)
    box("lower_shelf", (1.04, 0.48, 0.025), (0, 0, 0.14), "black_metal", bevel=0.006)


def modern_tv_console():
    box("body", (1.80, 0.40, 0.38), (0, 0, 0.32), "walnut", bevel=0.012, smooth=True)
    for x in (-0.42, 0.42):
        box("door", (0.84, 0.012, 0.33), (x, -0.203, 0.32), "oak", bevel=0.004)
        cyl("handle", 0.012, 0.20, (x, -0.222, 0.32), "brass", rot=(0, math.radians(90), 0))
    for x in (-0.82, 0.82):
        for y in (-0.14, 0.14):
            cyl("leg", 0.02, 0.13, (x, y, 0.065), "black_metal", verts=24)
    box("top", (1.84, 0.42, 0.02), (0, 0, 0.52), "black_metal", bevel=0.005)


def modern_bookshelf():
    for x in (-0.45, 0.45):
        box("side", (0.04, 0.32, 1.80), (x, 0, 0.90), "walnut", bevel=0.006)
    box("back", (0.90, 0.02, 1.80), (0, 0.15, 0.90), "oak", bevel=0.004)
    for i, z in enumerate((0.06, 0.50, 0.94, 1.38, 1.78)):
        box("shelf_%d" % i, (0.86, 0.30, 0.035), (0, 0, z), "walnut", bevel=0.006)
    for i, z in enumerate((0.30, 0.74, 1.18, 1.58)):
        box("book_%d" % i, (0.16, 0.22, 0.22), (-0.18 + i * 0.10, 0.0, z), "linen_gray")


def modern_floor_lamp():
    cyl("base", 0.17, 0.025, (0, 0, 0.0125), "black_metal", bevel=0.006)
    cyl("stem", 0.014, 1.36, (0, 0, 0.70), "black_metal", verts=24)
    cyl("shade", 0.20, 0.30, (0, 0, 1.48), "lamp_shade", smooth=True, radius2=0.13)
    sphere("bulb", 0.045, (0, 0, 1.42), "bulb_warm")


def modern_table_lamp():
    cyl("base", 0.09, 0.20, (0, 0, 0.10), "ceramic_white", bevel=0.02, smooth=True)
    cyl("stem", 0.010, 0.26, (0, 0, 0.31), "brass", verts=24)
    cyl("shade", 0.11, 0.18, (0, 0, 0.49), "lamp_shade", smooth=True, radius2=0.075)
    sphere("bulb", 0.03, (0, 0, 0.45), "bulb_warm")


def modern_dining_chair():
    box("seat", (0.48, 0.48, 0.05), (0, 0, 0.45), "oak", bevel=0.02, smooth=True)
    box("back", (0.46, 0.05, 0.40), (0, -0.235, 0.66), "oak", bevel=0.015, smooth=True,
        rot=(math.radians(-6), 0, 0))
    for x in (-0.20, 0.20):
        for y in (-0.20, 0.20):
            cyl("leg", 0.019, 0.44, (x, y, 0.22), "oak", verts=16)
    for y in (-0.20, 0.20):
        box("stretcher", (0.40, 0.02, 0.02), (0, y, 0.18), "oak", bevel=0.004)


def modern_bar_stool():
    cyl("seat", 0.19, 0.06, (0, 0, 0.74), "linen_gray", bevel=0.02, smooth=True)
    for i in range(4):
        a = math.radians(45 + i * 90)
        x, y = math.cos(a) * 0.14, math.sin(a) * 0.14
        cyl("leg", 0.014, 0.72, (x * 0.75, y * 0.75, 0.36), "black_metal", verts=16,
            rot=(math.radians(6) * math.sin(a), math.radians(6) * math.cos(a), 0))
    torus("footrest", 0.15, 0.012, (0, 0, 0.26), "brass", rot=(math.radians(90), 0, 0))


def modern_side_table():
    cyl("top", 0.23, 0.035, (0, 0, 0.48), "walnut", bevel=0.01, smooth=True)
    for i in range(3):
        a = math.radians(i * 120)
        x, y = math.cos(a) * 0.15, math.sin(a) * 0.15
        cyl("leg", 0.012, 0.46, (x, y, 0.23), "black_metal", verts=16,
            rot=(math.radians(4) * math.sin(a), math.radians(4) * math.cos(a), 0))


def modern_planter():
    cyl("pot", 0.26, 0.52, (0, 0, 0.26), "concrete", bevel=0.015, smooth=True, radius2=0.30)
    cyl("soil", 0.275, 0.03, (0, 0, 0.50), "soil", smooth=True)


def modern_wall_clock():
    cyl("dial", 0.20, 0.035, (0, 0, 0), "ceramic_white", rot=(math.radians(90), 0, 0),
        bevel=0.006, smooth=True)
    torus("rim", 0.20, 0.014, (0, 0.005, 0), "brass", rot=(math.radians(90), 0, 0))
    box("hand_h", (0.012, 0.008, 0.11), (0, -0.026, 0.045), "black_metal")
    box("hand_m", (0.010, 0.008, 0.16), (0.05, -0.028, 0.0), "black_metal",
        rot=(0, 0, math.radians(30)))


def modern_vase():
    lathe("vase", [(0.001, 0), (0.10, 0.005), (0.13, 0.06), (0.15, 0.18),
                   (0.11, 0.34), (0.075, 0.40), (0.085, 0.44), (0.08, 0.45)],
          "ceramic_white")


def modern_rug():
    box("rug", (2.40, 1.60, 0.018), (0, 0, 0.009), "rug_fabric", bevel=0.008)


def modern_picture_frame():
    w, h, t = 0.72, 0.92, 0.04
    box("canvas", (w - 0.08, t * 0.5, h - 0.08), (0, 0.0, 0), "canvas_art")
    box("frame_top", (w, t, 0.045), (0, -0.01, h / 2 - 0.02), "walnut", bevel=0.005)
    box("frame_bottom", (w, t, 0.045), (0, -0.01, -h / 2 + 0.02), "walnut", bevel=0.005)
    box("frame_left", (0.045, t, h), (-w / 2 + 0.02, -0.01, 0), "walnut", bevel=0.005)
    box("frame_right", (0.045, t, h), (w / 2 - 0.02, -0.01, 0), "walnut", bevel=0.005)


def modern_shelf_wall():
    box("board", (1.10, 0.24, 0.04), (0, 0, 0), "walnut", bevel=0.006)
    for x in (-0.45, 0.45):
        box("bracket", (0.03, 0.20, 0.14), (x, 0.0, -0.09), "black_metal", bevel=0.004)
    box("book_a", (0.16, 0.18, 0.20), (-0.28, 0, 0.12), "linen_gray")
    cyl("vase_small", 0.05, 0.16, (0.30, 0, 0.10), "ceramic_white", bevel=0.008, smooth=True)


MODELS = {
    "modern_sofa": (modern_sofa, "Furniture"),
    "modern_armchair": (modern_armchair, "Furniture"),
    "modern_coffee_table": (modern_coffee_table, "Furniture"),
    "modern_tv_console": (modern_tv_console, "Furniture"),
    "modern_bookshelf": (modern_bookshelf, "Furniture"),
    "modern_dining_chair": (modern_dining_chair, "Furniture"),
    "modern_bar_stool": (modern_bar_stool, "Furniture"),
    "modern_side_table": (modern_side_table, "Furniture"),
    "modern_floor_lamp": (modern_floor_lamp, "Lamps"),
    "modern_table_lamp": (modern_table_lamp, "Lamps"),
    "modern_planter": (modern_planter, "Decor"),
    "modern_wall_clock": (modern_wall_clock, "Decor"),
    "modern_vase": (modern_vase, "Decor"),
    "modern_rug": (modern_rug, "Decor"),
    "modern_picture_frame": (modern_picture_frame, "Decor"),
    "modern_shelf_wall": (modern_shelf_wall, "Decor"),
}


def tri_count(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    ev.to_mesh_clear()
    return n


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for name, (builder, category) in MODELS.items():
        reset()
        builder()
        tris = 0
        keys = set()
        for ob in _parts:
            tris += tri_count(ob)
            for slot in ob.material_slots:
                if slot.material:
                    keys.add(slot.material.name)
        outdir = os.path.join(OUT, name)
        if os.path.isdir(outdir):
            shutil.rmtree(outdir)
        os.makedirs(outdir)
        obj_path = os.path.join(outdir, name + ".obj")
        bpy.ops.object.select_all(action="DESELECT")
        for ob in _parts:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = _parts[0]
        bpy.ops.wm.obj_export(filepath=obj_path, export_selected_objects=True,
                              apply_modifiers=True, export_materials=True,
                              export_uv=True, export_normals=True,
                              forward_axis="NEGATIVE_Z", up_axis="Y")
        manifest.append({
            "name": name,
            "category": category,
            "tris": int(tris),
            "materials": sorted(keys),
        })
        print("BUILT %-24s tris=%d mats=%s" % (name, tris, ",".join(sorted(keys))))
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    print("DONE", len(manifest), "models ->", OUT)


if __name__ == "__main__":
    main()
