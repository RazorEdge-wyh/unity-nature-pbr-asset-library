"""Procedurally build a high-detail modern furniture / prop set in Blender and export OBJ.

Run:  blender --background --python blender_build.py
Output: <OUT>/<model>/<model>.obj + <OUT>/manifest.json
Units: meters. Models sit on Z=0 in Blender, exported as Y-up OBJ.
"""
import bpy
import bmesh
import json
import math
import os
import shutil

OUT = r"C:\Users\PC GAMER\AppData\Local\Temp\assetlib\blender_out"

# key: (base color, roughness, metallic)
MATERIALS = {
    "linen_cream":   ((0.87, 0.84, 0.78), 0.85, 0.0),
    "linen_gray":    ((0.52, 0.53, 0.55), 0.90, 0.0),
    "dark_fabric":   ((0.16, 0.16, 0.18), 0.92, 0.0),
    "walnut":        ((0.21, 0.12, 0.07), 0.42, 0.0),
    "oak":           ((0.56, 0.40, 0.24), 0.48, 0.0),
    "black_metal":   ((0.035, 0.035, 0.04), 0.32, 0.9),
    "brushed_steel": ((0.62, 0.63, 0.66), 0.26, 1.0),
    "brass":         ((0.78, 0.60, 0.28), 0.26, 1.0),
    "concrete":      ((0.55, 0.54, 0.52), 0.85, 0.0),
    "marble_white":  ((0.88, 0.88, 0.86), 0.12, 0.0),
    "ceramic_white": ((0.90, 0.90, 0.88), 0.16, 0.0),
    "canvas_art":    ((0.93, 0.91, 0.87), 0.90, 0.0),
    "book_teal":     ((0.10, 0.26, 0.29), 0.72, 0.0),
    "book_terra":    ((0.55, 0.24, 0.16), 0.78, 0.0),
    "rug_fabric":    ((0.46, 0.44, 0.42), 0.95, 0.0),
    "soil":          ((0.09, 0.07, 0.05), 1.00, 0.0),
    "lamp_shade":    ((0.95, 0.91, 0.84), 0.78, 0.0),
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
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.80, 0.52, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 10.0
    _mats[key] = m
    return m


def finish(ob, key, bevel=0.0, smooth=False, segments=4):
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
        es.split_angle = math.radians(38)
    ob.data.materials.append(mat(key))
    _parts.append(ob)
    return ob


def box(name, size, loc, key, rot=(0, 0, 0), bevel=0.0, smooth=False, segments=4):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, key, bevel, smooth, segments)


def cyl(name, r1, depth, loc, key, rot=(0, 0, 0), verts=64, bevel=0.0, smooth=True, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r1, depth=depth,
                                            location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                        depth=depth, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    return finish(ob, key, bevel, smooth)


def torus(name, major, minor, loc, key, rot=(0, 0, 0), mseg=64, nseg=12):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     location=loc, rotation=rot,
                                     major_segments=mseg, minor_segments=nseg)
    ob = bpy.context.active_object
    ob.name = name
    return finish(ob, key, 0.0, True)


def sphere(name, radius, loc, key, scale=(1, 1, 1), seg=32, ring=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ring, radius=radius, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, key, 0.0, True)


def lathe(name, profile, key, steps=64):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0.0, z)) for r, z in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1),
                   angle=math.radians(360), steps=steps, use_merge=True)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    return finish(ob, key, 0.0, True)


def tapered_leg(name, x, y, z0, z1, r_top, r_bottom, key="black_metal"):
    h = z1 - z0
    return cyl(name, r_bottom, h, (x, y, z0 + h / 2), key, r2=r_top, verts=24)


