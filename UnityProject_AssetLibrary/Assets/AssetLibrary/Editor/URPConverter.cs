using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace AssetLibrary.EditorTools
{
    /// <summary>
    /// Converts every generated Standard / custom material in the library to URP Lit.
    /// Works without a compile-time dependency on the URP package: the target shader is
    /// located by name at runtime (so this file compiles in Built-in, URP and HDRP projects).
    /// Run after the project has been switched to URP: Tools > Asset Library > Convert Materials To URP.
    /// </summary>
    public static class URPConverter
    {
        static readonly Dictionary<string, string> HdrpKeywords = new Dictionary<string, string>();

        [MenuItem("Tools/Asset Library/Convert Materials To URP")]
        public static void ConvertAll()
        {
            var urpLit = Shader.Find("Universal Render Pipeline/Lit");
            if (urpLit == null)
            {
                EditorUtility.DisplayDialog("URP not found",
                    "Universal Render Pipeline/Lit shader was not found.\n" +
                    "Install the Universal RP package and switch the project to URP first.", "OK");
                return;
            }
            int converted = 0;
            var guids = AssetDatabase.FindAssets("t:Material", new[] { AssetLibraryBuilder.Root });
            try
            {
                AssetDatabase.StartAssetEditing();
                foreach (var g in guids)
                {
                    string path = AssetDatabase.GUIDToAssetPath(g);
                    var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
                    if (mat == null) continue;
                    if (mat.shader == null) continue;
                    if (mat.shader.name.StartsWith("Universal Render Pipeline")) continue;
                    Convert(mat, urpLit);
                    EditorUtility.SetDirty(mat);
                    converted++;
                }
            }
            finally
            {
                AssetDatabase.StopAssetEditing();
            }
            AssetDatabase.SaveAssets();
            Debug.Log("[AssetLibrary] converted materials to URP: " + converted);
        }

        public static void Convert(Material mat, Shader urpLit)
        {
            Texture albedo = mat.HasProperty("_MainTex") ? mat.GetTexture("_MainTex") : null;
            Texture normal = mat.HasProperty("_BumpMap") ? mat.GetTexture("_BumpMap") : null;
            Texture mask = mat.HasProperty("_MetallicGlossMap") ? mat.GetTexture("_MetallicGlossMap") : null;
            Texture occlusion = mat.HasProperty("_OcclusionMap") ? mat.GetTexture("_OcclusionMap") : null;
            Color tint = mat.HasProperty("_Color") ? mat.GetColor("_Color") : Color.white;
            Color emission = mat.HasProperty("_EmissionColor") ? mat.GetColor("_EmissionColor") : Color.black;
            float cutoff = mat.HasProperty("_Cutoff") ? mat.GetFloat("_Cutoff") : 0.5f;
            float metallic = mat.HasProperty("_Metallic") ? mat.GetFloat("_Metallic") : 1f;
            float smoothness = mat.HasProperty("_Glossiness") ? mat.GetFloat("_Glossiness") : 1f;
            bool cutout = mat.IsKeywordEnabled("_ALPHATEST_ON") || mat.renderQueue == 2450;
            bool transparent = mat.renderQueue >= 3000 ||
                               (mat.HasProperty("_Mode") && mat.GetFloat("_Mode") >= 2f);

            mat.shader = urpLit;
            if (albedo != null) mat.SetTexture("_BaseMap", albedo);
            mat.SetColor("_BaseColor", tint);
            if (normal != null)
            {
                mat.SetTexture("_BumpMap", normal);
                mat.EnableKeyword("_NORMALMAP");
            }
            if (mask != null)
            {
                mat.SetTexture("_MetallicGlossMap", mask);
                mat.EnableKeyword("_METALLICSPECGLOSSMAP");
                mat.SetFloat("_Smoothness", smoothness);
                mat.SetFloat("_SmoothnessTextureChannel", 0f);
            }
            if (occlusion != null)
            {
                mat.SetTexture("_OcclusionMap", occlusion);
                mat.SetFloat("_OcclusionStrength", 1f);
            }
            mat.SetFloat("_Metallic", metallic);
            if (cutout)
            {
                mat.SetFloat("_AlphaClip", 1f);
                mat.EnableKeyword("_ALPHATEST_ON");
                mat.SetFloat("_Cutoff", cutoff);
                mat.SetFloat("_Surface", 0f);
                mat.SetOverrideTag("RenderType", "TransparentCutout");
                mat.renderQueue = 2450;
            }
            else if (transparent)
            {
                mat.SetFloat("_Surface", 1f);
                mat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                mat.SetFloat("_SrcBlend", (float)UnityEngine.Rendering.BlendMode.SrcAlpha);
                mat.SetFloat("_DstBlend", (float)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
                mat.SetFloat("_ZWrite", 0f);
                mat.SetOverrideTag("RenderType", "Transparent");
                mat.renderQueue = 3000;
            }
            else
            {
                mat.SetFloat("_Surface", 0f);
                mat.SetFloat("_ZWrite", 1f);
                mat.SetOverrideTag("RenderType", "Opaque");
                mat.renderQueue = -1;
            }
            if (emission.maxColorComponent > 0.001f)
            {
                mat.EnableKeyword("_EMISSION");
                mat.SetColor("_EmissionColor", emission);
                mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            }
            mat.SetFloat("_Cull", 0f); // double sided for foliage cards
        }
    }
}
