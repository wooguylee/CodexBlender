using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;

namespace StorybookCast.Editor
{
    [Serializable] public class MaterialSpec { public string name; public float[] linear_rgba; public float roughness, metallic; }
    [Serializable] public class ShoulderSpec { public string side, body_bone; public float[] root_points; }
    [Serializable] public class CharacterSpec { public string key, ko, role, theme, motion_style; public int bones, vertices, shapes; public MaterialSpec[] materials; public ShoulderSpec[] shoulders; }
    [Serializable] public class ClipSpec { public string name; public int first, last, fps; public bool loop; }
    [Serializable] public class ThemeSpec { public string key, ko, color; }
    [Serializable] public class Catalog { public ThemeSpec[] themes; public CharacterSpec[] characters; public ClipSpec[] clips; }

    public static class StorybookAssets
    {
        public const string Root = "Assets/StorybookCast";
        public static Catalog ReadCatalog() { return JsonUtility.FromJson<Catalog>(File.ReadAllText(Root + "/catalog.json")); }
        public static string ThemeRoot(string theme)
        {
            if (!ReadCatalog().themes.Any(t => t.key == theme)) throw new ArgumentException("Unknown theme: " + theme);
            return Root + "/Themes/" + theme;
        }
        public static void Folder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path).Replace('\\', '/'); Folder(parent); AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }
        public static AnimationClip[] Clips(CharacterSpec spec)
        { return AssetDatabase.LoadAllAssetsAtPath(ThemeRoot(spec.theme) + "/Models/" + spec.key + ".fbx").OfType<AnimationClip>().Where(c => !c.name.StartsWith("__")).ToArray(); }

        [MenuItem("Tools/Storybook Cast/Prepare Imported Themes")]
        public static void BuildImported()
        {
            foreach (var theme in ReadCatalog().themes)
                if (Directory.Exists(ThemeRoot(theme.key) + "/Models")) BuildTheme(theme.key);
        }
        public static void BuildTheme(string theme)
        {
            var catalog = ReadCatalog(); string root = ThemeRoot(theme);
            foreach (string folder in new[] { "Materials", "Prefabs", "Controllers", "Scenes" }) Folder(root + "/" + folder);
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) throw new InvalidOperationException("Storybook Cast materials require URP/Lit.");
            foreach (var spec in catalog.characters.Where(c => c.theme == theme))
            {
                foreach (var m in spec.materials)
                {
                    string path = root + "/Materials/" + m.name + ".mat";
                    var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                    if (material == null) { material = new Material(shader); AssetDatabase.CreateAsset(material, path); }
                    material.shader = shader; material.SetColor("_BaseColor", new Color(m.linear_rgba[0], m.linear_rgba[1], m.linear_rgba[2], m.linear_rgba[3]).gamma);
                    material.SetFloat("_Smoothness", 1f - m.roughness); material.SetFloat("_Metallic", m.metallic); EditorUtility.SetDirty(material);
                }
                AssetDatabase.SaveAssets();
                string modelPath = root + "/Models/" + spec.key + ".fbx";
                AssetDatabase.ImportAsset(modelPath, ImportAssetOptions.ForceSynchronousImport);
                var importer = (ModelImporter)AssetImporter.GetAtPath(modelPath);
                importer.animationType = ModelImporterAnimationType.Generic; importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
                importer.motionNodeName = "CTRL_Root"; importer.importAnimation = true; importer.importBlendShapes = true; importer.importBlendShapeDeformPercent = true;
                importer.importNormals = ModelImporterNormals.Import; importer.importBlendShapeNormals = ModelImporterNormals.Calculate;
                importer.importCameras = false; importer.importLights = false; importer.importVisibility = false;
                importer.animationCompression = ModelImporterAnimationCompression.Off; importer.optimizeGameObjects = false; importer.optimizeBones = false;
                importer.preserveHierarchy = true; importer.isReadable = true; importer.weldVertices = false; importer.globalScale = 1f; importer.useFileScale = true;
                importer.bakeAxisConversion = true; importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
                importer.SaveAndReimport(); var take = importer.defaultClipAnimations[0];
                importer.clipAnimations = catalog.clips.Select(c => new ModelImporterClipAnimation {
                    name = c.name, takeName = take.takeName, firstFrame = take.firstFrame + c.first - 1, lastFrame = take.firstFrame + c.last - 1,
                    loopTime = c.loop, keepOriginalOrientation = true, keepOriginalPositionY = true, keepOriginalPositionXZ = true,
                    lockRootRotation = true, lockRootHeightY = true, lockRootPositionXZ = true }).ToArray();
                foreach (var m in spec.materials) importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), m.name), AssetDatabase.LoadAssetAtPath<Material>(root + "/Materials/" + m.name + ".mat"));
                importer.SaveAndReimport();
                string controllerPath = root + "/Controllers/" + spec.key + ".controller";
                var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);
                if (controller == null)
                {
                    controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath); var machine = controller.layers[0].stateMachine;
                    var states = new Dictionary<string, AnimatorState>();
                    foreach (var clip in Clips(spec)) { var state = machine.AddState(clip.name); state.motion = clip; states.Add(clip.name, state); }
                    machine.defaultState = states["Idle"];
                    foreach (string from in new[] { "SitDown", "StandUp", "Wave", "Celebrate" })
                    { var transition = states[from].AddTransition(states[from == "SitDown" ? "SitIdle" : "Idle"]); transition.hasExitTime = true; transition.exitTime = 1f; transition.hasFixedDuration = true; transition.duration = .12f; }
                }
                // Keep existing asset GUIDs while refreshing clip sub-assets after
                // a rebuilt FBX changes its internal object hierarchy.
                var importedClips = Clips(spec).ToDictionary(c => c.name);
                foreach (var state in controller.layers[0].stateMachine.states)
                    if (importedClips.ContainsKey(state.state.name)) state.state.motion = importedClips[state.state.name];
                EditorUtility.SetDirty(controller);
                var preview = EditorSceneManager.NewPreviewScene();
                try
                {
                    var instance = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(modelPath), preview); instance.name = spec.key;
                    var animator = instance.GetComponent<Animator>(); animator.runtimeAnimatorController = controller; animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
                    var character = instance.AddComponent<StorybookCharacter>(); character.characterKey = spec.key; character.koreanName = spec.ko; character.role = spec.role;
                    foreach (var skin in instance.GetComponentsInChildren<SkinnedMeshRenderer>()) skin.updateWhenOffscreen = true;
                    PrefabUtility.SaveAsPrefabAsset(instance, root + "/Prefabs/" + spec.key + ".prefab");
                }
                finally { EditorSceneManager.ClosePreviewScene(preview); }
            }
            AssetDatabase.SaveAssets();
        }
        public static void ExportTheme(string theme, string outputPath)
        { AssetDatabase.ExportPackage(new[] { ThemeRoot(theme), Root + "/catalog.json", "Assets/Scripts/StorybookCast" }, outputPath, ExportPackageOptions.Recurse); }
        public static void ExportAll(string outputPath)
        { AssetDatabase.ExportPackage(new[] { Root, "Assets/Scripts/StorybookCast" }, outputPath, ExportPackageOptions.Recurse); }
    }
}
