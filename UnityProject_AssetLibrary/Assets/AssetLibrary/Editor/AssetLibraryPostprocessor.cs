using UnityEditor;
using UnityEngine;

namespace AssetLibrary.EditorTools
{
    /// <summary>
    /// Automatically applies correct import settings to every texture that lives under
    /// Assets/.../AssetLibrary/... so the package stays "дроп-in" ready for any project.
    /// Naming convention:
    ///   *_Albedo.(jpg|png)  -> sRGB colour, alpha from input when PNG
    ///   *_Normal.(jpg|png)  -> normal map
    ///   *_Mask.png          -> linear, R = metallic, G = ambient occlusion,
    ///                          B = roughness, A = smoothness
    ///   *.hdr               -> linear HDR panorama (no sRGB)
    /// </summary>
    public class AssetLibraryPostprocessor : AssetPostprocessor
    {
        private void OnPreprocessTexture()
        {
            string p = assetPath.Replace('\\', '/').ToLowerInvariant();
            if (!p.Contains("/assetlibrary/")) return;
            var imp = (TextureImporter)assetImporter;
            if (p.EndsWith(".hdr"))
            {
                imp.textureType = TextureImporterType.Default;
                imp.sRGBTexture = false;
                imp.textureShape = TextureImporterShape.Texture2D;
                imp.maxTextureSize = 2048;
                imp.mipmapEnabled = true;
                imp.wrapMode = TextureWrapMode.Clamp;
                imp.textureCompression = TextureImporterCompression.CompressedHQ;
                return;
            }
            if (p.Contains("_normal"))
            {
                imp.textureType = TextureImporterType.NormalMap;
                imp.maxTextureSize = 2048;
                imp.mipmapEnabled = true;
                imp.textureCompression = TextureImporterCompression.CompressedHQ;
                return;
            }
            if (p.Contains("_mask"))
            {
                imp.textureType = TextureImporterType.Default;
                imp.sRGBTexture = false;
                imp.alphaSource = TextureImporterAlphaSource.FromInput;
                imp.alphaIsTransparency = false;
                imp.maxTextureSize = 2048;
                imp.mipmapEnabled = true;
                imp.wrapMode = TextureWrapMode.Repeat;
                imp.textureCompression = TextureImporterCompression.CompressedHQ;
                return;
            }
            imp.textureType = TextureImporterType.Default;
            imp.sRGBTexture = true;
            imp.maxTextureSize = 2048;
            imp.mipmapEnabled = true;
            if (p.Contains("_albedo") && p.EndsWith(".png"))
            {
                imp.alphaSource = TextureImporterAlphaSource.FromInput;
                imp.alphaIsTransparency = true;
            }
            else
            {
                imp.alphaSource = TextureImporterAlphaSource.None;
            }
        }

        private void OnPreprocessModel()
        {
            string p = assetPath.Replace('\\', '/').ToLowerInvariant();
            if (!p.Contains("/assetlibrary/")) return;
            var mi = (ModelImporter)assetImporter;
            mi.globalScale = 1f;
            mi.importCameras = false;
            mi.importLights = false;
            mi.importBlendShapes = false;
            mi.isReadable = false;
            mi.optimizeMeshPolygons = true;
            mi.optimizeMeshVertices = true;
            mi.weldVertices = true;
            mi.meshCompression = ModelImporterMeshCompression.Off;
            mi.importNormals = ModelImporterNormals.Import;
            mi.importTangents = ModelImporterTangents.CalculateMikk;
        }
    }
}
