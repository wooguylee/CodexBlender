using System;
using UnityEngine;

namespace StorybookCast
{
    // Keep these names identical to catalog.py and the imported Animator states.
    public enum CastMotion
    {
        Idle,
        Walk,
        Run,
        SitDown,
        SitIdle,
        StandUp,
        Wave,
        Celebrate
    }

    [ExecuteAlways]
    [DisallowMultipleComponent]
    public sealed class StorybookCharacter : MonoBehaviour
    {
        public string characterKey;
        public string koreanName;
        public string role;
        public CastMotion motion = CastMotion.Idle;

        [Tooltip("Enable only to override the facial animation baked into the clips.")]
        public bool manualFace = false;

        [Range(0f, 1f)] public float blink;
        [Range(0f, 1f)] public float smile;
        [Range(0f, 1f)] public float surprise;

        private struct FaceIndices
        {
            public Mesh Mesh;
            public int Blink;
            public int Smile;
            public int Surprise;
        }

        private Animator cachedAnimator;
        private RuntimeAnimatorController cachedController;
        private SkinnedMeshRenderer[] faceRenderers;
        private FaceIndices[] faceIndices;
        private bool cacheDirty = true;
        private bool motionPending;
        private CastMotion observedMotion;

        private void OnEnable()
        {
            cacheDirty = true;
            observedMotion = motion;
            motionPending = Application.isPlaying;
            EnsureCache();
        }

        private void OnTransformChildrenChanged()
        {
            cacheDirty = true;
        }

        private void OnValidate()
        {
            blink = Mathf.Clamp01(blink);
            smile = Mathf.Clamp01(smile);
            surprise = Mathf.Clamp01(surprise);
            // ExecuteAlways applies the edited values in LateUpdate. Do not
            // access components here: Unity can invoke OnValidate while loading.
            if (faceRenderers == null || faceIndices == null)
            {
                cacheDirty = true;
            }
        }

        private void Update()
        {
            EnsureCache();
            if (!Application.isPlaying)
            {
                return;
            }

            RuntimeAnimatorController controller = cachedAnimator != null
                ? cachedAnimator.runtimeAnimatorController
                : null;
            if (controller != cachedController)
            {
                cachedController = controller;
                motionPending = true;
            }

            // Inspector changes are playback requests only during play mode.
            if (motion != observedMotion)
            {
                observedMotion = motion;
                motionPending = true;
            }

            TryPlayMotion();
        }

        /// <summary>Request an imported motion; safe without an Animator.</summary>
        public void Play(CastMotion state)
        {
            motion = state;
            observedMotion = state;
            motionPending = true;
            EnsureCache();
            TryPlayMotion();
        }

        private void TryPlayMotion()
        {
            if (!Application.isPlaying || !motionPending || !isActiveAndEnabled ||
                cachedAnimator == null || !cachedAnimator.isActiveAndEnabled ||
                cachedAnimator.runtimeAnimatorController == null || !cachedAnimator.isInitialized)
            {
                return;
            }

            // Names and hashes are resolved only for a motion request, never in
            // the facial LateUpdate path. A missing state does not spam warnings.
            string stateName = motion.ToString();
            motionPending = false;
            if (cachedAnimator.HasState(0, Animator.StringToHash(stateName)))
            {
                cachedAnimator.CrossFadeInFixedTime(stateName, .12f);
            }
        }

        /// <summary>Call after adding renderers/components at runtime.</summary>
        public void RefreshCache()
        {
            cacheDirty = true;
            EnsureCache();
        }

        private void EnsureCache()
        {
            if (!cacheDirty && faceRenderers != null && faceIndices != null)
            {
                return;
            }

            Animator previousAnimator = cachedAnimator;
            cachedAnimator = GetComponent<Animator>();
            if (cachedAnimator == null)
            {
                cachedAnimator = GetComponentInChildren<Animator>(true);
            }

            if (cachedAnimator != previousAnimator)
            {
                cachedController = cachedAnimator != null
                    ? cachedAnimator.runtimeAnimatorController
                    : null;
                motionPending = Application.isPlaying;
            }

            faceRenderers = GetComponentsInChildren<SkinnedMeshRenderer>(true);
            faceIndices = new FaceIndices[faceRenderers.Length];
            for (int i = 0; i < faceRenderers.Length; i++)
            {
                RefreshFaceIndices(i);
            }
            cacheDirty = false;
        }

        private void RefreshFaceIndices(int rendererIndex)
        {
            SkinnedMeshRenderer renderer = faceRenderers[rendererIndex];
            Mesh mesh = renderer != null ? renderer.sharedMesh : null;
            FaceIndices indices = new FaceIndices
            {
                Mesh = mesh,
                Blink = -1,
                Smile = -1,
                Surprise = -1
            };

            if (mesh != null)
            {
                for (int i = 0; i < mesh.blendShapeCount; i++)
                {
                    string shapeName = mesh.GetBlendShapeName(i);
                    // FBX may prepend a mesh/shape-group prefix to each name.
                    if (shapeName.EndsWith("Blink", StringComparison.Ordinal))
                    {
                        indices.Blink = i;
                    }
                    else if (shapeName.EndsWith("Smile", StringComparison.Ordinal))
                    {
                        indices.Smile = i;
                    }
                    else if (shapeName.EndsWith("Surprise", StringComparison.Ordinal))
                    {
                        indices.Surprise = i;
                    }
                }
            }
            faceIndices[rendererIndex] = indices;
        }

        private void LateUpdate()
        {
            // Default behavior never overwrites imported, baked facial curves.
            if (!manualFace)
            {
                return;
            }

            EnsureCache();
            float blinkWeight = 100f * Mathf.Clamp01(blink);
            float surpriseValue = Mathf.Clamp01(surprise);
            float smileWeight = 100f * Mathf.Clamp01(smile) * (1f - surpriseValue);
            float surpriseWeight = 100f * surpriseValue;

            for (int i = 0; i < faceRenderers.Length; i++)
            {
                SkinnedMeshRenderer renderer = faceRenderers[i];
                if (renderer == null)
                {
                    cacheDirty = true;
                    continue;
                }

                // Swapping a sharedMesh only refreshes this entry. The usual
                // per-frame path allocates no arrays, strings, lists or closures.
                if (faceIndices[i].Mesh != renderer.sharedMesh)
                {
                    RefreshFaceIndices(i);
                }

                FaceIndices indices = faceIndices[i];
                if (indices.Mesh == null)
                {
                    continue;
                }
                if (indices.Blink >= 0)
                {
                    renderer.SetBlendShapeWeight(indices.Blink, blinkWeight);
                }
                if (indices.Smile >= 0)
                {
                    renderer.SetBlendShapeWeight(indices.Smile, smileWeight);
                }
                if (indices.Surprise >= 0)
                {
                    renderer.SetBlendShapeWeight(indices.Surprise, surpriseWeight);
                }
            }
        }
    }
}
