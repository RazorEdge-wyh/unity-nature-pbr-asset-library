# Unity 自然 / 室内 PBR 素材库 · v1.0

> **249 个可直接用于 Unity 的素材**：147 个 3D 模型（花 / 草 / 树 / 岩石 / 灯具 / 盆栽 / 道具）
> ＋ 90 套 PBR 材质（木材、地面、草地、砾石、岩石、金属、砖、织物、混凝土、瓷砖、树皮、沙、雪）
> ＋ 12 张 HDRI 天空。
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

> 提示：第一次导入会压缩约 711 张纹理，耗时约 2–6 分钟；
> 导入完成后工程会多出 1.5–2.5 GB 的 `Library/` 缓存，属正常现象。

---

## 二、目录结构

```
UnityProject_AssetLibrary/
├─ Assets/AssetLibrary/
│  ├─ Models/            147 个模型，按类别分文件夹（.obj + .mtl + Textures/ + Materials/）
│  ├─ Materials/         90 套 PBR 材质（Albedo / Normal / Mask + .mat）
│  ├─ Prefabs/           自动生成的 147 个预制体（含碰撞体、灯具灯光）
│  ├─ Environment/HDRIs/ 12 张 .hdr 全景图 + Environment/Skyboxes/ 天空盒材质
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
| 3D 模型 | **147** | 三角面 182 – 509,944，合计 4,859,640 面（源模型 22,869,543 面，已按游戏规格简化） |
| PBR 材质 | **90** | 60 套 ambientCG 1K + 30 套 Poly Haven 2K，均为无缝平铺 |
| HDRI 天空 | **12** | 1K .hdr，可用于 Skybox / 环境光照（IBL） |
| **合计** | **249** | 另有 147 个自动预制体、147 组材质实例 |

### 3D 模型分类

| 类别 | 数量 | 代表素材 | 用途 | 授权 |
|---|---|---|---|---|
| Decor | 27 | antique_ceramic_vase_01(7998 面), book_encyclopedia_set_01(8942 面), brass_vase_01(7999 面), brass_vase_02(6890 面), brass_vase_03(2616 面), ceramic_vase_01(7998 面) … | 道具/环境 | CC0 |
| Furniture | 25 | ArmChair_01(5626 面), BarberShopChair_01(4280 面), ClassicConsole_01(7566 面), ClassicNightstand_01(2002 面), CoffeeTable_01(10404 面), GreenChair_01(4213 面) … | 道具/环境 | CC0 |
| 花草植物 | 23 | bark_debris_01(39992 面), celandine_01(8966 面), dandelion_01(39995 面), dead_quiver_branch_01(14834 面), dry_branches_medium_01(16803 面), fern_02(6232 面) … | 树木/植被 | CC0 |
| 灯具 | 19 | Lantern_01(7998 面), brass_candleholders(8068 面), brass_diya_lantern(7993 面), caged_hanging_light(8000 面), hanging_industrial_lamp(7998 面), industrial_wall_lamp(4446 面) … | 道具/环境 | CC0 |
| 树木 | 15 | dead_quiver_trunk(17978 面), dead_tree_trunk(101802 面), dead_tree_trunk_02(83128 面), fir_sapling(299993 面), fir_sapling_medium(299741 面), fir_tree_01(508166 面) … | 树木/植被 | CC0 |
| 盆栽 / 花箱 | 9 | anthurium_botany_01(39998 面), calathea_orbifolia_01(16688 面), pachira_aquatica_01(39995 面), planter_box_01(8094 面), planter_box_02(10944 面), planter_box_03(13112 面) … | 道具/环境 | CC0 |
| Electronics | 9 | Camera_01(14998 面), Drill_01(2926 面), Megaphone_01(14998 面), Television_01(1918 面), lightbulb_led(6420 面), portable_searchlight(14997 面) … | 道具/环境 | CC0 |
| 岩石 | 8 | boulder_01(9996 面), namaqualand_boulder_02(10001 面), rock_07(10000 面), rock_09(9998 面), rock_moss_set_01(11518 面), rock_moss_set_02(12352 面) … | 道具/环境 | CC0 |
| 道具 / 树桩 | 6 | ceramic_pot(3592 面), treasure_chest(8229 面), tree_stump_01(7996 面), tree_stump_02(7996 面), wicker_basket_01(12100 面), wooden_bowl_01(8000 面) | 道具/环境 | CC0 |
| Kitchenware | 6 | brass_pan_01(4340 面), brass_pot_01(3760 面), brass_pot_02(3344 面), carved_wooden_plate(2112 面), jug_01(5770 面), metal_jug(6040 面) | 道具/环境 | CC0 |

### PBR 材质分类

| 类别 | 数量 | 分辨率 | 素材 |
|---|---|---|---|
| 地面 | 16 | 1024 px | Ground037, Ground054, Ground103, Ground106, Ground107, Ground108, Ground109, Ground110, Ground111, Ground112, brown_mud_leaves_01, forest_ground_04, forrest_ground_01, red_laterite_soil_stones, rocky_terrain_02, rocky_trail_02 |
| 砾石 | 10 | 1024 px | Gravel022, Gravel023, Gravel040, Gravel041, Gravel043, bicolour_gravel, gravel_floor, gravel_stones, rocky_gravel, sandy_gravel_02 |
| 岩面 | 9 | 1024 px | Rock051, Rock058, Rock060, Rock063, Rock064, aerial_rocks_02, coast_sand_rocks_02, rock_boulder_dry, rock_face_03 |
| 木材 | 8 | 1024 px | Wood049, Wood051, Wood092, Wood094, Wood095, Wood096, weathered_brown_planks, wood_floor |
| 金属 | 7 | 1024 px | Metal032, Metal046B, Metal048A, Metal049A, Metal055A, Metal061B, Metal063 |
| 树皮 | 7 | 2048 px | bark_brown_01, bark_brown_02, bark_willow, palm_tree_bark, pine_bark, sakura_bark, tree_bark_03 |
| 草地 | 6 | 1024 px | Grass001, Grass004, Grass005, Grass006, Grass008, aerial_grass_rock |
| 砖墙 | 5 | 1024 px | Bricks106A, Bricks108A, Bricks109B, Bricks112A, Bricks113A |
| 木地板 | 4 | 1024 px | WoodFloor043, WoodFloor051, WoodFloor064, WoodFloor070 |
| 织物 | 4 | 1024 px | Fabric061, Fabric081C, Fabric084, Fabric085 |
| 沙地 | 4 | 2048 px | aerial_beach_01, coast_sand_01, gravelly_sand, sand_01 |
| 木板 | 3 | 1024 px | Planks023A, Planks037A, Planks039 |
| 混凝土 | 3 | 1024 px | Concrete034, Concrete047A, Concrete048 |
| 瓷砖 | 3 | 1024 px | Tiles139, Tiles141, Tiles143 |
| 雪地 | 1 | 2048 px | snow_02 |

### HDRI 天空

dikhololo_night, kiara_1_dawn, kloofendal_48d_partly_cloudy_puresky, kloppenheim_02, kloppenheim_06_puresky, lilienstein, meadow_2, moonless_golf, satara_night, spruit_sunrise, the_sky_is_on_fire, venice_sunset

---

## 四、质量与技术规格

**模型**

- 全部来自 Poly Haven 的摄影测量 / 手工模型（CC0），经管线自动简化到游戏可用面数：
  树木 60,000 面以内、花草 ≤15,000、岩石 ≤8,000、灯具 ≤6,000、道具 ≤5,000。
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

### Decor（27）

![Decor](Screenshots/models_Decor.jpg)

### Electronics（9）

![Electronics](Screenshots/models_Electronics.jpg)

### Furniture（25）

![Furniture](Screenshots/models_Furniture.jpg)

### Kitchenware（6）

![Kitchenware](Screenshots/models_Kitchenware.jpg)

### 灯具（19）

![灯具](Screenshots/models_Lamps.jpg)

### 花草植物（23）

![花草植物](Screenshots/models_Plants.jpg)

### 盆栽 / 花箱（9）

![盆栽 / 花箱](Screenshots/models_PottedPlants.jpg)

### 道具 / 树桩（6）

![道具 / 树桩](Screenshots/models_Props.jpg)

### 岩石（8）

![岩石](Screenshots/models_Rocks.jpg)

### 树木（15）

![树木](Screenshots/models_Trees.jpg)

### 材质 · 树皮（7）

![材质 树皮](Screenshots/materials_Bark.jpg)

### 材质 · 砖墙（5）

![材质 砖墙](Screenshots/materials_Bricks.jpg)

### 材质 · 混凝土（3）

![材质 混凝土](Screenshots/materials_Concrete.jpg)

### 材质 · 织物（4）

![材质 织物](Screenshots/materials_Fabric.jpg)

### 材质 · 草地（6）

![材质 草地](Screenshots/materials_Grass.jpg)

### 材质 · 砾石（10）

![材质 砾石](Screenshots/materials_Gravel.jpg)

### 材质 · 地面（16）

![材质 地面](Screenshots/materials_Ground.jpg)

### 材质 · 金属（7）

![材质 金属](Screenshots/materials_Metal.jpg)

### 材质 · 木板（3）

![材质 木板](Screenshots/materials_Planks.jpg)

### 材质 · 岩面（9）

![材质 岩面](Screenshots/materials_Rock.jpg)

### 材质 · 沙地（4）

![材质 沙地](Screenshots/materials_Sand.jpg)

### 材质 · 雪地（1）

![材质 雪地](Screenshots/materials_Snow.jpg)

### 材质 · 瓷砖（3）

![材质 瓷砖](Screenshots/materials_Tiles.jpg)

### 材质 · 木材（8）

![材质 木材](Screenshots/materials_Wood.jpg)

### 材质 · 木地板（4）

![材质 木地板](Screenshots/materials_WoodFloor.jpg)

### HDRI 天空（12）

![HDRI](Screenshots/hdris.jpg)