# ---------------------------------------------------------------- furniture
def modern_sofa():
    # plinth + slatted wooden base
    box("base", (2.24, 0.92, 0.24), (0, 0, 0.30), "walnut", bevel=0.02)
    for i in range(9):
        box("slat_%d" % i, (0.02, 0.86, 0.10), (-0.94 + i * 0.235, 0.0, 0.44), "oak", bevel=0.003)
    for x in (-1.02, -0.34, 0.34, 1.02):
        tapered_leg("leg", x, 0.36, 0.0, 0.20, 0.022, 0.016)
        tapered_leg("leg", x, -0.36, 0.0, 0.20, 0.022, 0.016)
    # seat cushions with piping + tufting
    for i, x in enumerate((-0.72, 0.0, 0.72)):
        box("seat_%d" % i, (0.68, 0.84, 0.17), (x, 0.02, 0.50), "linen_cream",
            bevel=0.06, smooth=True)
        for tx in (-0.18, 0.18):
            for ty in (-0.22, 0.0, 0.22):
                sphere("tuft", 0.022, (x + tx, ty, 0.585), "linen_cream", scale=(1, 1, 0.55))
    # back frame + cushions
    box("back_frame", (2.24, 0.14, 0.58), (0, -0.39, 0.62), "walnut", bevel=0.02)
    for i, x in enumerate((-0.72, 0.0, 0.72)):
        box("back_cushion_%d" % i, (0.66, 0.18, 0.50), (x, -0.28, 0.76), "linen_cream",
            bevel=0.07, smooth=True)
    for x in (-1.06, 1.06):
        box("armrest", (0.15, 0.92, 0.36), (x, 0.0, 0.68), "linen_cream", bevel=0.06, smooth=True)
        box("armrest_cap", (0.16, 0.94, 0.03), (x, 0.0, 0.865), "walnut", bevel=0.008)
    # throw pillows
    box("pillow_a", (0.36, 0.14, 0.36), (-0.88, -0.20, 0.72), "dark_fabric",
        rot=(0, 0, 0), bevel=0.07, smooth=True)
    box("pillow_b", (0.34, 0.13, 0.34), (0.90, -0.20, 0.72), "book_teal",
        rot=(0, math.radians(8), math.radians(-6)), bevel=0.07, smooth=True)


def modern_armchair():
    box("base", (1.00, 0.86, 0.20), (0, 0, 0.31), "walnut", bevel=0.02)
    box("seat", (0.84, 0.78, 0.17), (0, 0.02, 0.485), "linen_cream", bevel=0.065, smooth=True)
    for x in (-0.42, 0.42):
        tapered_leg("leg", x, 0.32, 0.0, 0.21, 0.02, 0.015)
        tapered_leg("leg", x, -0.32, 0.0, 0.21, 0.02, 0.015)
    box("back", (1.00, 0.15, 0.56), (0, -0.36, 0.62), "walnut", bevel=0.02)
    box("back_cushion", (0.84, 0.18, 0.48), (0, -0.25, 0.75), "linen_cream", bevel=0.07, smooth=True)
    for x in (-0.46, 0.46):
        box("arm", (0.12, 0.86, 0.30), (x, 0.0, 0.62), "linen_cream", bevel=0.055, smooth=True)
        box("arm_cap", (0.13, 0.88, 0.025), (x, 0.0, 0.775), "walnut", bevel=0.006)
    sphere("button", 0.02, (0, -0.15, 0.995), "linen_cream", scale=(1, 1, 0.5))


def modern_coffee_table():
    box("top", (1.30, 0.68, 0.06), (0, 0, 0.41), "walnut", bevel=0.014, smooth=True)
    box("top_edge", (1.34, 0.72, 0.018), (0, 0, 0.375), "oak", bevel=0.006)
    for x in (-0.56, 0.56):
        for y in (-0.26, 0.26):
            tapered_leg("leg", x, y, 0.0, 0.37, 0.024, 0.014)
            cyl("cap", 0.026, 0.02, (x, y, 0.01), "brass", verts=24)
    box("shelf", (1.10, 0.52, 0.025), (0, 0, 0.13), "black_metal", bevel=0.005)
    box("tray", (0.34, 0.24, 0.02), (0.30, 0.02, 0.455), "brass", bevel=0.008)
    box("book", (0.26, 0.19, 0.035), (-0.32, 0.05, 0.462), "book_terra", bevel=0.004)
    cyl("vase_small", 0.045, 0.14, (-0.32, -0.16, 0.525), "ceramic_white", bevel=0.006)


