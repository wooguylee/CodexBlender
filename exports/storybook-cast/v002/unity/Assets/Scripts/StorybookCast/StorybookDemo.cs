using UnityEngine;

namespace StorybookCast
{
    [DisallowMultipleComponent]
    public sealed class StorybookDemo : MonoBehaviour
    {
        public bool autoCycle = true;
        public string theme;
        public StorybookCharacter[] actors = new StorybookCharacter[0];

        private static readonly CastMotion[] Sequence =
        {
            CastMotion.Idle,
            CastMotion.Walk,
            CastMotion.Run,
            CastMotion.SitDown,
            CastMotion.SitIdle,
            CastMotion.StandUp,
            CastMotion.Wave,
            CastMotion.Celebrate
        };

        private static readonly float[] Durations =
        {
            3f, 3f, 3f, 1.5f, 2f, 1.5f, 2f, 2f
        };

        private int sequenceIndex;
        private float elapsed;
        private bool observedAutoCycle;

        private void Start()
        {
            observedAutoCycle = autoCycle;
            if (autoCycle)
            {
                BeginCycle();
            }
        }

        private void Update()
        {
            // Re-enabling the Inspector toggle starts an easily understood
            // Idle-to-Celebrate sequence without changing any global setting.
            if (autoCycle != observedAutoCycle)
            {
                observedAutoCycle = autoCycle;
                if (autoCycle)
                {
                    BeginCycle();
                }
            }

            if (!autoCycle)
            {
                return;
            }

            elapsed += Time.deltaTime;
            while (elapsed >= Durations[sequenceIndex])
            {
                elapsed -= Durations[sequenceIndex];
                sequenceIndex = (sequenceIndex + 1) % Sequence.Length;
                ApplyMotion(Sequence[sequenceIndex]);
            }
        }

        private void BeginCycle()
        {
            sequenceIndex = 0;
            elapsed = 0f;
            ApplyMotion(Sequence[sequenceIndex]);
        }

        /// <summary>
        /// Manually play a motion for every assigned actor. Enable autoCycle
        /// again to resume the automatic demonstration from Idle.
        /// </summary>
        public void PlayAll(CastMotion state)
        {
            autoCycle = false;
            observedAutoCycle = false;
            elapsed = 0f;
            ApplyMotion(state);
        }

        private void ApplyMotion(CastMotion state)
        {
            if (actors == null)
            {
                return;
            }
            for (int i = 0; i < actors.Length; i++)
            {
                StorybookCharacter actor = actors[i];
                if (actor != null)
                {
                    actor.Play(state);
                }
            }
        }
    }
}
