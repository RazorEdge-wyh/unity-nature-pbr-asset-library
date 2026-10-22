# Asset Library Guide / 素材库使用说明

共 **243** 个 CC0 素材：141 模型 · 90 PBR 材质 · 12 HDRI。

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