def modern_tv_console():
    box("body", (1.86, 0.42, 0.40), (0, 0, 0.34), "walnut", bevel=0.012, smooth=True)
    for x in (-0.44, 0.44):
        box("door", (0.86, 0.016, 0.35), (x, -0.213, 0.34), "oak", bevel=0.005)
        box("door_panel", (0.74, 0.008, 0.26), (x, -0.222, 0.34), "walnut", bevel=0.004)
        cyl("handle", 0.010, 0.18, (x + 0.36, -0.232, 0.34), "brass",
            rot=(0, math.radians(90), 0), verts=20)
    box("divider", (0.02, 0.40, 0.36), (0, 0, 0.34), "walnut")
    for x in (-0.84, 0.84):
        for y in (-0.15, 0.15):
            tapered_leg("leg", x, y, 0.0, 0.14, 0.018, 0.012)
    box("top", (1.92, 0.46, 0.025), (0, 0, 0.565), "black_metal", bevel=0.006)
    for i, x in enumerate((-0.30, -0.18, -0.06)):
        box("book_%d" % i, (0.05, 0.22, 0.26), (x, 0.02, 0.71), "book_teal", bevel=0.004)


def modern_bookshelf():
    for x in (-0.47, 0.47):
        box("side", (0.045, 0.34, 1.90), (x, 0, 0.95), "walnut", bevel=0.006)
    box("back", (0.90, 0.018, 1.90), (0, 0.16, 0.95), "oak", bevel=0.003)
    for i, z in enumerate((0.06, 0.52, 0.98, 1.44, 1.86)):
        box("shelf_%d" % i, (0.90, 0.32, 0.04), (0, 0, z), "walnut", bevel=0.006)
    heights = [0.26, 0.22, 0.30, 0.24, 0.20, 0.28, 0.23, 0.26, 0.21, 0.29, 0.24, 0.22]
    mats = ["book_teal", "book_terra", "linen_gray", "walnut", "oak"]
    x = -0.36
    idx = 0
    for shelf_z in (0.60, 1.06, 1.52, 1.94):
        x = -0.36
        for j in range(3):
            h = heights[idx % len(heights)]
            box("book_%d" % idx, (0.09, 0.24, h), (x, 0.0, shelf_z + h / 2), mats[idx % len(mats)],
                bevel=0.004)
            x += 0.11
            idx += 1
        box("box_%d" % j, (0.20, 0.26, 0.14), (0.20, 0.0, shelf_z + 0.07), "concrete", bevel=0.008)


def modern_dining_chair():
    cyl("seat", 0.245, 0.055, (0, 0, 0.46), "oak", bevel=0.02, smooth=True)
    for i in range(4):
        a = math.radians(45 + i * 90)
        x, y = math.cos(a) * 0.18, math.sin(a) * 0.18
        tapered_leg("leg", x, y, 0.0, 0.44, 0.018, 0.013, key="oak")
    for i, z in enumerate((0.62, 0.72, 0.82)):
        box("back_slat_%d" % i, (0.40 - i * 0.03, 0.035, 0.045), (0, -0.235, z), "oak",
            bevel=0.01, smooth=True, rot=(math.radians(-7), 0, 0))
    for x in (-0.18, 0.18):
        cyl("post", 0.014, 0.42, (x, -0.235, 0.66), "oak", rot=(math.radians(-7), 0, 0), verts=16)


def modern_bar_stool():
    box("seat_frame", (0.40, 0.40, 0.05), (0, 0, 0.72), "black_metal", bevel=0.01)
    cyl("seat", 0.19, 0.075, (0, 0, 0.775), "linen_gray", bevel=0.025, smooth=True)
    for i in range(4):
        a = math.radians(45 + i * 90)
        x, y = math.cos(a) * 0.16, math.sin(a) * 0.16
        cyl("leg", 0.014, 0.72, (x * 0.8, y * 0.8, 0.36), "black_metal", verts=20,
            rot=(math.radians(7) * math.sin(a), math.radians(7) * math.cos(a), 0))
    torus("footrest", 0.155, 0.011, (0, 0, 0.26), "brass")
    torus("stretcher", 0.10, 0.008, (0, 0, 0.12), "black_metal")


def modern_side_table():
    cyl("top", 0.24, 0.04, (0, 0, 0.50), "marble_white", bevel=0.012, smooth=True)
    cyl("apron", 0.20, 0.05, (0, 0, 0.465), "walnut", smooth=True)
    for i in range(3):
        a = math.radians(i * 120 + 20)
        x, y = math.cos(a) * 0.15, math.sin(a) * 0.15
        tapered_leg("leg", x, y, 0.0, 0.46, 0.016, 0.011)
    torus("ring", 0.10, 0.008, (0, 0, 0.14), "brass")


