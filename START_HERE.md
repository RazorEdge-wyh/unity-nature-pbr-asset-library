# Unity 素材库 · 从这里开始

本文件夹是一套可直接用于 Unity 开发的高质量素材库，**共 227 个素材**：

| 类型 | 数量 | 内容 |
|---|---|---|
| 3D 模型 | 125 | 树木 19、花草植物 23、盆栽花箱 9、岩石 8、灯具 16、道具树桩 6 |
| PBR 材质 | 90 | 木材/木地板/木板/地面/草地/砾石/岩面/金属/砖/织物/混凝土/瓷砖/树皮/沙/雪 |
| HDRI 天空 | 12 | 晴天、日出、黄昏、阴天、夜景 |
| 自动预制体 | 81 | 带碰撞体；灯具自带暖色点光源 |
| 演示场景 | 2 | Showcase.unity（自然场景）+ Showcase_Interior.unity（现代室内场景） |

全部素材均为 **CC0 1.0 公共领域**授权：可商用、可修改、可再分发，无需署名。
所有模型与材质均经过 PBR 管线处理（Albedo / Normal / Mask 打包、线性色彩空间、平滑度通道），
并已按游戏规格做面数优化（总计约 187 万三角面，单模型 3 千 ~ 11 万面）。

## 怎么用（两条路，任选其一）

### ① 直接打开完整工程（推荐）
用 **Unity 2022.3 LTS** 打开 `UnityProject_AssetLibrary/`，
再打开 `Assets/AssetLibrary/Scenes/Showcase.unity`，按 Play 即可漫游。
素材在 `Assets/AssetLibrary/` 下：`Models / Materials / Prefabs / Environment / Shaders`。

### ② 导入到你自己的项目
双击 `UnityPackage/AssetLibrary_v1.0.unitypackage`，或在 Unity 里
`Assets ▸ Import Package ▸ Custom Package...` 选择它。
包内自带导入后处理器，会自动配置法线贴图、线性遮罩、HDR 等导入参数。

> 第一次导入约 2–6 分钟（要压缩 hundreds 张贴图），之后工程 Library 会增大 1.5–2.5 GB，正常。

## 目录说明

```
素材/
├─ START_HERE.md                   本文件
├─ UnityProject_AssetLibrary/      完整 Unity 工程（推荐直接打开）
│  ├─ Assets/AssetLibrary/         素材本体 + 预制体 + 演示场景 + 文档
│  ├─ Screenshots/                 分类联系表、演示场景渲染图
│  ├─ Thumbnails/                  183 张单素材预览图（512×512）
│  ├─ Tools/                       可复现的 Python 素材生成管线
│  ├─ README.md                    素材库详细说明（分类清单、技术规格、用法）
│  └─ CREDITS.md                   每个素材的源站链接
├─ UnityPackage/AssetLibrary_v1.0.unitypackage
├─ AssetIndex.csv                  227 条素材索引（名称/类别/面数/来源链接）
├─ CREDITS.md                      素材出处与授权
├─ LICENSE_CC0.txt                 CC0 1.0 授权全文说明
└─ Screenshots/                    预览图（联系表 + 演示渲染）
```

## 注意事项

- 工程使用 **内置渲染管线（Built-in）+ 线性色彩空间**。URP 用户请在
  `Tools ▸ Asset Library ▸ Convert Materials To URP` 一键转换材质。
- 植被材质使用 `AssetLibrary/Foliage` 着色器（双面 + 镂空 + 顶点风摆），
  可在材质面板调 `_WindStrength` / `_WindSpeed` / `_WindDirection`。
- 灯具预制体自带 `Lamp Light` 子物体（点光源，默认关闭阴影）；
  需要烛光晃动时勾选其上的 `LightFlicker` 组件。
- 模型轴心在底部中心、单位为米，可直接摆放；树木带树干胶囊碰撞体，岩石/道具为凸包碰撞体。
- 授权：模型/HDRI/自然材质来自 Poly Haven（CC0），建材来自 ambientCG（CC0）。
