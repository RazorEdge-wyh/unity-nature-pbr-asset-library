using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;

namespace AssetLibrary.EditorTools
{
    [Serializable]
    public class MatFiles
    {
        public string albedo;
        public string normal;
        public string mask;
    }

    [Serializable]
    public class ModelMat
    {
        public string name;
        public string sourceName;
        public string albedo;
        public string normal;
        public string mask;
        public string renderMode;
        public bool doubleSided;
        public bool emissive;
        public float metallic;
        public float roughness;
    }

    [Serializable]
    public class ModelEntry
    {
        public string name;
        public string category;
        public string file;
        public int tris;
        public int trisOriginal;
        public float[] boundsMin;
        public float[] boundsMax;
        public ModelMat[] materials;
    }

    [Serializable]
    public class MaterialEntry
    {
        public string name;
        public string category;
        public string path;
        public MatFiles files;
        public int resolution;
    }

    [Serializable]
    public class HdriEntry
    {
        public string name;
        public string path;
        public int resolution;
    }

    [Serializable]
    public class LibraryData
    {
        public string version;
        public ModelEntry[] models;
        public MaterialEntry[] materials;
        public HdriEntry[] hdris;
    }

    public static class AssetLibraryBuilder
    {
        public const string Root = "Assets/AssetLibrary";
        public const string DocsPath = Root + "/Documentation/asset_library.json";
        const string FoliageShaderName = "AssetLibrary/Foliage";
        const string TwoSidedShaderName = "AssetLibrary/TwoSided";
        const string TransparentShaderName = "AssetLibrary/TransparentTwoSided";

        static Dictionary<string, Material> modelMaterialMap = new Dictionary<string, Material>();

        // ------------------------------------------------------------------ utils
        static void EnsureFolder(string assetDir)
        {
            if (AssetDatabase.IsValidFolder(assetDir)) return;
            string parent = Path.GetDirectoryName(assetDir).Replace('\\', '/');
            if (!string.IsNullOrEmpty(parent) && !AssetDatabase.IsValidFolder(parent)) EnsureFolder(parent);
            string leaf = Path.GetFileName(assetDir);
            if (!AssetDatabase.IsValidFolder(assetDir)) AssetDatabase.CreateFolder(parent, leaf);
        }

        static T LoadAsset<T>(string path) where T : UnityEngine.Object
        {
            if (string.IsNullOrEmpty(path)) return null;
            return AssetDatabase.LoadAssetAtPath<T>(path);
        }

        static string TexPath(string modelDir, string file)
        {
            return modelDir + "/Textures/" + file;
        }

        static bool IsFoliage(ModelEntry e, ModelMat m)
        {
            string n = (m.sourceName != null ? m.sourceName : m.name).ToLowerInvariant();
            if (n.Contains("pot") || n.Contains("planter") || n.Contains("soil")
                || n.Contains("trunk") || n.Contains("bark") || n.Contains("root")
                || n.Contains("stump") || n.Contains("branch"))
                return false;
            string[] hints = { "leaf", "leaves", "twig", "needle", "grass", "flower", "petal", "plant",
                               "shrub", "fern", "moss", "foliage", "frond", "weed", "dandelion",
                               "celandine", "periwinkle", "nettle", "ursinia", "gazania", "empodium",
                               "stinkkruid", "heliophila", "sorrel", "leipoldtia", "cheiridopsis",
                               "iceplant", "rooibos", "didelta", "searsia", "quiver", "nettle" };
            if (hints.Any(h => n.Contains(h))) return true;
            if (e.category == "Plants") return true;
            return false;
        }

        static Shader ShaderOrFallback(string name)
        {
            var s = Shader.Find(name);
            if (s == null)
            {
                Debug.LogWarning("Shader not found: " + name + " - using Standard");
                s = Shader.Find("Standard");
            }
            return s;
        }

        static Material CreateOrUpdate(string assetPath, Shader shader)
        {
            EnsureFolder(Path.GetDirectoryName(assetPath).Replace('\\', '/'));
            var mat = AssetDatabase.LoadAssetAtPath<Material>(assetPath);
            if (mat == null)
            {
                mat = new Material(shader);
                AssetDatabase.CreateAsset(mat, assetPath);
            }
            else if (mat.shader != shader)
            {
                mat.shader = shader;
            }
            return mat;
        }