def modern_desk():
    box("top", (1.40, 0.68, 0.045), (0, 0, 0.755), "walnut", bevel=0.01, smooth=True)
    box("back_apron", (1.30, 0.03, 0.12), (0, 0.30, 0.69), "walnut", bevel=0.004)
    for x in (-0.64, 0.64):
        box("leg_frame", (0.06, 0.60, 0.72), (x, 0, 0.38), "black_metal", bevel=0.008)
        box("foot", (0.08, 0.62, 0.02), (x, 0, 0.01), "black_metal", bevel=0.004)
    # drawer unit
    box("drawer_body", (0.42, 0.56, 0.42), (0.42, 0.0, 0.52), "oak", bevel=0.008)
    for i, z in enumerate((0.40, 0.64)):
        box("drawer_front_%d" % i, (0.40, 0.02, 0.19), (0.42, -0.29, z), "walnut", bevel=0.004)
        box("drawer_handle_%d" % i, (0.16, 0.012, 0.015), (0.42, -0.305, z + 0.07), "brass", bevel=0.003)
    box("monitor", (0.52, 0.03, 0.30), (0.0, 0.24, 1.05), "black_metal", bevel=0.006)
    cyl("monitor_stand", 0.02, 0.24, (0, 0.24, 0.905), "black_metal", verts=20)
    box("keyboard", (0.34, 0.11, 0.018), (0.0, 0.11, 0.79), "black_metal", bevel=0.004)
    cyl("mug", 0.045, 0.10, (-0.34, 0.12, 0.83), "ceramic_white", bevel=0.006, smooth=True)


def modern_sideboard():
    box("body", (1.60, 0.45, 0.60), (0, 0, 0.45), "walnut", bevel=0.012, smooth=True)
    for x in (-0.40, 0.40):
        box("door", (0.76, 0.016, 0.52), (x, -0.23, 0.45), "oak", bevel=0.005)
        box("door_panel", (0.64, 0.008, 0.42), (x, -0.24, 0.45), "walnut", bevel=0.004)
        cyl("handle", 0.008, 0.16, (x + 0.30, -0.25, 0.45), "brass",
            rot=(0, math.radians(90), 0), verts=16)
    box("top", (1.64, 0.47, 0.03), (0, 0, 0.765), "marble_white", bevel=0.006, smooth=True)
    for x in (-0.70, 0.70):
        for y in (-0.16, 0.16):
            tapered_leg("leg", x, y, 0.0, 0.15, 0.018, 0.012)
    cyl("vase_a", 0.07, 0.26, (-0.48, 0.0, 0.90), "ceramic_white", bevel=0.008, smooth=True)
    box("book_stack", (0.24, 0.17, 0.09), (0.44, 0.0, 0.80), "book_teal", bevel=0.005)


def modern_wardrobe():
    box("body", (1.20, 0.60, 1.95), (0, 0, 1.05), "walnut", bevel=0.012, smooth=True)
    for x in (-0.30, 0.30):
        box("door", (0.56, 0.02, 1.85), (x, -0.305, 1.05), "oak", bevel=0.006)
        box("door_panel", (0.46, 0.006, 1.70), (x, -0.318, 1.05), "walnut", bevel=0.005)
        cyl("handle", 0.010, 0.55, (x + (0.22 if x < 0 else -0.22), -0.325, 1.05), "brass",
            verts=20)
    for x in (-0.52, 0.52):
        for y in (-0.24, 0.24):
            tapered_leg("leg", x, y, 0.0, 0.075, 0.02, 0.013)
    box("top", (1.24, 0.63, 0.02), (0, 0, 2.035), "black_metal", bevel=0.004)


# ---------------------------------------------------------------- lamps
def modern_floor_lamp():
    cyl("base", 0.16, 0.03, (0, 0, 0.015), "marble_white", bevel=0.008, smooth=True)
    cyl("base_ring", 0.05, 0.05, (0, 0, 0.045), "brass", verts=32)
    cyl("stem", 0.012, 1.30, (0, 0, 0.70), "brass", verts=24)
    cyl("shade_inner", 0.185, 0.28, (0, 0, 1.42), "lamp_shade", smooth=True)
    cyl("shade", 0.21, 0.30, (0, 0, 1.43), "lamp_shade", smooth=True, r2=0.17)
    torus("shade_rim", 0.205, 0.006, (0, 0, 1.285), "brass")
    sphere("bulb", 0.04, (0, 0, 1.36), "bulb_warm")
    cyl("cap", 0.02, 0.03, (0, 0, 1.59), "black_metal", verts=20)


