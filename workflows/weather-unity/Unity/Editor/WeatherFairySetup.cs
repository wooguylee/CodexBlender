using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace WeatherFairies.Editor
{
    public static class WeatherFairySetup
    {
        public const string Root = "Assets/WeatherFairies";
        public static readonly string[] Names = { "Mongsil", "Haerong", "Ttorr", "Songsong", "Solsol" };
        [Serializable] class MaterialSpec { public string name; public string character; public float[] linear_rgba; public float roughness; public float metallic; }
        [Serializable] class MaterialList { public MaterialSpec[] materials; }
        [Serializable] public class CharacterCheck
        {
            public string name; public int skinnedMeshes, bones, blendShapes, vertices; public bool validAvatar;
            public string[] clips; public float[] size; public float[] min; public float sampleMovement;
            public int animatedTransformCurves, animatedShapeCurves; public bool materialsValid; public float maxFaceWeightChange;
        }
        [Serializable] public class Report { public bool ok; public string unityVersion; public CharacterCheck[] characters; }

        static void Folder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path).Replace('\\', '/');
            Folder(parent); AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }

        [MenuItem("Tools/Weather Fairies/Prepare Models and Prefabs")]
        public static void BuildAssets()
        {
            foreach (string folder in new[] { "Materials", "Prefabs", "Controllers", "Scenes" }) Folder(Root + "/" + folder);
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) throw new InvalidOperationException("These materials require Universal Render Pipeline/Lit.");
            var specs = JsonUtility.FromJson<MaterialList>(File.ReadAllText(Root + "/material-manifest.json")).materials;
            foreach (var spec in specs)
            {
                string path = Root + "/Materials/" + spec.name + ".mat";
                var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (material == null) { material = new Material(shader); AssetDatabase.CreateAsset(material, path); }
                material.shader = shader;
                Color linear = new Color(spec.linear_rgba[0], spec.linear_rgba[1], spec.linear_rgba[2], spec.linear_rgba[3]);
                material.SetColor("_BaseColor", linear.gamma);
                material.SetFloat("_Smoothness", 1f - spec.roughness); material.SetFloat("_Metallic", spec.metallic);
                EditorUtility.SetDirty(material);
            }
            AssetDatabase.SaveAssets();
            foreach (string name in Names)
            {
                string path = Root + "/Models/" + name + ".fbx";
                AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
                var importer = (ModelImporter)AssetImporter.GetAtPath(path);
                importer.animationType = ModelImporterAnimationType.Generic;
                importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
                importer.motionNodeName = "CTRL_Root";
                importer.importAnimation = true; importer.importBlendShapes = true; importer.importBlendShapeDeformPercent = true;
                importer.importNormals = ModelImporterNormals.Import; importer.importBlendShapeNormals = ModelImporterNormals.Calculate;
                importer.importCameras = false; importer.importLights = false; importer.importVisibility = false;
                importer.animationCompression = ModelImporterAnimationCompression.Off;
                importer.optimizeGameObjects = false; importer.optimizeBones = false; importer.preserveHierarchy = true;
                importer.isReadable = true; importer.weldVertices = false; importer.globalScale = 1f; importer.useFileScale = true;
                importer.bakeAxisConversion = true; importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
                importer.SaveAndReimport();
                string take = importer.defaultClipAnimations[0].takeName;
                float firstFrame = importer.defaultClipAnimations[0].firstFrame;
                string[] clipNames = { "RigDemo", "Idle", "HandsIK", "Expressions", "Weather", "Special" };
                int[] first = { 0, 0, 48, 120, 192, 288 }; int[] last = { 383, 47, 119, 191, 287, 383 };
                importer.clipAnimations = clipNames.Select((clip, i) => new ModelImporterClipAnimation
                { name = clip, takeName = take, firstFrame = firstFrame + first[i], lastFrame = firstFrame + last[i], loopTime = clip == "Idle",
                  keepOriginalOrientation = true, keepOriginalPositionY = true, keepOriginalPositionXZ = true,
                  lockRootRotation = true, lockRootHeightY = true, lockRootPositionXZ = true }).ToArray();
                foreach (var spec in specs.Where(s => s.character == name))
                    importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), spec.name), AssetDatabase.LoadAssetAtPath<Material>(Root + "/Materials/" + spec.name + ".mat"));
                importer.SaveAndReimport();
                var clips = AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__")).ToArray();
                string controllerPath = Root + "/Controllers/" + name + ".controller";
                var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);
                if (controller == null)
                {
                    controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
                    var machine = controller.layers[0].stateMachine;
                    foreach (var clip in clips) { var state = machine.AddState(clip.name); state.motion = clip; if (clip.name == "RigDemo") machine.defaultState = state; }
                }
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                var tempScene = EditorSceneManager.NewPreviewScene();
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, tempScene); instance.name = name;
                var animator = instance.GetComponent<Animator>(); animator.runtimeAnimatorController = controller; animator.applyRootMotion = false;
                var face = instance.AddComponent<WeatherFairyExpressions>(); face.Apply();
                foreach (var renderer in instance.GetComponentsInChildren<SkinnedMeshRenderer>()) renderer.updateWhenOffscreen = true;
                PrefabUtility.SaveAsPrefabAsset(instance, Root + "/Prefabs/" + name + ".prefab");
                UnityEngine.Object.DestroyImmediate(instance);
                EditorSceneManager.ClosePreviewScene(tempScene);
            }
            AssetDatabase.SaveAssets();
        }

        static Vector3[] VertexSample(GameObject instance)
        {
            var list = new List<Vector3>();
            foreach (var renderer in instance.GetComponentsInChildren<SkinnedMeshRenderer>())
            {
                var mesh = new Mesh(); renderer.BakeMesh(mesh);
                foreach (var p in mesh.vertices) list.Add(renderer.transform.TransformPoint(p));
                UnityEngine.Object.DestroyImmediate(mesh);
            }
            return list.ToArray();
        }

        public static string Verify(string outputDirectory)
        {
            Directory.CreateDirectory(outputDirectory); var checks = new List<CharacterCheck>();
            var preview = EditorSceneManager.NewPreviewScene();
            try
            {
                foreach (var name in Names)
                {
                    var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Prefabs/" + name + ".prefab");
                    if (prefab == null) throw new Exception("Missing prefab " + name);
                    var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab, preview);
                    var animator = instance.GetComponent<Animator>(); var renderers = instance.GetComponentsInChildren<SkinnedMeshRenderer>();
                    var clips = AssetDatabase.LoadAllAssetsAtPath(Root + "/Models/" + name + ".fbx").OfType<AnimationClip>().Where(c => !c.name.StartsWith("__")).ToArray();
                    var demo = clips.Single(c => c.name == "RigDemo");
                    demo.SampleAnimation(instance, 0); var before = VertexSample(instance);
                    var bounds = new Bounds(before[0], Vector3.zero); foreach (var p in before) bounds.Encapsulate(p);
                    demo.SampleAnimation(instance, 10.1f); var after = VertexSample(instance);
                    float movement = before.Zip(after, (a, b) => Vector3.Distance(a, b)).Max();
                    if (movement < .02f || bounds.size.y < 1 || bounds.size.y > 6 || Mathf.Abs(bounds.min.y) > .005f) throw new Exception("Bad motion/scale/ground pivot: " + name + " y=" + bounds.min.y);
                    if (!animator.avatar.isValid || animator.avatar.isHuman) throw new Exception("Invalid Generic avatar: " + name);
                    if (renderers.Any(r => r.bones.Length == 0 || r.bones.Any(b => b == null))) throw new Exception("Broken skin bones: " + name);
                    bool materialsOK = renderers.All(r => r.sharedMaterials.All(m => m != null && m.shader.name == "Universal Render Pipeline/Lit"));
                    if (!materialsOK) throw new Exception("Invalid materials: " + name);
                    var bindings = AnimationUtility.GetCurveBindings(demo);
                    int shapeCurves = bindings.Count(b => b.propertyName.StartsWith("blendShape."));
                    if (shapeCurves == 0) throw new Exception("Missing facial animation: " + name);
                    float faceChange = bindings.Where(b => b.propertyName.StartsWith("blendShape.")).Select(b =>
                    { var curve = AnimationUtility.GetEditorCurve(demo, b); return Mathf.Abs(curve.Evaluate(7.4f) - curve.Evaluate(0)); }).Max();
                    if (faceChange < 90) throw new Exception("Frozen facial animation: " + name);
                    checks.Add(new CharacterCheck { name = name, skinnedMeshes = renderers.Length, bones = instance.GetComponentsInChildren<Transform>().Count(t => t.name.StartsWith("CTRL_") || t.name.StartsWith("DEF_") || t.name.StartsWith("MCH_")),
                        blendShapes = renderers.Sum(r => r.sharedMesh.blendShapeCount), vertices = before.Length, validAvatar = true,
                        clips = clips.Select(c => c.name).ToArray(), size = new[] { bounds.size.x, bounds.size.y, bounds.size.z }, min = new[] { bounds.min.x, bounds.min.y, bounds.min.z },
                        sampleMovement = movement, animatedShapeCurves = shapeCurves, animatedTransformCurves = bindings.Count(b => b.type == typeof(Transform)), materialsValid = materialsOK, maxFaceWeightChange = faceChange });
                    var face = instance.GetComponent<WeatherFairyExpressions>(); face.manualExpressions = true; face.awake = 1; face.surprise = 1; face.Apply();
                    if (!renderers.Any(r => Enumerable.Range(0, r.sharedMesh.blendShapeCount).Any(i => r.sharedMesh.GetBlendShapeName(i).EndsWith("SurpriseHide") && r.GetBlendShapeWeight(i) > 99))) throw new Exception("Live face failed: " + name);
                    UnityEngine.Object.DestroyImmediate(instance);
                }
            }
            finally { EditorSceneManager.ClosePreviewScene(preview); }
            var report = new Report { ok = true, unityVersion = Application.unityVersion, characters = checks.ToArray() };
            string json = JsonUtility.ToJson(report, true); File.WriteAllText(Path.Combine(outputDirectory, "unity-verification.json"), json); return json;
        }

        [MenuItem("Tools/Weather Fairies/Create Showcase Scene")]
        public static void CreateShowcase()
        {
            string path = Root + "/Scenes/WeatherFairiesShowcase.unity";
            if (File.Exists(path)) throw new InvalidOperationException("Showcase already exists; open it instead.");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive); SceneManager.SetActiveScene(scene);
            RenderSettings.ambientMode = AmbientMode.Flat; RenderSettings.ambientLight = new Color(.65f, .65f, .65f);
            for (int i = 0; i < Names.Length; ++i)
            {
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Prefabs/" + Names[i] + ".prefab");
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene); instance.transform.position = new Vector3((i - 2) * 3.2f, 0, 0);
            }
            foreach (var pair in new[] { new Vector3(35, -35, 0), new Vector3(55, 145, 0) })
            { var light = new GameObject("Studio Light").AddComponent<Light>(); light.type = LightType.Directional; light.intensity = .9f; light.transform.rotation = Quaternion.Euler(pair); light.shadows = LightShadows.None; }
            var camera = new GameObject("Weather Showcase Camera").AddComponent<Camera>(); camera.tag = "MainCamera";
            camera.transform.position = new Vector3(0, 5, -18); camera.transform.LookAt(new Vector3(0, 1.5f, 0)); camera.orthographic = true; camera.orthographicSize = 5;
            camera.clearFlags = CameraClearFlags.SolidColor; camera.backgroundColor = new Color(.86f, .84f, .89f);
            camera.gameObject.AddComponent<AudioListener>();
            ConfigureShowcase();
            EditorSceneManager.SaveScene(scene, path); AssetDatabase.SaveAssets();
        }

        public static void ConfigureShowcase()
        {
            var scene = SceneManager.GetActiveScene();
            if (scene.name != "WeatherFairiesShowcase" && !scene.GetRootGameObjects().Any(o => o.name == "Weather Showcase Camera")) throw new Exception("Select the Weather Fairies showcase scene first.");
            Folder(Root + "/Settings");
            string profilePath = Root + "/Settings/ShowcaseTone.asset";
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(profilePath);
            if (profile == null) { profile = ScriptableObject.CreateInstance<VolumeProfile>(); AssetDatabase.CreateAsset(profile, profilePath); }
            Tonemapping tone;
            if (!profile.TryGet<Tonemapping>(out tone)) { tone = profile.Add<Tonemapping>(true); AssetDatabase.AddObjectToAsset(tone, profile); }
            tone.mode.Override(TonemappingMode.ACES);
            var volume = scene.GetRootGameObjects().Select(o => o.GetComponent<Volume>()).FirstOrDefault(v => v != null);
            if (volume == null) volume = new GameObject("Weather Tone Mapping").AddComponent<Volume>();
            volume.isGlobal = true; volume.sharedProfile = profile;
            foreach (var light in scene.GetRootGameObjects().SelectMany(o => o.GetComponentsInChildren<Light>())) light.intensity = .8f;
            var camera = scene.GetRootGameObjects().SelectMany(o => o.GetComponentsInChildren<Camera>()).Single();
            camera.transform.position = new Vector3(0, 5, -18); camera.transform.LookAt(new Vector3(0, 1.5f, 0)); camera.allowHDR = true;
            camera.GetUniversalAdditionalCameraData().renderPostProcessing = true;
            EditorUtility.SetDirty(profile); AssetDatabase.SaveAssets();
        }

        public static void RenderShowcase(string outputPath, float seconds)
        {
            var scene = SceneManager.GetSceneByPath(Root + "/Scenes/WeatherFairiesShowcase.unity");
            if (!scene.isLoaded) scene = EditorSceneManager.OpenScene(Root + "/Scenes/WeatherFairiesShowcase.unity", OpenSceneMode.Additive);
            foreach (var root in scene.GetRootGameObjects())
            {
                if (!Names.Contains(root.name)) continue;
                Vector3 position = root.transform.position;
                var clip = AssetDatabase.LoadAllAssetsAtPath(Root + "/Models/" + root.name + ".fbx").OfType<AnimationClip>().Single(c => c.name == "RigDemo");
                clip.SampleAnimation(root, seconds); root.transform.position = position;
            }
            var camera = scene.GetRootGameObjects().SelectMany(o => o.GetComponentsInChildren<Camera>()).Single();
            var target = new RenderTexture(1920, 1080, 24, RenderTextureFormat.ARGBHalf); target.antiAliasing = 4;
            var skins = scene.GetRootGameObjects().SelectMany(o => o.GetComponentsInChildren<SkinnedMeshRenderer>()).ToArray();
            var previousForce = skins.Select(s => s.forceMatrixRecalculationPerRender).ToArray();
            var previous = RenderTexture.active; var previousTarget = camera.targetTexture;
            Texture2D image = null;
            try
            {
                // Several SampleAnimation calls can occur within one Editor frame.
                foreach (var skin in skins) skin.forceMatrixRecalculationPerRender = true;
                camera.targetTexture = target; camera.Render(); RenderTexture.active = target;
                image = new Texture2D(1920, 1080, TextureFormat.RGB24, false); image.ReadPixels(new Rect(0, 0, 1920, 1080), 0, 0); image.Apply();
                File.WriteAllBytes(outputPath, image.EncodeToPNG());
            }
            finally
            {
                for (int i = 0; i < skins.Length; i++) skins[i].forceMatrixRecalculationPerRender = previousForce[i];
                camera.targetTexture = previousTarget; RenderTexture.active = previous;
                if (image != null) UnityEngine.Object.DestroyImmediate(image);
                target.Release(); UnityEngine.Object.DestroyImmediate(target);
            }
        }

        public static void ExportPackage(string outputPath)
        {
            AssetDatabase.ExportPackage(new[] { Root, "Assets/Scripts/WeatherFairies" }, outputPath, ExportPackageOptions.Recurse);
        }
    }
}