        static void SetupStandardPBR(Material mat, Texture2D albedo, Texture2D normal, Texture2D mask,
                                     float metallic, float smoothness, string renderMode)
        {
            mat.SetTexture("_MainTex", albedo);
            if (normal != null)
            {
                mat.SetTexture("_BumpMap", normal);
                mat.EnableKeyword("_NORMALMAP");
                mat.SetFloat("_BumpScale", 1f);
            }
            if (mask != null)
            {
                mat.SetTexture("_MetallicGlossMap", mask);
                mat.SetTexture("_OcclusionMap", mask);
                mat.EnableKeyword("_METALLICGLOSSMAP");
                mat.EnableKeyword("_OCCLUSIONMAP");
                mat.SetFloat("_Metallic", metallic);
                mat.SetFloat("_Glossiness", smoothness);
                mat.SetFloat("_SmoothnessTextureChannel", 0f);
                mat.SetFloat("_OcclusionStrength", 1f);
            }
            else
            {
                mat.SetFloat("_Metallic", metallic);
                mat.SetFloat("_Glossiness", smoothness);
            }
            if (renderMode == "cutout")
            {
                mat.SetFloat("_Mode", 1f);
                mat.SetOverrideTag("RenderType", "TransparentCutout");
                mat.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.One);
                mat.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.Zero);
                mat.SetInt("_ZWrite", 1);
                mat.EnableKeyword("_ALPHATEST_ON");
                mat.DisableKeyword("_ALPHABLEND_ON");
                mat.DisableKeyword("_ALPHAPREMULTIPLY_ON");
                mat.SetFloat("_Cutoff", 0.5f);
                mat.renderQueue = 2450;
            }
            else if (renderMode == "transparent")
            {
                mat.SetFloat("_Mode", 3f);
                mat.SetOverrideTag("RenderType", "Transparent");
                mat.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
                mat.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
                mat.SetInt("_ZWrite", 0);
                mat.DisableKeyword("_ALPHATEST_ON");
                mat.EnableKeyword("_ALPHABLEND_ON");
                mat.DisableKeyword("_ALPHAPREMULTIPLY_ON");
                mat.renderQueue = 3000;
            }
            else
            {
                mat.SetFloat("_Mode", 0f);
                mat.SetOverrideTag("RenderType", "Opaque");
                mat.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.One);
                mat.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.Zero);
                mat.SetInt("_ZWrite", 1);
                mat.DisableKeyword("_ALPHATEST_ON");
                mat.DisableKeyword("_ALPHABLEND_ON");
                mat.DisableKeyword("_ALPHAPREMULTIPLY_ON");
                mat.renderQueue = -1;
            }
            mat.enableInstancing = true;
        }

        static void SetupCustomPBR(Material mat, Texture2D albedo, Texture2D normal, Texture2D mask,
                                   float metallic, float smoothness, bool emissive, float windStrength,
                                   float windHeight)
        {
            mat.SetTexture("_MainTex", albedo);
            mat.SetTexture("_BumpMap", normal != null ? normal : Texture2D.normalTexture);
            if (mask != null)
            {
                mat.SetTexture("_MetallicGlossMap", mask);
                mat.SetTexture("_OcclusionMap", mask);
            }
            mat.SetColor("_Color", Color.white);
            mat.SetFloat("_Metallic", metallic);
            mat.SetFloat("_Glossiness", smoothness);
            mat.SetFloat("_OcclusionStrength", 1f);
            mat.SetFloat("_Cutoff", 0.18f);
            mat.SetFloat("_WindStrength", windStrength);
            mat.SetFloat("_WindSpeed", 1.4f);
            mat.SetFloat("_WindFrequency", 0.35f);
            mat.SetVector("_WindDirection", new Vector4(1f, 0f, 0.35f, 0f));
            mat.SetFloat("_WindHeight", Mathf.Max(0.2f, windHeight));
            mat.SetColor("_EmissionColor", emissive ? new Color(1f, 0.78f, 0.5f) * 3f : Color.black);
        }

        // ------------------------------------------------------------------ import data
        static LibraryData LoadData()
        {
            var ta = AssetDatabase.LoadAssetAtPath<TextAsset>(DocsPath);
            if (ta == null) throw new Exception("Missing " + DocsPath);
            return JsonUtility.FromJson<LibraryData>(ta.text);
        }

        public static void ImportAllCommitted()
        {
            AssetDatabase.ImportAsset(Root, ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceSynchronousImport);
            AssetDatabase.Refresh();
        }

        // ------------------------------------------------------------------ textures
        public static void ApplyTextureSettings()
        {
            var guids = AssetDatabase.FindAssets("t:Texture2D", new[] { Root });
            int fixedCount = 0;
            try
            {
                AssetDatabase.StartAssetEditing();
                foreach (var g in guids)
                {
                    string path = AssetDatabase.GUIDToAssetPath(g);
                    var imp = AssetImporter.GetAtPath(path) as TextureImporter;
                    if (imp == null) continue;
                    string low = path.ToLowerInvariant();
                    bool dirty = false;
                    if (low.EndsWith(".hdr"))
                    {
                        if (imp.sRGBTexture) { imp.sRGBTexture = false; dirty = true; }
                        if (imp.maxTextureSize < 2048) { imp.maxTextureSize = 2048; dirty = true; }
                        if (imp.textureShape != TextureImporterShape.Texture2D) { imp.textureShape = TextureImporterShape.Texture2D; dirty = true; }
                    }
                    else if (low.Contains("_normal"))
                    {
                        if (imp.textureType != TextureImporterType.NormalMap) { imp.textureType = TextureImporterType.NormalMap; dirty = true; }
                        if (imp.maxTextureSize < 2048) { imp.maxTextureSize = 2048; dirty = true; }
                    }
                    else if (low.Contains("_mask"))
                    {
                        if (imp.sRGBTexture) { imp.sRGBTexture = false; dirty = true; }
                        if (imp.alphaSource != TextureImporterAlphaSource.FromInput) { imp.alphaSource = TextureImporterAlphaSource.FromInput; dirty = true; }
                        if (imp.alphaIsTransparency) { imp.alphaIsTransparency = false; dirty = true; }
                        if (imp.wrapMode != TextureWrapMode.Repeat) { imp.wrapMode = TextureWrapMode.Repeat; dirty = true; }
                    }
                    else
                    {
                        if (!imp.sRGBTexture) { imp.sRGBTexture = true; dirty = true; }
                        if (low.Contains("_albedo") && low.EndsWith(".png") && imp.alphaSource != TextureImporterAlphaSource.FromInput)
                        {
                            imp.alphaSource = TextureImporterAlphaSource.FromInput;
                            imp.alphaIsTransparency = true;
                            dirty = true;
                        }
                        if (imp.maxTextureSize < 2048) { imp.maxTextureSize = 2048; dirty = true; }
                    }
                    if (imp.mipmapEnabled == false && !low.Contains("_thumb")) { imp.mipmapEnabled = true; dirty = true; }
                    if (dirty) { imp.SaveAndReimport(); fixedCount++; }
                }
            }
            finally
            {
                AssetDatabase.StopAssetEditing();
            }
            AssetDatabase.Refresh();
            Debug.Log("[AssetLibrary] texture settings fixed: " + fixedCount);
        }

        // ------------------------------------------------------------------ library materials
        public static void BuildLibraryMaterials(LibraryData data)
        {
            var standard = Shader.Find("Standard");
            var twoSided = ShaderOrFallback(TwoSidedShaderName);
            int count = 0;
            foreach (var m in data.materials)
            {
                if (m.files == null) continue;
                string dir = Root + "/" + m.path;
                string matPath = dir + "/" + m.name + ".mat";
                var mat = CreateOrUpdate(matPath, standard);
                var albedo = LoadAsset<Texture2D>(dir + "/" + m.files.albedo);
                var normal = LoadAsset<Texture2D>(dir + "/" + m.files.normal);
                var mask = LoadAsset<Texture2D>(dir + "/" + m.files.mask);
                SetupStandardPBR(mat, albedo, normal, mask, 1f, 1f, "opaque");
                mat.name = m.name;
                EditorUtility.SetDirty(mat);
                count++;
            }
            Debug.Log("[AssetLibrary] library materials: " + count);
        }

        // ------------------------------------------------------------------ model materials + prefabs
        static void BuildModelMaterials(LibraryData data)
        {
            modelMaterialMap.Clear();
            int count = 0;
            foreach (var e in data.models)
            {
                string modelDir = Root + "/Models/" + e.category + "/" + e.name;
                float height = Mathf.Max(0.2f, e.boundsMax != null ? e.boundsMax[1] - e.boundsMin[1] : 1f);
                foreach (var m in e.materials)
                {
                    bool foliage = IsFoliage(e, m) && m.renderMode != "transparent";
                    Shader shader;
                    if (m.renderMode == "transparent") shader = ShaderOrFallback(TransparentShaderName);
                    else if (foliage) shader = ShaderOrFallback(FoliageShaderName);
                    else if (m.doubleSided) shader = ShaderOrFallback(TwoSidedShaderName);
                    else shader = Shader.Find("Standard");

                    string matPath = modelDir + "/Materials/" + m.name + ".mat";
                    var mat = CreateOrUpdate(matPath, shader);
                    mat.name = m.name;
                    var albedo = LoadAsset<Texture2D>(TexPath(modelDir, m.albedo));
                    var normal = LoadAsset<Texture2D>(TexPath(modelDir, m.normal));
                    var mask = LoadAsset<Texture2D>(TexPath(modelDir, m.mask));

                    if (shader.name == "Standard")
                        SetupStandardPBR(mat, albedo, normal, mask, 1f, 1f, m.renderMode);
                    else
                    {
                        float wind = 0f;
                        if (foliage)
                        {
                            if (e.category == "Plants") wind = 0.06f;
                            else if (e.category == "Trees") wind = 0.025f;
                            else wind = 0.02f;
                        }
                        SetupCustomPBR(mat, albedo, normal, mask, 1f, foliage ? 0.55f : 1f, m.emissive, wind, height);
                        if (m.emissive)
                        {
                            mat.EnableKeyword("_EMISSION");
                            mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
                        }
                    }
                    EditorUtility.SetDirty(mat);
                    modelMaterialMap[e.name + "|" + m.name] = mat;
                    count++;
                }
            }
            Debug.Log("[AssetLibrary] model materials: " + count);
        }

        static Material MatchMaterial(ModelEntry e, string importedName, int fallbackIndex)
        {
            if (!string.IsNullOrEmpty(importedName))
            {
                foreach (var m in e.materials)
                    if (string.Equals(m.name, importedName, StringComparison.OrdinalIgnoreCase)) return modelMaterialMap[e.name + "|" + m.name];
                foreach (var m in e.materials)
                {
                    var src = m.sourceName ?? m.name;
                    if (importedName.IndexOf(src, StringComparison.OrdinalIgnoreCase) >= 0 ||
                        src.IndexOf(importedName, StringComparison.OrdinalIgnoreCase) >= 0)
                        return modelMaterialMap[e.name + "|" + m.name];
                }
            }
            if (fallbackIndex >= 0 && fallbackIndex < e.materials.Length)
                return modelMaterialMap[e.name + "|" + e.materials[fallbackIndex].name];
            return null;
        }

        static Bounds RendererBounds(GameObject go)
        {
            var rs = go.GetComponentsInChildren<MeshRenderer>(true);
            if (rs.Length == 0) return new Bounds(Vector3.zero, Vector3.one);
            Bounds b = rs[0].bounds;
            foreach (var r in rs) b.Encapsulate(r.bounds);
            return b;
        }

        public static void BuildPrefabs(LibraryData data)
        {
            int count = 0;
            foreach (var e in data.models)
            {
                string objPath = Root + "/Models/" + e.file;
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(objPath);
                if (model == null) { Debug.LogWarning("[AssetLibrary] missing model " + objPath); continue; }
                var go = UnityEngine.Object.Instantiate(model);
                go.name = e.name;
                go.transform.position = Vector3.zero;
                go.transform.rotation = Quaternion.identity;
                go.transform.localScale = Vector3.one;

                int fallback = 0;
                foreach (var r in go.GetComponentsInChildren<MeshRenderer>(true))
                {
                    var mats = r.sharedMaterials;
                    for (int i = 0; i < mats.Length; i++)
                    {
                        string imported = mats[i] != null ? mats[i].name : "";
                        var target = MatchMaterial(e, imported, fallback);
                        if (target != null) mats[i] = target;
                        fallback++;
                    }
                    r.sharedMaterials = mats;
                    r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.On;
                    r.receiveShadows = true;
                }
                foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
                {
                    if (mf.sharedMesh != null) mf.sharedMesh.name = mf.sharedMesh.name;
                }

                var b = RendererBounds(go);
                AddCollider(go, e, b);
                if (e.category == "Lamps") AddLampLight(go, b);

                string prefabPath = Root + "/Prefabs/" + e.category + "/" + e.name + ".prefab";
                EnsureFolder(Root + "/Prefabs/" + e.category);
                PrefabUtility.SaveAsPrefabAsset(go, prefabPath);
                UnityEngine.Object.DestroyImmediate(go);
                count++;
            }
            Debug.Log("[AssetLibrary] prefabs: " + count);
        }

        static void AddCollider(GameObject go, ModelEntry e, Bounds b)
        {
            switch (e.category)
            {
                case "Trees":
                    {
                        var col = go.AddComponent<CapsuleCollider>();
                        col.radius = Mathf.Max(0.03f, 0.06f * Mathf.Max(b.size.x, b.size.z));
                        col.height = Mathf.Max(0.5f, b.size.y * 0.85f);
                        col.center = new Vector3(b.center.x, col.height * 0.5f, b.center.z);
                        break;
                    }
                case "Rocks":
                case "Props":
                    {
                        var col = go.AddComponent<MeshCollider>();
                        col.convex = true;
                        break;
                    }
                case "PottedPlants":
                case "Lamps":
                    {
                        var col = go.AddComponent<BoxCollider>();
                        col.center = b.center;
                        col.size = b.size;
                        break;
                    }
                default:
                    break;
            }
        }

        static void AddLampLight(GameObject go, Bounds b)
        {
            var lightGo = new GameObject("Lamp Light");
            lightGo.transform.SetParent(go.transform, false);
            lightGo.transform.position = new Vector3(b.center.x, b.min.y + b.size.y * 0.72f, b.center.z);
            var light = lightGo.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = new Color(1f, 0.82f, 0.6f);
            light.intensity = 4f;
            light.range = Mathf.Clamp(Mathf.Max(b.size.x, b.size.z, b.size.y) * 2.2f, 3f, 18f);
            light.shadows = LightShadows.None;
            light.renderMode = LightRenderMode.ForcePixel;
            var marker = lightGo.AddComponent<LightFlicker>();
            marker.enabled = false;
        }

        // ------------------------------------------------------------------ skyboxes
        public static void BuildSkyboxes(LibraryData data)
        {
            EnsureFolder(Root + "/Environment/Skyboxes");
            var shader = ShaderOrFallback("Skybox/Panoramic");
            foreach (var h in data.hdris)
            {
                var tex = LoadAsset<Texture2D>(Root + "/" + h.path);
                if (tex == null) { Debug.LogWarning("missing hdri " + h.path); continue; }
                string matPath = Root + "/Environment/Skyboxes/" + h.name + ".mat";
                var mat = CreateOrUpdate(matPath, shader);
                mat.SetTexture("_MainTex", tex);
                mat.SetFloat("_Mapping", 1f);
                mat.SetFloat("_ImageType", 0f);
                mat.SetFloat("_Exposure", 1.2f);
                mat.SetFloat("_Rotation", 0f);
                mat.name = h.name + "_Skybox";
                EditorUtility.SetDirty(mat);
            }
            Debug.Log("[AssetLibrary] skyboxes built");
        }

        // ------------------------------------------------------------------ showcase scene
        public static void BuildShowcase(LibraryData data)
        {
            EnsureFolder(Root + "/Scenes");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            Material ground = LoadAsset<Material>(Root + "/Materials/Ground/Ground111/Ground111.mat");
            if (ground == null) ground = AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.FindAssets("t:Material " + Root + "/Materials/Ground").Select(AssetDatabase.GUIDToAssetPath).FirstOrDefault());

            var plane = GameObject.CreatePrimitive(PrimitiveType.Plane);
            plane.name = "Ground";
            plane.transform.position = Vector3.zero;
            plane.transform.localScale = new Vector3(4f, 1f, 4f);
            if (ground != null) plane.GetComponent<Renderer>().sharedMaterial = ground;

            RenderSettings.skybox = LoadAsset<Material>(Root + "/Environment/Skyboxes/kloofendal_48d_partly_cloudy_puresky.mat");
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Skybox;
            RenderSettings.ambientIntensity = 1f;
            RenderSettings.fog = false;

            var sunGo = new GameObject("Sun");
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.95f, 0.86f);
            sun.intensity = 1.15f;
            sun.shadows = LightShadows.Soft;
            sunGo.transform.rotation = Quaternion.Euler(42f, -38f, 0f);

            var fillGo = new GameObject("Fill");
            var fill = fillGo.AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.color = new Color(0.55f, 0.65f, 0.9f);
            fill.intensity = 0.25f;
            fill.shadows = LightShadows.None;
            fillGo.transform.rotation = Quaternion.Euler(-25f, 140f, 0f);

            string[] trees = { "tree_small_02", "fir_sapling_medium", "pine_sapling_medium", "quiver_tree_02", "searsia_burchellii", "fir_tree_01" };
            Scatter(trees, "Trees", 14, 9f, new Vector2(0f, 0f));
            string[] shrubs = { "shrub_01", "shrub_02", "shrub_03", "fern_02", "nettle_plant", "flower_gazania", "celandine_01", "dandelion_01" };
            Scatter(shrubs, "Plants", 34, 11f, new Vector2(0f, 0f));
            string[] rocks = { "boulder_01", "rock_07", "rock_moss_set_01", "stone_01" };
            Scatter(rocks, "Rocks", 14, 10f, new Vector2(0f, 0f));
            string[] lamps = { "street_lamp_01", "street_lamp_02", "lantern_chandelier_01", "vintage_oil_lamp" };
            Scatter(lamps, "Lamps", 4, 5f, new Vector2(0f, 0f));

            var camGo = new GameObject("Main Camera");
            var cam = camGo.AddComponent<Camera>();
            camGo.tag = "MainCamera";
            camGo.transform.position = new Vector3(7.5f, 3.6f, -9.5f);
            camGo.transform.LookAt(new Vector3(0f, 2.2f, 1.5f));
            cam.fieldOfView = 48f;
            cam.farClipPlane = 500f;
            var orbit = camGo.AddComponent<OrbitCamera>();
            orbit.focus = new Vector3(0f, 2.2f, 1.5f);
            orbit.distance = 13f;

            EditorSceneManager.SaveScene(scene, Root + "/Scenes/Showcase.unity");
            Debug.Log("[AssetLibrary] showcase scene saved");
        }

        static void Scatter(string[] names, string category, int count, float radius, Vector2 yRange)
        {
            var rand = new System.Random(1234 + names.Length);
            for (int i = 0; i < count; i++)
            {
                string n = names[i % names.Length];
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Prefabs/" + category + "/" + n + ".prefab");
                if (prefab == null) continue;
                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                float a = (float)(rand.NextDouble() * Math.PI * 2.0);
                float r = 3f + (float)rand.NextDouble() * radius;
                go.transform.position = new Vector3(Mathf.Cos(a) * r, 0f, Mathf.Sin(a) * r);
                go.transform.rotation = Quaternion.Euler(0f, (float)(rand.NextDouble() * 360.0), 0f);
                if (yRange.y > 0f)
                    go.transform.position += Vector3.up * ((float)rand.NextDouble() * (yRange.y - yRange.x) + yRange.x);
            }
        }


        // ------------------------------------------------------------------ modern interior showcase
        static GameObject PlacePrefab(string category, string name, Vector3 pos, float rotY)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Prefabs/" + category + "/" + name + ".prefab");
            if (prefab == null) { Debug.LogWarning("[AssetLibrary] missing prefab " + category + "/" + name); return null; }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            go.transform.position = pos;
            go.transform.rotation = Quaternion.Euler(0f, rotY, 0f);
            return go;
        }

        static Material LoadMatSafe(string relPath)
        {
            var m = AssetDatabase.LoadAssetAtPath<Material>(Root + "/" + relPath + ".mat");
            if (m == null) Debug.LogWarning("[AssetLibrary] missing material " + relPath);
            return m;
        }

        static void AddWall(string name, Vector3 pos, Vector3 euler, Vector3 scale, Material mat)
        {
            var wall = GameObject.CreatePrimitive(PrimitiveType.Plane);
            wall.name = name;
            wall.transform.position = pos;
            wall.transform.rotation = Quaternion.Euler(euler);
            wall.transform.localScale = scale;
            if (mat != null) wall.GetComponent<Renderer>().sharedMaterial = mat;
        }

        public static void BuildShowcaseInterior(LibraryData data)
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var floorMat = LoadMatSafe("Materials/WoodFloor/WoodFloor051/WoodFloor051");
            var wallMat = LoadMatSafe("Materials/Concrete/Concrete034/Concrete034");
            var rugMat = LoadMatSafe("Materials/Fabric/Fabric085/Fabric085");

            var floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
            floor.name = "Floor";
            floor.transform.localScale = new Vector3(1.3f, 1f, 1.3f);
            if (floorMat != null) floor.GetComponent<Renderer>().sharedMaterial = floorMat;

            AddWall("Wall_Back", new Vector3(0f, 1.6f, 6.5f), new Vector3(90f, 0f, 0f), new Vector3(1.3f, 0.32f, 1f), wallMat);
            AddWall("Wall_Left", new Vector3(-6.5f, 1.6f, 0f), new Vector3(90f, 90f, 0f), new Vector3(1.3f, 0.32f, 1f), wallMat);

            var rug = GameObject.CreatePrimitive(PrimitiveType.Plane);
            rug.name = "Rug";
            rug.transform.position = new Vector3(0f, 0.012f, 2.2f);
            rug.transform.localScale = new Vector3(0.42f, 1f, 0.34f);
            if (rugMat != null) rug.GetComponent<Renderer>().sharedMaterial = rugMat;

            // seating group
            PlacePrefab("Furniture", "Sofa_01", new Vector3(0f, 0f, 3.6f), 180f);
            var coffee = PlacePrefab("Furniture", "CoffeeTable_01", new Vector3(0f, 0f, 1.6f), 0f);
            PlacePrefab("Furniture", "ArmChair_01", new Vector3(-2.9f, 0f, 2.2f), 125f);
            PlacePrefab("Furniture", "Ottoman_01", new Vector3(2.5f, 0f, 1.8f), 20f);
            PlacePrefab("Furniture", "GreenChair_01", new Vector3(4.6f, 0f, 3.0f), 230f);

            // wall units
            PlacePrefab("Furniture", "Shelf_01", new Vector3(-4.4f, 0f, 5.6f), 0f);
            var console = PlacePrefab("Furniture", "ClassicConsole_01", new Vector3(2.4f, 0f, 5.6f), 0f);
            float consoleTop = 0.75f;
            if (console != null) consoleTop = RendererBounds(console).max.y;
            PlacePrefab("Electronics", "Television_01", new Vector3(2.4f, consoleTop, 5.6f), 180f);

            // plants
            PlacePrefab("PottedPlants", "potted_plant_01", new Vector3(-5.6f, 0f, 1.0f), 20f);
            PlacePrefab("PottedPlants", "potted_plant_02", new Vector3(5.6f, 0f, 0.8f), -30f);
            PlacePrefab("PottedPlants", "planter_box_02", new Vector3(5.3f, 0f, 4.4f), 0f);
            PlacePrefab("Plants", "fern_02", new Vector3(-5.4f, 0f, 3.4f), 0f);

            // decor
            if (coffee != null)
            {
                float top = RendererBounds(coffee).max.y;
                PlacePrefab("Decor", "ceramic_vase_01", new Vector3(-0.35f, top, 1.45f), 0f);
                PlacePrefab("Decor", "chess_set", new Vector3(0.35f, top, 1.9f), 20f);
            }
            PlacePrefab("Decor", "brass_vase_01", new Vector3(-4.4f, 0.9f, 5.45f), 0f);
            PlacePrefab("Decor", "book_encyclopedia_set_01", new Vector3(2.9f, consoleTop, 5.5f), 0f);
            PlacePrefab("Decor", "wall_clock", new Vector3(0f, 2.55f, 6.44f), 0f);
            PlacePrefab("Decor", "fancy_picture_frame_01", new Vector3(-2.1f, 1.9f, 6.44f), 0f);
            PlacePrefab("Decor", "ornate_mirror_01", new Vector3(-3.6f, 1.85f, 6.44f), 0f);
            PlacePrefab("Decor", "standing_picture_frame_01", new Vector3(4.0f, 0f, 0.6f), 200f);

            // lighting
            var ceilingGo = new GameObject("Ceiling_Lamp");
            PlacePrefab("Lamps", "modern_ceiling_lamp_01", new Vector3(0f, 2.9f, 2.0f), 0f);

            var keyGo = new GameObject("Sun");
            var sun = keyGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.95f, 0.88f);
            sun.intensity = 1.0f;
            sun.shadows = LightShadows.Soft;
            keyGo.transform.rotation = Quaternion.Euler(38f, -55f, 0f);

            var fillGo = new GameObject("Fill_Area");
            var fill = fillGo.AddComponent<Light>();
            fill.type = LightType.Point;
            fill.color = new Color(1f, 0.92f, 0.82f);
            fill.intensity = 3.5f;
            fill.range = 10f;
            fill.shadows = LightShadows.None;
            fillGo.transform.position = new Vector3(0f, 2.6f, 2.0f);

            RenderSettings.skybox = LoadMatSafe("Environment/Skyboxes/kloofendal_48d_partly_cloudy_puresky");
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Skybox;
            RenderSettings.ambientIntensity = 0.85f;
            RenderSettings.fog = false;

            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            var cam = camGo.AddComponent<Camera>();
            camGo.transform.position = new Vector3(6.2f, 1.65f, -3.6f);
            camGo.transform.LookAt(new Vector3(0f, 1.15f, 2.2f));
            cam.fieldOfView = 52f;
            cam.farClipPlane = 200f;

            EditorSceneManager.SaveScene(scene, Root + "/Scenes/Showcase_Interior.unity");
            Debug.Log("[AssetLibrary] interior showcase scene saved");
        }
        // ------------------------------------------------------------------ thumbnails
        public static void RenderThumbnails()
        {
            var data = LoadData();
            string filter = (Environment.GetEnvironmentVariable("AL_THUMB_FILTER") ?? "").ToLowerInvariant();
            string outDir = Path.Combine(Directory.GetCurrentDirectory(), "Thumbnails");
            Directory.CreateDirectory(outDir);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            RenderSettings.skybox = MakeStudioSky();
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Skybox;
            RenderSettings.ambientIntensity = 1.1f;
            RenderSettings.fog = false;
            QualitySettings.shadowDistance = 80f;

            var keyGo = new GameObject("Key");
            var key = keyGo.AddComponent<Light>();
            key.type = LightType.Directional; key.intensity = 1.25f; key.color = new Color(1f, 0.96f, 0.9f);
            key.shadows = LightShadows.Soft;
            keyGo.transform.rotation = Quaternion.Euler(38f, -40f, 0f);

            var rimGo = new GameObject("Rim");
            var rim = rimGo.AddComponent<Light>();
            rim.type = LightType.Directional; rim.intensity = 0.5f; rim.color = new Color(0.6f, 0.72f, 1f);
            rim.shadows = LightShadows.None;
            rimGo.transform.rotation = Quaternion.Euler(-18f, 155f, 0f);

            var camGo = new GameObject("PreviewCamera");
            var cam = camGo.AddComponent<Camera>();
            cam.fieldOfView = 32f;
            cam.nearClipPlane = 0.01f;
            cam.farClipPlane = 200f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.105f, 0.115f, 0.135f);
            cam.allowHDR = false;
            cam.orthographic = false;

            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "PreviewGround";
            ground.transform.localScale = new Vector3(8f, 1f, 8f);
            var gm = new Material(Shader.Find("Standard"));
            gm.color = new Color(0.19f, 0.20f, 0.22f);
            gm.SetFloat("_Glossiness", 0.15f);
            ground.GetComponent<Renderer>().sharedMaterial = gm;

            int pw = 512, ph = 512;
            var rt = new RenderTexture(pw, ph, 24, RenderTextureFormat.ARGB32);
            rt.antiAliasing = 4;
            cam.targetTexture = rt;

            int done = 0;
            foreach (var e in data.models)
            {
                if (filter.Length > 0 && !e.name.ToLowerInvariant().Contains(filter)) continue;
                if (Environment.GetEnvironmentVariable("AL_THUMB_FORCE") != "1" && File.Exists(Path.Combine(outDir, "model_" + e.name + ".png"))) continue;
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Prefabs/" + e.category + "/" + e.name + ".prefab");
                if (prefab == null) continue;
                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                go.transform.position = Vector3.zero;
                go.transform.rotation = Quaternion.Euler(0f, 25f, 0f);
                var b = RendererBounds(go);
                ground.transform.position = new Vector3(0f, b.min.y - 0.02f, 0f);
                Frame(cam, b, new Vector3(0.95f, 0.42f, -1f));
                SaveRT(rt, cam, Path.Combine(outDir, "model_" + e.name + ".png"));
                UnityEngine.Object.DestroyImmediate(go);
                done++;
            }
            foreach (var m in data.materials)
            {
                if (filter.Length > 0 && !m.name.ToLowerInvariant().Contains(filter)) continue;
                if (Environment.GetEnvironmentVariable("AL_THUMB_FORCE") != "1" && File.Exists(Path.Combine(outDir, "material_" + m.category + "_" + m.name + ".png"))) continue;
                var mat = AssetDatabase.LoadAssetAtPath<Material>(Root + "/" + m.path + "/" + m.name + ".mat");
                if (mat == null) continue;
                var sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                sphere.transform.localScale = Vector3.one * 2f;
                sphere.GetComponent<Renderer>().sharedMaterial = mat;
                var b = new Bounds(new Vector3(0f, 1f, 0f), Vector3.one * 2f);
                ground.transform.position = new Vector3(0f, -0.02f, 0f);
                Frame(cam, b, new Vector3(0.9f, 0.35f, -1f));
                SaveRT(rt, cam, Path.Combine(outDir, "material_" + m.category + "_" + m.name + ".png"));
                UnityEngine.Object.DestroyImmediate(sphere);
                done++;
            }
            foreach (var h in data.hdris)
            {
                if (filter.Length > 0 && !h.name.ToLowerInvariant().Contains(filter)) continue;
                if (Environment.GetEnvironmentVariable("AL_THUMB_FORCE") != "1" && File.Exists(Path.Combine(outDir, "hdri_" + h.name + ".png"))) continue;
                var sky = AssetDatabase.LoadAssetAtPath<Material>(Root + "/Environment/Skyboxes/" + h.name + ".mat");
                if (sky == null) continue;
                RenderSettings.skybox = sky;
                DynamicGI.UpdateEnvironment();
                cam.clearFlags = CameraClearFlags.Skybox;
                cam.transform.position = Vector3.zero;
                cam.transform.rotation = Quaternion.Euler(8f, 120f, 0f);
                SaveRT(rt, cam, Path.Combine(outDir, "hdri_" + h.name + ".png"));
                done++;
            }
            RenderSettings.skybox = MakeStudioSky();
            cam.targetTexture = null;
            UnityEngine.Object.DestroyImmediate(rt);
            Debug.Log("[AssetLibrary] thumbnails rendered: " + done);
        }

        static Material MakeStudioSky()
        {
            var sh = Shader.Find("Skybox/Procedural");
            var m = new Material(sh);
            m.SetFloat("_SunDisk", 0f);
            m.SetFloat("_SunSize", 0.04f);
            m.SetFloat("_AtmosphereThickness", 0.85f);
            m.SetColor("_SkyTint", new Color(0.45f, 0.55f, 0.7f));
            m.SetColor("_GroundColor", new Color(0.25f, 0.25f, 0.27f));
            m.SetFloat("_Exposure", 1.1f);
            return m;
        }

        static void Frame(Camera cam, Bounds b, Vector3 dir)
        {
            float halfFov = Mathf.Deg2Rad * cam.fieldOfView * 0.5f;
            float h = Mathf.Max(0.2f, b.size.y);
            float w = Mathf.Max(0.2f, Mathf.Max(b.size.x, b.size.z));
            float distH = h / (2f * Mathf.Tan(halfFov));
            float distW = w / (2f * Mathf.Tan(halfFov) * Mathf.Max(0.35f, cam.aspect));
            float dist = Mathf.Max(distH, distW) * 1.08f;
            cam.transform.position = b.center + dir.normalized * dist;
            cam.transform.LookAt(b.center);
        }

        static void SaveRT(RenderTexture rt, Camera cam, string path)
        {
            if (cam != null) cam.Render();
            var prev = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(rt.width, rt.height, TextureFormat.RGBA32, false);
            tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
            tex.Apply();
            RenderTexture.active = prev;
            File.WriteAllBytes(path, tex.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(tex);
        }

        // ------------------------------------------------------------------ entry points
        public static void BatchRenderInterior()
        {
            try
            {
                var scene = EditorSceneManager.OpenScene(Root + "/Scenes/Showcase_Interior.unity", OpenSceneMode.Single);
                var cam = Camera.main;
                if (cam == null) cam = UnityEngine.Object.FindObjectOfType<Camera>();
                string outDir = Path.Combine(Directory.GetCurrentDirectory(), "Screenshots");
                Directory.CreateDirectory(outDir);
                var rt = new RenderTexture(1600, 900, 24, RenderTextureFormat.ARGB32);
                rt.antiAliasing = 4;
                cam.targetTexture = rt;
                var shots = new[]
                {
                    new object[] { new Vector3(6.2f, 1.65f, -3.6f), new Vector3(0f, 1.15f, 2.2f), 52f, "interior_01_hero" },
                    new object[] { new Vector3(2.2f, 1.35f, -1.6f), new Vector3(-0.6f, 1.0f, 3.2f), 58f, "interior_02_sofa" },
                    new object[] { new Vector3(4.6f, 1.7f, 2.0f), new Vector3(-2.0f, 1.1f, 4.6f), 55f, "interior_03_shelf" },
                    new object[] { new Vector3(-4.2f, 1.8f, -3.0f), new Vector3(1.0f, 1.1f, 3.0f), 62f, "interior_04_wide" },
                };
                foreach (var s in shots)
                {
                    cam.transform.position = (Vector3)s[0];
                    cam.transform.LookAt((Vector3)s[1]);
                    cam.fieldOfView = (float)s[2];
                    SaveRT(rt, cam, Path.Combine(outDir, (string)s[3] + ".png"));
                    Debug.Log("[AssetLibrary] interior shot " + s[3]);
                }
                cam.targetTexture = null;
                UnityEngine.Object.DestroyImmediate(rt);
                Debug.Log("[AssetLibrary] INTERIOR_COMPLETE");
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[AssetLibrary] INTERIOR_FAILED " + ex);
                EditorApplication.Exit(1);
            }
        }
        public static void BatchRenderShowcase()
        {
            try
            {
                var scene = EditorSceneManager.OpenScene(Root + "/Scenes/Showcase.unity", OpenSceneMode.Single);
                var cam = Camera.main;
                if (cam == null) cam = UnityEngine.Object.FindObjectOfType<Camera>();
                string outDir = Path.Combine(Directory.GetCurrentDirectory(), "Screenshots");
                Directory.CreateDirectory(outDir);
                var rt = new RenderTexture(1600, 900, 24, RenderTextureFormat.ARGB32);
                rt.antiAliasing = 4;
                cam.targetTexture = rt;
                var shots = new[]
                {
                    new object[] { new Vector3(7.5f, 3.6f, -9.5f), new Vector3(0f, 2.2f, 1.5f), 55f, "showcase_01_hero" },
                    new object[] { new Vector3(-9f, 5.5f, 9f), new Vector3(0f, 1.6f, 0f), 55f, "showcase_02_wide" },
                    new object[] { new Vector3(5.5f, 1.7f, -7.0f), new Vector3(0.5f, 1.5f, 1.5f), 58f, "showcase_03_detail" },
                    new object[] { new Vector3(0f, 21f, -18f), new Vector3(0f, 0f, 0f), 45f, "showcase_04_overview" },
                };
                foreach (var s in shots)
                {
                    cam.transform.position = (Vector3)s[0];
                    cam.transform.LookAt((Vector3)s[1]);
                    cam.fieldOfView = (float)s[2];
                    SaveRT(rt, cam, Path.Combine(outDir, (string)s[3] + ".png"));
                    Debug.Log("[AssetLibrary] showcase shot " + s[3]);
                }
                cam.targetTexture = null;
                UnityEngine.Object.DestroyImmediate(rt);
                Debug.Log("[AssetLibrary] SHOWCASE_COMPLETE");
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[AssetLibrary] SHOWCASE_FAILED " + ex);
                EditorApplication.Exit(1);
            }
        }

        public static void BatchBuild()
        {
            try
            {
                PlayerSettings.colorSpace = ColorSpace.Linear;
                ImportAllCommitted();
                var data = LoadData();
                ApplyTextureSettings();
                BuildLibraryMaterials(data);
                BuildModelMaterials(data);
                BuildPrefabs(data);
                BuildSkyboxes(data);
                BuildShowcase(data);
                BuildShowcaseInterior(data);
                AssetDatabase.SaveAssets();
                Debug.Log("[AssetLibrary] BUILD_COMPLETE");
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[AssetLibrary] BUILD_FAILED " + ex);
                EditorApplication.Exit(1);
            }
        }

        public static void BatchThumbFilter()
        {
            try
            {
                RenderThumbnails();
                Debug.Log("[AssetLibrary] THUMBS_COMPLETE");
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[AssetLibrary] THUMBS_FAILED " + ex);
                EditorApplication.Exit(1);
            }
        }

        public static void BatchThumbnails()
        {
            try
            {
                RenderThumbnails();
                Debug.Log("[AssetLibrary] THUMBS_COMPLETE");
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[AssetLibrary] THUMBS_FAILED " + ex);
                EditorApplication.Exit(1);
            }
        }

        public static void BatchExportPackage()
        {
            try
            {
                AssetDatabase.ExportPackage(new[] { Root }, "AssetLibrary_v1.0.unitypackage",
                    ExportPackageOptions.IncludeDependencies | ExportPackageOptions.Recurse);
                Debug.Log("[AssetLibrary] PACKAGE_COMPLETE");
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[AssetLibrary] PACKAGE_FAILED " + ex);
                EditorApplication.Exit(1);
            }
        }

        [MenuItem("Tools/Asset Library/Rebuild Everything")]
        public static void MenuRebuild()
        {
            var data = LoadData();
            ImportAllCommitted();
            ApplyTextureSettings();
            BuildLibraryMaterials(data);
            BuildModelMaterials(data);
            BuildPrefabs(data);
            BuildSkyboxes(data);
            BuildShowcase(data);
            AssetDatabase.SaveAssets();
        }
    }
}