def modern_table_lamp():
    lathe("base", [(0.001, 0), (0.09, 0.005), (0.115, 0.06), (0.10, 0.16),
                   (0.065, 0.22), (0.05, 0.25)], "ceramic_white")
    cyl("neck", 0.012, 0.10, (0, 0, 0.29), "brass", verts=20)
    cyl("shade", 0.115, 0.17, (0, 0, 0.40), "lamp_shade", smooth=True, r2=0.085)
    sphere("bulb", 0.028, (0, 0, 0.38), "bulb_warm")
    torus("shade_rim", 0.112, 0.004, (0, 0, 0.315), "brass")


def modern_pendant_lamp():
    cyl("ceiling_cap", 0.06, 0.02, (0, 0, 0.0), "brass", smooth=True)
    cyl("cord", 0.004, 0.75, (0, 0, 0.38), "black_metal", verts=12)
    cyl("shade", 0.24, 0.20, (0, 0, 0.70), "brass", smooth=True, r2=0.20)
    cyl("shade_inner", 0.225, 0.19, (0, 0, 0.695), "lamp_shade", smooth=True, r2=0.19)
    sphere("bulb", 0.04, (0, 0, 0.66), "bulb_warm")


# ---------------------------------------------------------------- decor
def modern_planter():
    cyl("pot", 0.20, 0.46, (0, 0, 0.25), "concrete", bevel=0.012, smooth=False,
        verts=8, r2=0.245)
    cyl("rim", 0.245, 0.035, (0, 0, 0.48), "concrete", smooth=False, verts=8)
    cyl("soil", 0.225, 0.02, (0, 0, 0.475), "soil", smooth=True)
    for i in range(7):
        a = math.radians(i * 51)
        sphere("pebble", 0.02, (math.cos(a) * 0.14, math.sin(a) * 0.14, 0.49), "marble_white",
               scale=(1, 1, 0.6), seg=12, ring=8)


def modern_wall_clock():
    cyl("dial", 0.21, 0.04, (0, 0, 0), "ceramic_white", rot=(math.radians(90), 0, 0),
        bevel=0.006, smooth=True)
    torus("rim", 0.21, 0.013, (0, 0.004, 0), "brass", rot=(math.radians(90), 0, 0))
    for i in range(12):
        a = math.radians(i * 30)
        x, y = math.sin(a) * 0.17, math.cos(a) * 0.17
        box("tick_%d" % i, (0.008, 0.004, 0.032 if i % 3 == 0 else 0.02),
            (x, -0.024, y), "black_metal", rot=(0, 0, -a))
    box("hand_hour", (0.012, 0.004, 0.10), (0.035, -0.028, 0.05), "black_metal",
        rot=(math.radians(-25), 0, 0))
    box("hand_min", (0.009, 0.004, 0.15), (-0.045, -0.030, 0.0), "black_metal",
        rot=(0, math.radians(40), 0))
    cyl("pin", 0.012, 0.01, (0, -0.033, 0), "brass", rot=(math.radians(90), 0, 0), verts=16)


def modern_vase():
    lathe("vase", [(0.001, 0), (0.09, 0.004), (0.12, 0.05), (0.145, 0.14),
                   (0.14, 0.24), (0.10, 0.34), (0.065, 0.40), (0.075, 0.44),
                   (0.072, 0.455)], "ceramic_white")


def modern_rug():
    box("rug", (2.50, 1.70, 0.016), (0, 0, 0.008), "rug_fabric", bevel=0.006)
    box("rug_border", (2.26, 1.46, 0.006), (0, 0, 0.019), "linen_gray", bevel=0.003)
    for y in (-0.87, 0.87):
        for i in range(18):
            box("fringe_%d_%d" % (int(y * 10), i), (0.012, 0.10, 0.008),
                (-1.10 + i * 0.13, y, 0.005), "linen_cream", bevel=0.002)


