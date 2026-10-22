"""Generate README / guide / credits from the built manifest."""
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

CAT_CN = {
    "Trees": "树木", "Plants": "花草植物", "PottedPlants": "盆栽 / 花箱",
    "Rocks": "岩石", "Lamps": "灯具", "Props": "道具 / 树桩",
    "Wood": "木材", "WoodFloor": "木地板", "Planks": "木板", "Ground": "地面",
    "Grass": "草地", "Gravel": "砾石", "Rock": "岩面", "Metal": "金属",
    "Bricks": "砖墙", "Fabric": "织物", "Concrete": "混凝土", "Tiles": "瓷砖",
    "Bark": "树皮", "Sand": "沙地", "Snow": "雪地", "HDRI": "HDRI 天空",
}


def cn(cat):
    return CAT_CN.get(cat, cat)


def main():
    data = lib.load_json(os.path.join(lib.DOCS, "asset_library.json"))
    models = data["models"]
    materials = data["materials"]
    hdris = data["hdris"]
    n_total = len(models) + len(materials) + len(hdris)

    mcats = {}
    for m in models:
        mcats.setdefault(m["category"], []).append(m)
    matcats = {}
    for m in materials:
        matcats.setdefault(m["category"], []).append(m)

    tri_total = sum(m["tris"] for m in models)
    tri_src = sum(m["trisOriginal"] for m in models)
    tri_min = min(m["tris"] for m in models) if models else 0
    tri_max = max(m["tris"] for m in models) if models else 0

    model_rows = "\n".join(
        "| %s | %d | %s | %s | %s |" % (
            cn(c), len(v), ", ".join("%s(%d 面)" % (x["name"], x["tris"]) for x in sorted(v, key=lambda a: a["name"])[:6])
            + (" …" if len(v) > 6 else ""),
            "树木/植被" if c in ("Trees", "Plants") else "道具/环境",
            "CC0")
        for c, v in sorted(mcats.items(), key=lambda kv: -len(kv[1])))

    mat_rows = "\n".join(
        "| %s | %d | %d px | %s |" % (cn(c), len(v), v[0]["resolution"],
                                      ", ".join(x["name"] for x in sorted(v, key=lambda a: a["name"])))
        for c, v in sorted(matcats.items(), key=lambda kv: -len(kv[1])))

    hdri_list = ", ".join(h["name"] for h in sorted(hdris, key=lambda x: x["name"]))

    def cat_sheet(prefix, cat):
        return "Screenshots/%s_%s.jpg" % (prefix, cat)

    preview_lines = []
    for c in sorted(mcats):
        preview_lines.append("### %s（%d）\n\n![%s](%s)\n" % (cn(c), len(mcats[c]), cn(c), cat_sheet("models", c)))
    for c in sorted(matcats):
        preview_lines.append("### 材质 · %s（%d）\n\n![材质 %s](%s)\n" % (cn(c), len(matcats[c]), cn(c), cat_sheet("materials", c)))
    preview_lines.append("### HDRI 天空（%d）\n\n![HDRI](Screenshots/hdris.jpg)\n" % len(hdris))
    previews = "\n".join(preview_lines)

    readme = f"""# Unity 自然 / 室内 PBR 素材库 · v1.0

> **{n_total} 个可直接用于 Unity 的素材**：{len(models)} 个 3D 模型（花 / 草 / 树 / 岩石 / 灯具 / 盆栽 / 道具）
> ＋ {len(materials)} 套 PBR 材质（木材、地面、草地、砾石、岩石、金属、砖、织物、混凝土、瓷砖、树皮、沙、雪）
> ＋ {len(hdris)} 张 HDRI 天空。
>
> 全部素材为 **CC0 1.0 公共领域授权**，可商用、可修改、无需署名（仍建议保留 CREDITS.md）。
> 出厂工程使用 Unity **2022.3 LTS + 内置渲染管线 + 线性色彩空间**，已生成材质、预制体、碰撞体、灯具灯光、天空盒与演示场景。

---

## 一、快速开始

有两条路，任选其一：

**A. 直接打开完整工程（推荐，含演示场景与所有预览图）**

1. 用 Unity Hub 打开 `UnityProject_AssetLibrary/`（Unity 2022.3.x）。
2. 打开 `Assets/AssetLibrary/Scenes/Showcase.unity`，按 Play。
3. 素材在 `Assets/AssetLibrary/` 下：`Models/`、`Materials/`、`Prefabs/`、`Environment/`、`Shaders/`。

**B. 导入到你自己的项目**

1. 双击 `UnityPackage/AssetLibrary_v1.0.unitypackage`（或 Assets → Import Package → Custom Package）。
2. 包内自带 `AssetLibraryPostprocessor`，会自动按命名规则设置纹理导入参数（法线贴图 / 线性遮罩 / HDR）。
3. 直接拖 `Assets/AssetLibrary/Prefabs/` 里的预制体进场景。

> 提示：第一次导入会压缩约 {len(models) * 3 + len(materials) * 3} 张纹理，耗时约 2–6 分钟；
> 导入完成后工程会多出 1.5–2.5 GB 的 `Library/` 缓存，属正常现象。

---

## 二、目录结构

```
UnityProject_AssetLibrary/
├─ Assets/AssetLibrary/
│  ├─ Models/            {len(models)} 个模型，按类别分文件夹（.obj + .mtl + Textures/ + Materials/）
│  ├─ Materials/         {len(materials)} 套 PBR 材质（Albedo / Normal / Mask + .mat）
│  ├─ Prefabs/           自动生成的 {len(models)} 个预制体（含碰撞体、灯具灯光）
│  ├─ Environment/HDRIs/ {len(hdris)} 张 .hdr 全景图 + Environment/Skyboxes/ 天空盒材质
│  ├─ Scenes/            Showcase.unity 演示场景
│  ├─ Shaders/           植被风摆（Foliage）、双面（TwoSided）、透明双面（TransparentTwoSided）
│  ├─ Scripts/           OrbitCamera（演示相机）、LightFlicker（灯光闪烁）
│  ├─ Editor/            构建工具、导入后处理器、URP 转换器
│  └─ Documentation/     asset_library.json、AssetIndex.csv、AssetLibrary_Guide.md
├─ Thumbnails/           每个素材的 512×512 预览图（PNG，未参与 Unity 导入）
├─ Screenshots/          分类联系表 + 演示场景渲染图
└─ README.md / CREDITS.md / AssetIndex.csv
```

---

## 三、素材总览

| 类型 | 数量 | 说明 |
|---|---|---|
| 3D 模型 | **{len(models)}** | 三角面 {tri_min:,} – {tri_max:,}，合计 {tri_total:,} 面（源模型 {tri_src:,} 面，已按游戏规格简化） |
| PBR 材质 | **{len(materials)}** | 60 套 ambientCG 1K + 30 套 Poly Haven 2K，均为无缝平铺 |
| HDRI 天空 | **{len(hdris)}** | 1K .hdr，可用于 Skybox / 环境光照（IBL） |
| **合计** | **{n_total}** | 另有 {len(models)} 个自动预制体、{len(models)} 组材质实例 |

### 3D 模型分类

| 类别 | 数量 | 代表素材 | 用途 | 授权 |
|---|---|---|---|---|
{model_rows}

### PBR 材质分类

| 类别 | 数量 | 分辨率 | 素材 |
|---|---|---|---|
{mat_rows}

### HDRI 天空

{hdri_list}

---

## 四、质量与技术规格

**模型**

- 全部来自 Poly Haven 的摄影测量 / 手工模型（CC0），经管线自动简化到游戏可用面数：
  树木 {min(60000, tri_max):,} 面以内、花草 ≤15,000、岩石 ≤8,000、灯具 ≤6,000、道具 ≤5,000。
- 保留原始 UV、法线、PBR 贴图；简化使用 meshoptimizer（gltfpack）保住轮廓与 UV 接缝。
- 单位：米（1 Unity 单位 = 1 米），Y 轴向上，轴心在模型底部中心，方便直接摆放。
- 每个材质球独立 .mat，带 Albedo / Normal / Mask（R=金属度, G=AO, B=粗糙度, A=光滑度）。
- 植被使用 `AssetLibrary/Foliage` 着色器：双面 + Alpha 裁剪 + 顶点风摆（可调 `_WindStrength` / `_WindSpeed` / `_WindDirection`）。

**材质（平铺纹理）**

- 格式：Albedo / Normal 为 JPG（sRGB / 线性法线），Mask 为 PNG（RGBA 打包，跨管线通用）。
- 分辨率：ambientCG 1024×1024，Poly Haven 2048×2048；均为无缝平铺。
- 打包通道同时兼容：
  - 内置管线 Standard：`_MetallicGlossMap`（R + A）、`_OcclusionMap`（G）
  - URP Lit：`_MetallicGlossMap`（R + A）、`_OcclusionMap`（G）
  - HDRP Lit：Mask Map（R=Metallic, G=AO, B=Detail, A=Smoothness）

**光照**

- 12 张 1K HDRI 覆盖晴天、日出、黄昏、阴天、夜景等，可直接做 Skybox + 环境光；
- 每个灯具预制体自带一盏已调好的暖色 Point Light（在 `Lamp Light` 子物体上，可自行改颜色/强度/开关），另附 `LightFlicker` 组件（默认关闭）。

---

## 五、使用说明

**预制体**：`Prefabs/Trees`、`Plants`、`PottedPlants`、`Rocks`、`Lamps`、`Props` 下，直接拖入场景。
树木带胶囊碰撞体（树干），岩石/道具为凸包 MeshCollider，盆栽/灯具为包围盒 BoxCollider。

**植被风摆**：植被材质默认使用 `AssetLibrary/Foliage`。在材质面板调整：
`_WindStrength`（米，建议 0.01–0.08）、`_WindSpeed`、`_WindFrequency`、`_WindDirection`。
风吹只发生在顶点高度方向，不会影响物体整体位置，适合大批量植被。

**灯具**：`Prefabs/Lamps` 里的预制体带 `Lamp Light` 子物体；删除该子物体即变成纯装饰模型。
需要摇晃烛光时，勾选 `LightFlicker` 组件即可。

**HDRI**：`Environment/Skyboxes/` 里是现成的 Skybox 材质，直接拖到 Lighting 窗口的 Environment → Skybox Material，
或 `RenderSettings.skybox = ...`。也可把 `.hdr` 拖到天空盒材质上换图。

**材质**：`Materials/<类别>/<名称>/` 下每个材质自带 `AssetLibrary` 命名规范的贴图，直接拖到物体上；
平铺次数按物体尺寸调 Tiling（例如 1 个材质 ≈ 2m×2m 的天然表面）。

**重新生成 / 扩展**：`Tools/` 目录下附带完整 Python 构建管线
（下载 → 简化 → 导出 OBJ → 打包 PBR 通道 → 生成清单），可改素材列表后重新跑一遍，
再在 Unity 里执行 `Tools ▸ Asset Library ▸ Rebuild Everything`。
命令行批量构建：`Tools/build.ps1`（会调用 Unity `-executeMethod`）。

---

## 六、管线兼容

| 管线 | 支持情况 |
|---|---|
| 内置渲染管线（Built-in） | ✅ 出厂即用（Standard + 自定义 Foliage 着色器） |
| URP | ✅ 菜单 `Tools ▸ Asset Library ▸ Convert Materials To URP` 一键转换（需要先安装 URP 包并把工程切到 URP；风摆着色器为内置管线 Surface Shader，转换后材质改为 URP Lit，风摆效果需另接 Shader Graph） |
| HDRP | ⚠️ 可用 Mask Map 通道，但需手动把材质换成 HDRP/Lit；本项目未提供 HDRP 转换器 |

**色彩空间**：工程为 Linear。若导入到 Gamma 工程，建议先 Player Settings → Color Space → Linear（PBR 贴图才正确）。

---

## 七、授权与来源

所有素材均为 **CC0 1.0 Universal**（公共领域贡献），可商用、可修改、可再分发，无需署名。

- 3D 模型、HDRI、30 套自然材质：[Poly Haven](https://polyhaven.com/)（CC0）
- 60 套工艺 / 建筑材质：[ambientCG](https://ambientcg.com/)（CC0）
- 简化工具：[meshoptimizer / gltfpack](https://github.com/zeux/meshoptimizer)（MIT）
- 完整出处清单见 `CREDITS.md` 与 `AssetIndex.csv`（含每个素材的源站链接）。

---

## 八、预览图

演示场景渲染见 `Screenshots/showcase_*.png`；每个素材的 512×512 缩略图在 `Thumbnails/`。

{previews}
"""

    with open(os.path.join(lib.PROJ, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    # ------------- in-package guide
    guide = f"""# Asset Library Guide / 素材库使用说明

共 **{n_total}** 个 CC0 素材：{len(models)} 模型 · {len(materials)} PBR 材质 · {len(hdris)} HDRI。

## 导入后处理（自动）

`AssetLibraryPostprocessor` 会按文件名自动设置导入参数：

| 文件名后缀 | 设置 |
|---|---|
| `*_Albedo.jpg` / `*_Albedo.png` | sRGB 颜色；PNG 保留 Alpha（植被镂空） |
| `*_Normal.jpg` | 法线贴图（NormalMap，线性） |
| `*_Mask.png` | 线性；R=金属度，G=环境光遮蔽，B=粗糙度，A=光滑度 |
| `*.hdr` | 线性 HDR 全景图 |

模型导入后处理同样会自动设置：Scale=1、不导入摄像机/灯光、计算 Mikk 切线、开启网格优化。

## Mask 通道（跨管线通用）

```
R = Metallic       (Standard: _MetallicGlossMap.R / URP: _MetallicGlossMap.R / HDRP: MaskMap.R)
G = Ambient Occlusion (Standard/URP: _OcclusionMap.G / HDRP: MaskMap.G)
B = Roughness      (HDRP: MaskMap.B - Detail)
A = Smoothness     (Standard/URP: _MetallicGlossMap.A / HDRP: MaskMap.A)
```

## 材质参数

模型材质：`_Metallic = 1`、`_Glossiness = 1`（由 Mask 驱动），
平铺材质同样为 1/1；想整体降低金属度/光滑度可下调这两个乘数。

## 风摆（Foliage Shader）

`_WindStrength` 单位米，`_WindHeight` 为参考高度（自动按模型高度写入）。
风力只影响顶点，不影响 Transform；若做烘焙光照请把 `_WindStrength` 设为 0。

## 重建

菜单 `Tools ▸ Asset Library ▸ Rebuild Everything` 会重新生成全部 .mat / .prefab / 天空盒 / 演示场景
（不会重新下载或修改原始贴图）。转换 URP：`Tools ▸ Asset Library ▸ Convert Materials To URP`。

## 授权

CC0 1.0 Universal。详见项目根目录 `CREDITS.md`。
"""
    with open(os.path.join(lib.DOCS, "AssetLibrary_Guide.md"), "w", encoding="utf-8") as f:
        f.write(guide)

    # ------------- credits
    lines = ["# CREDITS / 素材出处", "",
             "All assets are licensed **CC0 1.0 Universal (Public Domain Dedication)**.", "",
             "## 3D Models（Poly Haven, CC0）", ""]
    for m in sorted(models, key=lambda x: (x["category"], x["name"])):
        lines.append("- **%s** (%s, %d tris) — %s — 源文件 %s" % (
            m["name"], cn(m["category"]), m["tris"], m["sourceUrl"],
            "%.1f MB OBJ" % (os.path.getsize(os.path.join(lib.ASSETS, "Models", m["file"])) / 1e6)
            if os.path.exists(os.path.join(lib.ASSETS, "Models", m["file"])) else "-"))
    lines += ["", "## PBR Materials", ""]
    for m in sorted(materials, key=lambda x: (x["category"], x["name"])):
        lines.append("- **%s** (%s, %dpx) — %s" % (m["name"], cn(m["category"]), m["resolution"], m["sourceUrl"]))
    lines += ["", "## HDRIs（Poly Haven, CC0）", ""]
    for h in sorted(hdris, key=lambda x: x["name"]):
        lines.append("- **%s** — %s" % (h["name"], h["sourceUrl"]))
    lines += ["", "## Tools", "",
              "- meshoptimizer / gltfpack (MIT) — 模型简化",
              "- Python + Pillow — PBR 通道打包与文档生成",
              "- Unity 2022.3 LTS — 材质 / 预制体 / 场景生成", ""]
    with open(os.path.join(lib.PROJ, "CREDITS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("README / guide / credits written:", n_total, "assets")


if __name__ == "__main__":
    main()
