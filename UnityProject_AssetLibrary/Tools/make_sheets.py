"""Compose thumbnail contact sheets for the documentation."""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

THUMBS = os.path.join(lib.PROJ, "Thumbnails")
SHOTS = os.path.join(lib.PROJ, "Screenshots")
os.makedirs(SHOTS, exist_ok=True)

CAT_CN = {
    "Trees": "树木 Trees", "Plants": "花草 Plants", "PottedPlants": "盆栽 Potted Plants",
    "Rocks": "岩石 Rocks", "Lamps": "灯具 Lamps", "Props": "道具 Props",
    "Wood": "木材 Wood", "WoodFloor": "木地板 Wood Floor", "Planks": "木板 Planks",
    "Ground": "地面 Ground", "Grass": "草地 Grass", "Gravel": "砾石 Gravel",
    "Rock": "岩石 Rock", "Metal": "金属 Metal", "Bricks": "砖墙 Bricks",
    "Fabric": "织物 Fabric", "Concrete": "混凝土 Concrete", "Tiles": "瓷砖 Tiles",
    "Bark": "树皮 Bark", "Sand": "沙地 Sand", "Snow": "雪地 Snow", "HDRI": "天空 HDRI",
}


def font(size):
    for p in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:  # noqa: BLE001
                pass
    return ImageFont.load_default()


def sheet(items, title, out, cols=4, cell=320, label_h=30):
    if not items:
        return
    rows = (len(items) + cols - 1) // cols
    pad = 10
    head = 56
    W = cols * (cell + pad) + pad
    H = head + rows * (cell + label_h + pad) + pad
    bg = Image.new("RGB", (W, H), (24, 26, 30))
    d = ImageDraw.Draw(bg)
    d.text((pad, 12), title, font=font(26), fill=(240, 240, 245))
    f = font(15)
    for i, (label, path) in enumerate(items):
        c = i % cols
        r = i // cols
        x = pad + c * (cell + pad)
        y = head + r * (cell + label_h + pad)
        try:
            im = Image.open(path).convert("RGB")
        except Exception:  # noqa: BLE001
            continue
        im.thumbnail((cell, cell), Image.LANCZOS)
        tile = Image.new("RGB", (cell, cell), (32, 35, 40))
        tile.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2))
        bg.paste(tile, (x, y))
        d.text((x + 4, y + cell + 6), label[:44], font=f, fill=(200, 205, 215))
    bg.save(out, quality=92)
    print("sheet", os.path.basename(out), len(items), "items")


def main():
    data = lib.load_json(os.path.join(lib.DOCS, "asset_library.json"))
    files = os.listdir(THUMBS) if os.path.isdir(THUMBS) else []
    present = set(files)

    # models by category
    cats = {}
    for m in data["models"]:
        fn = "model_" + m["name"] + ".png"
        if fn in present:
            cats.setdefault(m["category"], []).append((m["name"], os.path.join(THUMBS, fn)))
    for cat, items in sorted(cats.items()):
        items.sort()
        sheet(items, CAT_CN.get(cat, cat), os.path.join(SHOTS, "models_%s.jpg" % cat))

    # materials by category
    mc = {}
    for m in data["materials"]:
        fn = "material_%s_%s.png" % (m["category"], m["name"])
        if fn in present:
            mc.setdefault(m["category"], []).append((m["name"], os.path.join(THUMBS, fn)))
    for cat, items in sorted(mc.items()):
        items.sort()
        sheet(items, CAT_CN.get(cat, cat), os.path.join(SHOTS, "materials_%s.jpg" % cat))

    hd = []
    for h in data["hdris"]:
        fn = "hdri_" + h["name"] + ".png"
        if fn in present:
            hd.append((h["name"], os.path.join(THUMBS, fn)))
    if hd:
        sheet(hd, CAT_CN["HDRI"], os.path.join(SHOTS, "hdris.jpg"), cols=3, cell=420)

    print("done", len(cats), "model sheets,", len(mc), "material sheets")


if __name__ == "__main__":
    main()