def modern_picture_frame():
    w, h, t = 0.78, 0.98, 0.045
    box("canvas", (w - 0.10, t * 0.4, h - 0.10), (0, 0.0, 0), "canvas_art")
    box("mat", (w - 0.06, t * 0.5, h - 0.06), (0, -0.004, 0), "ceramic_white")
    box("frame_top", (w, t, 0.05), (0, -0.012, h / 2 - 0.025), "walnut", bevel=0.006)
    box("frame_bottom", (w, t, 0.05), (0, -0.012, -h / 2 + 0.025), "walnut", bevel=0.006)
    box("frame_left", (0.05, t, h), (-w / 2 + 0.025, -0.012, 0), "walnut", bevel=0.006)
    box("frame_right", (0.05, t, h), (w / 2 - 0.025, -0.012, 0), "walnut", bevel=0.006)


def modern_wall_art():
    for i, x in enumerate((-1.05, 0.0, 1.05)):
        box("frame_%d" % i, (0.86, 0.05, 0.66), (x, 0, 0), "walnut", bevel=0.006)
        box("canvas_%d" % i, (0.78, 0.02, 0.58), (x, -0.02, 0), "canvas_art")
        box("bar_%d" % i, (0.30, 0.01, 0.34), (x - 0.10, -0.032, 0.05),
            "book_teal" if i == 0 else ("book_terra" if i == 1 else "dark_fabric"),
            bevel=0.004)


def modern_shelf_wall():
    box("board", (1.20, 0.26, 0.045), (0, 0, 0), "walnut", bevel=0.008)
    for x in (-0.50, 0.50):
        box("bracket", (0.03, 0.22, 0.16), (x, 0.0, -0.10), "black_metal", bevel=0.004)
    box("book_a", (0.14, 0.19, 0.22), (-0.34, 0, 0.13), "book_teal", bevel=0.004)
    box("book_b", (0.12, 0.18, 0.20), (-0.20, 0, 0.12), "book_terra", bevel=0.004)
    cyl("pot", 0.06, 0.11, (0.34, 0, 0.078), "ceramic_white", bevel=0.01, smooth=True)
    sphere("leaf", 0.07, (0.34, 0, 0.20), "book_teal", scale=(0.7, 0.7, 1.0))


def modern_floor_mirror():
    cyl("base", 0.20, 0.025, (0, 0, 0.0125), "marble_white", bevel=0.006, smooth=True)
    for x in (-0.10, 0.10):
        cyl("post", 0.012, 1.75, (x, 0, 0.89), "brass", verts=20)
    box("frame", (0.62, 0.03, 1.70), (0, 0, 0.92), "brass", bevel=0.008, smooth=True)
    box("glass", (0.54, 0.01, 1.62), (0, -0.02, 0.92), "brushed_steel", bevel=0.004)


MODELS = {
    "modern_sofa": (modern_sofa, "Furniture"),
    "modern_armchair": (modern_armchair, "Furniture"),
    "modern_coffee_table": (modern_coffee_table, "Furniture"),
    "modern_tv_console": (modern_tv_console, "Furniture"),
    "modern_bookshelf": (modern_bookshelf, "Furniture"),
    "modern_dining_chair": (modern_dining_chair, "Furniture"),
    "modern_bar_stool": (modern_bar_stool, "Furniture"),
    "modern_side_table": (modern_side_table, "Furniture"),
    "modern_desk": (modern_desk, "Furniture"),
    "modern_sideboard": (modern_sideboard, "Furniture"),
    "modern_wardrobe": (modern_wardrobe, "Furniture"),
    "modern_floor_lamp": (modern_floor_lamp, "Lamps"),
    "modern_table_lamp": (modern_table_lamp, "Lamps"),
    "modern_pendant_lamp": (modern_pendant_lamp, "Lamps"),
    "modern_planter": (modern_planter, "Decor"),
    "modern_wall_clock": (modern_wall_clock, "Decor"),
    "modern_vase": (modern_vase, "Decor"),
    "modern_rug": (modern_rug, "Decor"),
    "modern_picture_frame": (modern_picture_frame, "Decor"),
    "modern_wall_art": (modern_wall_art, "Decor"),
    "modern_shelf_wall": (modern_shelf_wall, "Decor"),
    "modern_floor_mirror": (modern_floor_mirror, "Decor"),
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
    total = 0
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
        total += tris
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
        manifest.append({"name": name, "category": category, "tris": int(tris),
                         "materials": sorted(keys)})
        print("BUILT %-24s tris=%6d mats=%s" % (name, tris, ",".join(sorted(keys))))
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    print("DONE", len(manifest), "models,", total, "tris ->", OUT)


if __name__ == "__main__":
    main()
