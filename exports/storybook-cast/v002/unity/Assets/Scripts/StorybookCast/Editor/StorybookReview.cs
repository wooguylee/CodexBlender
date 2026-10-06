using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace StorybookCast.Editor
{
    // Asset-level checks and isolated render scenes; never save another user's scene.
    public static class StorybookReview
    {
        [Serializable] public class ClipCheck { public string name; public float seconds, loopError, maxMovement, minY, maxY; public int curves; }
        [Serializable] public class CharacterCheck { public string key; public int vertices, bones, shapes, materials; public float seatedDrop, blinkRange; public ClipCheck[] clips; }
        [Serializable] public class Report { public bool ok; public string unity, theme; public CharacterCheck[] characters; }
        [Serializable] public class RuntimeCheck { public string key; public string[] states; public bool sitTransition; public float walkMovement; public float[] faceWeights; }
        [Serializable] public class RuntimeReport { public bool ok; public string unity; public RuntimeCheck[] characters; }
        static void Require(bool pass, string message) { if (!pass) throw new InvalidOperationException(message); }
        static Vector3[] Vertices(SkinnedMeshRenderer skin)
        {
            var mesh = new Mesh();
            try { skin.BakeMesh(mesh); return mesh.vertices.Select(v => skin.transform.TransformPoint(v)).ToArray(); }
            finally { UnityEngine.Object.DestroyImmediate(mesh); }
        }
        static float Delta(Vector3[] a, Vector3[] b)
        { Require(a.Length == b.Length, "Vertex count changed"); float d = 0; for (int i = 0; i < a.Length; i++) d = Mathf.Max(d, Vector3.Distance(a[i], b[i])); return d; }
        public static string VerifyPlaying(string outputPath)
        {
            Require(Application.isPlaying, "Enter Play mode in an owned Storybook showcase first");
            Require(SceneManager.GetActiveScene().path.StartsWith(StorybookAssets.Root + "/Themes/"), "Expected owned scene");
            foreach (var demo in UnityEngine.Object.FindObjectsByType<StorybookDemo>(FindObjectsSortMode.None)) demo.autoCycle = false;
            var results = new List<RuntimeCheck>();
            foreach (var spec in StorybookAssets.ReadCatalog().characters)
            {
                var actor = UnityEngine.Object.FindObjectsByType<StorybookCharacter>(FindObjectsSortMode.None).FirstOrDefault(c => c.characterKey == spec.key);
                if (actor == null) actor = UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(StorybookAssets.ThemeRoot(spec.theme) + "/Prefabs/" + spec.key + ".prefab")).GetComponent<StorybookCharacter>();
                var animator = actor.GetComponent<Animator>(); animator.Rebind(); animator.Update(0);
                var states = new List<string>();
                foreach (CastMotion state in Enum.GetValues(typeof(CastMotion)))
                {
                    actor.Play(state); animator.Update(0); animator.Update(.25f);
                    Require(animator.GetCurrentAnimatorStateInfo(0).IsName(state.ToString()), spec.key + ": runtime state " + state); states.Add(state.ToString());
                }
                var skin = actor.GetComponentInChildren<SkinnedMeshRenderer>(); actor.Play(CastMotion.Walk); animator.Update(0); animator.Update(.31f); var before = Vertices(skin); animator.Update(.37f); float movement = Delta(before, Vertices(skin)); Require(movement > .001f, spec.key + ": frozen Play skin");
                animator.Play("SitDown"); animator.Update(0); animator.Update(1.6f); animator.Update(.3f); bool seated = animator.GetCurrentAnimatorStateInfo(0).IsName("SitIdle"); Require(seated, spec.key + ": automatic SitIdle transition");
                actor.manualFace = true; actor.blink = .4f; actor.smile = .6f; actor.surprise = .25f; actor.SendMessage("LateUpdate");
                var weights = new float[3]; string[] names = { "Blink", "Smile", "Surprise" }; float[] expected = { 40, 45, 25 };
                for (int i = 0; i < 3; i++) { int index = Enumerable.Range(0, skin.sharedMesh.blendShapeCount).Single(n => skin.sharedMesh.GetBlendShapeName(n).EndsWith(names[i])); weights[i] = skin.GetBlendShapeWeight(index); Require(Mathf.Abs(weights[i] - expected[i]) < .01f, spec.key + ": manual face"); }
                actor.manualFace = false; actor.Play(CastMotion.Idle);
                results.Add(new RuntimeCheck { key = spec.key, states = states.ToArray(), sitTransition = seated, walkMovement = movement, faceWeights = weights });
            }
            Require(results.Count == 20, "Expected twenty live actors"); var report = new RuntimeReport { ok = true, unity = Application.unityVersion, characters = results.ToArray() }; string json = JsonUtility.ToJson(report, true); File.WriteAllText(outputPath, json); return "20 live actors: 160 states, skinned movement, sitting transitions and manual faces passed";
        }
        public static string VerifyTheme(string theme, string outputDirectory)
        {
            Directory.CreateDirectory(outputDirectory); var results = new List<CharacterCheck>();
            var scene = EditorSceneManager.NewPreviewScene();
            try
            {
                foreach (var spec in StorybookAssets.ReadCatalog().characters.Where(c => c.theme == theme))
                {
                    var instance = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(StorybookAssets.ThemeRoot(theme) + "/Prefabs/" + spec.key + ".prefab"), scene);
                    try
                    {
                        var skins = instance.GetComponentsInChildren<SkinnedMeshRenderer>(); Require(skins.Length == 1, spec.key + ": expected one skin"); var skin = skins[0];
                        Require(skin.bones.All(b => b != null), spec.key + ": missing bone"); Require(skin.sharedMesh.blendShapeCount == 3, spec.key + ": shape count");
                        Require(skin.sharedMaterials.All(m => m != null && m.shader.name == "Universal Render Pipeline/Lit"), spec.key + ": material mapping");
                        var animator = instance.GetComponent<Animator>(); Require(animator.avatar != null && animator.avatar.isValid && !animator.avatar.isHuman, spec.key + ": Generic avatar");
                        var clips = StorybookAssets.Clips(spec); Require(clips.Length == 8, spec.key + ": clip count"); var checks = new List<ClipCheck>();
                        float idleTop = 0, seatTop = 0, blinkRange = 0;
                        foreach (var clip in clips)
                        {
                            clip.SampleAnimation(instance, 0); var first = Vertices(skin); float low = first.Min(v => v.y), high = first.Max(v => v.y), movement = 0;
                            foreach (float f in new[] { .125f, .25f, .5f, .75f, .875f, 1f })
                            {
                                clip.SampleAnimation(instance, clip.length * f); var sample = Vertices(skin);
                                Require(sample.All(v => !float.IsNaN(v.x) && !float.IsNaN(v.y) && !float.IsNaN(v.z) && !float.IsInfinity(v.sqrMagnitude)), spec.key + ": invalid vertex");
                                movement = Mathf.Max(movement, Delta(first, sample)); low = Mathf.Min(low, sample.Min(v => v.y)); high = Mathf.Max(high, sample.Max(v => v.y));
                            }
                            float loopError = Delta(first, Vertices(skin)); var def = StorybookAssets.ReadCatalog().clips.Single(c => c.name == clip.name);
                            Require(!def.loop || loopError < .002f, spec.key + "/" + clip.name + ": loop mismatch " + loopError);
                            Require(low > -.006f, spec.key + "/" + clip.name + ": below floor " + low);
                            if (clip.name == "Walk" || clip.name == "Run") Require(movement > .025f, spec.key + "/" + clip.name + ": frozen animation");
                            clip.SampleAnimation(instance, 0); if (clip.name == "Idle") idleTop = Vertices(skin).Max(v => v.y); if (clip.name == "SitIdle") seatTop = Vertices(skin).Max(v => v.y);
                            var bindings = AnimationUtility.GetCurveBindings(clip);
                            foreach (var binding in bindings.Where(b => b.propertyName.EndsWith("Blink")))
                            { var curve = AnimationUtility.GetEditorCurve(clip, binding); blinkRange = Mathf.Max(blinkRange, curve.keys.Max(k => k.value) - curve.keys.Min(k => k.value)); }
                            checks.Add(new ClipCheck { name = clip.name, seconds = clip.length, curves = bindings.Length, loopError = loopError, maxMovement = movement, minY = low, maxY = high });
                        }
                        Require(idleTop - seatTop > .05f, spec.key + ": sitting height unchanged " + (idleTop - seatTop)); Require(blinkRange > 80, spec.key + ": blink missing");
                        results.Add(new CharacterCheck { key = spec.key, vertices = skin.sharedMesh.vertexCount, bones = skin.bones.Length, shapes = skin.sharedMesh.blendShapeCount, materials = skin.sharedMaterials.Length, seatedDrop = idleTop - seatTop, blinkRange = blinkRange, clips = checks.ToArray() });
                    }
                    finally { UnityEngine.Object.DestroyImmediate(instance); }
                }
            }
            finally { EditorSceneManager.ClosePreviewScene(scene); }
            Require(results.Count == 5, "Expected five characters"); var report = new Report { ok = true, theme = theme, unity = Application.unityVersion, characters = results.ToArray() };
            string json = JsonUtility.ToJson(report, true); File.WriteAllText(Path.Combine(outputDirectory, theme + "-unity-verification.json"), json); return json;
        }
        static GameObject NewObject(string name, Scene scene)
        { var go = new GameObject(name); SceneManager.MoveGameObjectToScene(go, scene); return go; }
        static Camera Populate(Scene scene, string theme)
        {
            var catalog = StorybookAssets.ReadCatalog(); var specs = catalog.characters.Where(c => c.theme == theme).ToArray();
            var actors = new StorybookCharacter[specs.Length];
            for (int i = 0; i < specs.Length; i++)
            {
                var obj = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(StorybookAssets.ThemeRoot(theme) + "/Prefabs/" + specs[i].key + ".prefab"), scene);
                obj.transform.position = new Vector3((i - 2) * 3.15f, 0, 0); actors[i] = obj.GetComponent<StorybookCharacter>();
            }
            var demo = NewObject("Storybook Motion Demo", scene).AddComponent<StorybookDemo>(); demo.theme = theme; demo.actors = actors;
            int n = 0;
            foreach (var rotation in new[] { new Vector3(35, -35, 0), new Vector3(55, 145, 0) })
            { var light = NewObject("Studio Light " + n, scene).AddComponent<Light>(); light.type = LightType.Directional; light.intensity = n++ == 0 ? .9f : .55f; light.transform.rotation = Quaternion.Euler(rotation); light.shadows = LightShadows.None; }
            var camera = NewObject("Storybook Camera", scene).AddComponent<Camera>(); camera.tag = "MainCamera"; camera.scene = scene;
            camera.transform.position = new Vector3(0, 4.9f, -18); camera.transform.LookAt(new Vector3(0, 1.5f, 0)); camera.orthographic = true; camera.orthographicSize = 4.65f;
            camera.clearFlags = CameraClearFlags.SolidColor; Color color; ColorUtility.TryParseHtmlString("#" + catalog.themes.Single(t => t.key == theme).color, out color); camera.backgroundColor = color;
            camera.allowHDR = true; camera.gameObject.AddComponent<AudioListener>(); camera.GetUniversalAdditionalCameraData().renderPostProcessing = true;
            string profilePath = StorybookAssets.ThemeRoot(theme) + "/Materials/ShowcaseTone.asset";
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(profilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>(); AssetDatabase.CreateAsset(profile, profilePath); var tone = profile.Add<Tonemapping>(true); tone.mode.Override(TonemappingMode.ACES); AssetDatabase.AddObjectToAsset(tone, profile); EditorUtility.SetDirty(profile); AssetDatabase.SaveAssets();
            }
            var volume = NewObject("Storybook Tone", scene).AddComponent<Volume>(); volume.isGlobal = true; volume.priority = 100; volume.sharedProfile = profile;
            return camera;
        }
        public static void CreateShowcase(string theme)
        {
            string path = StorybookAssets.ThemeRoot(theme) + "/Scenes/" + theme + "Showcase.unity"; Require(!File.Exists(path), "Showcase exists: " + path);
            var previous = SceneManager.GetActiveScene(); var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
            try { SceneManager.SetActiveScene(scene); RenderSettings.ambientMode = AmbientMode.Flat; RenderSettings.ambientLight = new Color(.4f, .4f, .4f); Populate(scene, theme); EditorSceneManager.SaveScene(scene, path); }
            finally { SceneManager.SetActiveScene(previous); EditorSceneManager.CloseScene(scene, true); }
        }
        public static void RenderFrames(string theme, string clipName, string directory, int first, int count, int fps = 24, int width = 1280, int height = 720, float yaw = 0)
        {
            Directory.CreateDirectory(directory); var scene = EditorSceneManager.NewPreviewScene(); var previousTarget = RenderTexture.active;
            RenderTexture target = null; Texture2D image = null;
            try
            {
                var camera = Populate(scene, theme); var actors = scene.GetRootGameObjects().Select(g => g.GetComponent<StorybookCharacter>()).Where(c => c != null).ToArray();
                var clipSets = actors.Select(a => StorybookAssets.Clips(StorybookAssets.ReadCatalog().characters.Single(c => c.key == a.characterKey)).ToDictionary(c => c.name)).ToArray();
                var ranges = StorybookAssets.ReadCatalog().clips;
                foreach (var actor in actors) foreach (var skin in actor.GetComponentsInChildren<SkinnedMeshRenderer>()) skin.forceMatrixRecalculationPerRender = true;
                target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGBHalf); target.antiAliasing = 4; camera.targetTexture = target; image = new Texture2D(width, height, TextureFormat.RGB24, false);
                for (int frame = first; frame < first + count; frame++)
                {
                    var range = clipName == "Timeline" ? ranges.Single(c => c.first <= frame + 1 && c.last >= frame + 1) : null;
                    string current = range == null ? clipName : range.name; float seconds = range == null ? (float)frame / fps : (float)(frame + 1 - range.first) / range.fps;
                    for (int i = 0; i < actors.Length; i++) { var pos = actors[i].transform.position; var clip = clipSets[i][current]; clip.SampleAnimation(actors[i].gameObject, Mathf.Min(seconds, clip.length)); actors[i].transform.position = pos; actors[i].transform.rotation = Quaternion.Euler(0,yaw,0); }
                    camera.Render(); RenderTexture.active = target; image.ReadPixels(new Rect(0, 0, width, height), 0, 0); image.Apply(); File.WriteAllBytes(Path.Combine(directory, frame.ToString("D4") + ".png"), image.EncodeToPNG());
                }
                camera.targetTexture = null;
            }
            finally { RenderTexture.active = previousTarget; if (image != null) UnityEngine.Object.DestroyImmediate(image); if (target != null) { target.Release(); UnityEngine.Object.DestroyImmediate(target); } EditorSceneManager.ClosePreviewScene(scene); }
        }
    }
}
