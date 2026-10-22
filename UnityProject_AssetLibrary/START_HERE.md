# Unity 素材库 · 从这里开始

本文件夹是一套可直接用于 Unity 开发的高质量素材库，**共 249 个素材**（其中 22 个现代家具/陈设模型由 Blender 自行建模生成）。

| 类型 | 数量 | 内容 |
|---|---|---|
| 3D 模型 | 147 | 装饰摆件 27、家具 25、花草植物 23、灯具 19、树木 15、盆栽花箱 9、电子设备 9、岩石 8、道具树桩 6、厨具器皿 6 |
| PBR 材质 | 90 | 木材/木地板/木板/地面/草地/砾石/岩面/金属/砖/织物/混凝土/瓷砖/树皮/沙/雪 |
| HDRI 天空 | 12 | 晴天、日出、黄昏、阴天、夜景 |
| 自动预制体 | 147 | 带碰撞体；灯具自带暖色点光源 |
| 演示场景 | 2 | Showcase.unity（自然场景）+ Showcase_Interior.unity（现代室内场景） |
| 预览图 | 249 | 单素材缩略图 + 分类联系表 + 场景渲染图 |

全部素材均为 **CC0 1.0 公共领域**授权：可商用、可修改、可再分发，无需署名。

- 自然场景素材（树木 / 花草 / 岩石 / 灯具 / 自然材质 / HDRI）：来自 [Poly Haven](https://polyhaven.com)（CC0）
- 建筑与工艺材质：来自 [ambientCG](https://ambientcg.com)（CC0）
- **现代家具 / 灯具 / 陈设（22 件）**：使用 **Blender 4.2 程序化建模**自行搭建并导出，含现代沙发、扶手椅、茶几、
  电视柜、书架、餐椅、吧凳、边几、落地灯、台灯、混凝土地花盆、挂钟、花瓶、地毯、挂画、壁架等，
  面数 188–3144，配 14 套程序化 PBR 材质（胡桃木、橡木、亚麻、金属、黄铜、混凝土、陶瓷等）。

所有模型与材质均经过 PBR 管线处理（Albedo / Normal / Mask 打包、线性色彩空间、光滑度通道），
并已按游戏规格做面数优化（总计约 486 万三角面）。

## 怎么用（两条路，任选其一）

### 1. 直接打开完整工程（推荐）

用 **Unity 2022.3 LTS** 打开 `UnityProject_AssetLibrary/`：

- 自然场景：`Assets/AssetLibrary/Scenes/Showcase.unity`
- 现代室内场景：`Assets/AssetLibrary/Scenes/Showcase_Interior.unity`

素材在 `Assets/AssetLibrary/` 下：`Models / Materials / Prefabs / Environment / Shaders`。

### 2. 导入到你自己的项目

双击 `UnityPackage/AssetLibrary_v1.0.unitypackage`，或在 Unity 里
`Assets > Import Package > Custom Package...` 选择它。
包内自带导入后处理器，会自动配置法线贴图、线性遮罩、HDR 等导入参数。

> 第一次导入约 3–8 分钟（要压缩约 700 张贴图），之后工程 Library 会增大 1.5–3 GB，属正常。

## 目录说明

```
素材/
├─ START_HERE.md                   本文件
├─ UnityProject_AssetLibrary/      完整 Unity 工程（推荐直接打开）
│  ├─ Assets/AssetLibrary/         素材本体 + 预制体 + 两个演示场景 + 文档
│  ├─ Screenshots/                 分类联系表、自然/室内场景渲染图
│  ├─ Thumbnails/                  249 张单素材预览图（512x512）
│  ├─ Tools/                       可复现的 Python + Blender 素材生成管线
│  ├─ README.md                    素材库详细说明
│  └─ CREDITS.md                   每个素材的源站链接
├─ UnityPackage/AssetLibrary_v1.0.unitypackage
├─ AssetIndex.csv                  249 条素材索引（名称/类别/面数/来源链接）
├─ CREDITS.md / LICENSE_CC0.txt    出处与授权
└─ Screenshots/                    预览图
```

## 注意事项

- 工程使用 **内置渲染管线（Built-in）+ 线性色彩空间**。URP 用户请在
  `Tools > Asset Library > Convert Materials To URP` 一键转换材质。
- 植被材质使用 `AssetLibrary/Foliage` 着色器（双面 + 镂空 + 顶点风摆），
  可在材质面板调 `_WindStrength` / `_WindSpeed` / `_WindDirection`。
- 灯具预制体自带 `Lamp Light` 子物体（点光源）；现代落地灯/台灯同样带暖光，
  需要烛光晃动时勾选其上的 `LightFlicker` 组件。
- 模型轴心在底部中心、单位为米，可直接摆放；家具/装饰为包围盒碰撞体，
  树木为树干胶囊碰撞体，岩石/道具为凸包碰撞体。
- 自制现代模型可用 Blender 重新生成：`blender --background --python Tools/blender_build.py`
  （再执行 `python Tools/build_blender_assets.py` 导入 Unity 工程）。
- 授权：模型 / HDRI / 自然材质来自 Poly Haven（CC0），建材来自 ambientCG（CC0），
  自制模型与材质为 CC0。
- 作者：**湖南科技大学 26 级 王越豪**（GitHub @RazorEdge-wyh）
