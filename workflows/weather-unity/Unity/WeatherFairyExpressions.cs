using UnityEngine;

namespace WeatherFairies
{
    /// <summary>Optional live face controls. Leave manualExpressions off to play imported facial animation.</summary>
    [ExecuteAlways]
    public sealed class WeatherFairyExpressions : MonoBehaviour
    {
        public bool manualExpressions;
        [Range(0, 1)] public float awake;
        [Range(0, 1)] public float blink;
        [Range(0, 1)] public float smile;
        [Range(0, 1)] public float surprise;
        [Range(-1, 1)] public float tipSway;

        void LateUpdate() { if (manualExpressions) Apply(); }
        void OnValidate() { if (manualExpressions) Apply(); }

        public void Apply()
        {
            foreach (var renderer in GetComponentsInChildren<SkinnedMeshRenderer>(true))
            {
                var mesh = renderer.sharedMesh;
                if (mesh == null) continue;
                bool addedEye = renderer.name.Contains("AwakeEye");
                for (int i = 0; i < mesh.blendShapeCount; ++i)
                {
                    string shape = mesh.GetBlendShapeName(i);
                    int dot = shape.LastIndexOf('.');
                    if (dot >= 0) shape = shape.Substring(dot + 1);
                    float value;
                    switch (shape)
                    {
                        case "Wake": value = awake; break;
                        case "Blink": value = blink * (addedEye ? awake : 1f); break;
                        case "Smile": value = smile * (1f - surprise); break;
                        case "SurpriseHide": case "BrowRaise": value = surprise; break;
                        case "Hide": value = 1f - (addedEye ? awake : surprise); break;
                        case "TipSway": value = tipSway; break;
                        default: continue;
                    }
                    renderer.SetBlendShapeWeight(i, 100f * value);
                }
            }
        }
    }
}
