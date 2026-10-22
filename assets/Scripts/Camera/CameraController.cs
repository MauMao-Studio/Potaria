using System;
using UnityEngine;
using Potaria.Input;
using Potaria.Player;

namespace Potaria.Cameras
{
    /// <summary>
    /// Camera Controller for Potaria:
    /// - Smooth camera follow with damping/lerp
    /// - 3 discrete zoom levels (1x, 2x, 3x) toggled via 'Z' key
    /// - Cinematic pitch-black death transition: 3.0s total (fade to black 1.5s, snap camera/player to spawn at pitch black, fade in 1.5s)
    /// </summary>
    [RequireComponent(typeof(UnityEngine.Camera))]
    public class CameraController : MonoBehaviour
    {
        [Header("Target & Follow")]
        [SerializeField] private Transform target;
        [SerializeField] private Vector3 followOffset = new Vector3(0f, 0f, -10f);
        [SerializeField] private float followDamping = 6.0f;

        [Header("3-Level Discrete Zoom (Z key)")]
        [SerializeField] private int currentZoomLevel = 1; // 1, 2, 3
        [SerializeField] private float zoom1OrthoSize = 10.0f; // 1x
        [SerializeField] private float zoom2OrthoSize = 7.5f;  // 2x
        [SerializeField] private float zoom3OrthoSize = 5.0f;  // 3x
        [SerializeField] private float zoomLerpSpeed = 10.0f;

        [Header("Cinematic Pitch-Black Death Transition")]
        [SerializeField] private float deathTransitionDuration = 3.0f;
        private float _deathTimer = 0f;
        private bool _isDeathTransitionActive = false;
        private bool _deathSnapExecuted = false;
        private Vector2 _respawnPosition = Vector2.zero;
        private float _blackoutAlpha = 0f;

        [Header("Dependencies")]
        [SerializeField] private PotariaInput input;
        [SerializeField] private PlayerController player;

        private UnityEngine.Camera _cam;
        private UnityEngine.Camera Cam => _cam != null ? _cam : (_cam = GetComponent<UnityEngine.Camera>());
        private Texture2D _blackoutTexture;

        public int CurrentZoomLevel => currentZoomLevel;
        public float TargetOrthoSize => GetTargetOrthoSize();
        public float CurrentOrthoSize => (Cam != null) ? Cam.orthographicSize : 10f;
        public float BlackoutAlpha => _blackoutAlpha;
        public bool IsDeathTransitionActive => _isDeathTransitionActive;

        public event Action<int> OnZoomChanged;
        public event Action OnDeathSnap;

        private void Reset()
        {
            _cam = GetComponent<UnityEngine.Camera>();
        }

        private void Awake()
        {
            _cam = GetComponent<UnityEngine.Camera>();
            if (input == null) input = PotariaInput.Instance;
            if (player == null) player = FindAnyObjectByType<PlayerController>();

            CreateBlackoutTexture();
        }

        private void Start()
        {
            if (target == null && player != null)
            {
                target = player.transform;
            }

            if (_cam != null)
            {
                _cam.orthographicSize = GetTargetOrthoSize();
            }
        }

        private void CreateBlackoutTexture()
        {
            if (_blackoutTexture == null)
            {
                _blackoutTexture = new Texture2D(1, 1);
                _blackoutTexture.SetPixel(0, 0, Color.black);
                _blackoutTexture.Apply();
            }
        }

        private void Update()
        {
            if (input == null) input = PotariaInput.Instance;

            // 1. Zoom toggle via 'Z' key
            if (input != null && input.ZoomTogglePressed)
            {
                ToggleZoomLevel();
            }

            // 2. Smooth zoom interpolation
            if (_cam != null)
            {
                float targetOrtho = GetTargetOrthoSize();
                _cam.orthographicSize = Mathf.Lerp(_cam.orthographicSize, targetOrtho, zoomLerpSpeed * Time.deltaTime);
            }

            // 3. Cinematic death transition timeline
            if (_isDeathTransitionActive)
            {
                UpdateDeathTransition(Time.deltaTime);
            }
        }

        private void LateUpdate()
        {
            if (target == null) return;

            // If death snap just executed, snap position instantly
            if (_deathSnapExecuted && _deathTimer > (deathTransitionDuration * 0.45f))
            {
                transform.position = new Vector3(target.position.x + followOffset.x, target.position.y + followOffset.y, followOffset.z);
                return;
            }

            // Smooth camera follow
            Vector3 desiredPosition = new Vector3(target.position.x + followOffset.x, target.position.y + followOffset.y, followOffset.z);
            transform.position = Vector3.Lerp(transform.position, desiredPosition, followDamping * Time.deltaTime);
        }

        /// <summary>
        /// Advances zoom level: 1x -> 2x -> 3x -> 1x.
        /// </summary>
        public void ToggleZoomLevel()
        {
            currentZoomLevel++;
            if (currentZoomLevel > 3) currentZoomLevel = 1;
            OnZoomChanged?.Invoke(currentZoomLevel);
        }

        public void SetZoomLevel(int level)
        {
            currentZoomLevel = Mathf.Clamp(level, 1, 3);
            OnZoomChanged?.Invoke(currentZoomLevel);
        }

        private float GetTargetOrthoSize()
        {
            return currentZoomLevel switch
            {
                1 => zoom1OrthoSize,
                2 => zoom2OrthoSize,
                3 => zoom3OrthoSize,
                _ => zoom1OrthoSize
            };
        }

        /// <summary>
        /// Initiates the 3.0s cinematic pitch-black death transition.
        /// - 3.0s -> 1.5s: Fade to black
        /// - 1.5s: Screen pitch black, snap player & camera to spawn point
        /// - 1.5s -> 0.0s: Fade in from black
        /// </summary>
        public void StartDeathTransition(Vector2 spawnPoint)
        {
            _respawnPosition = spawnPoint;
            _deathTimer = deathTransitionDuration;
            _isDeathTransitionActive = true;
            _deathSnapExecuted = false;
            _blackoutAlpha = 0f;
        }

        public void UpdateDeathTransition(float dt)
        {
            _deathTimer -= dt;
            float halfDuration = deathTransitionDuration * 0.5f;

            if (_deathTimer > halfDuration)
            {
                // First half (3.0s -> 1.5s): Fade to black (alpha: 0 -> 1)
                float progress = (deathTransitionDuration - _deathTimer) / halfDuration;
                _blackoutAlpha = Mathf.Clamp01(progress);
            }
            else
            {
                // At midpoint (1.5s): Screen is 100% black -> Execute instantaneous teleport & snap!
                if (!_deathSnapExecuted)
                {
                    _deathSnapExecuted = true;
                    _blackoutAlpha = 1.0f;

                    if (player != null)
                    {
                        player.Respawn(_respawnPosition);
                    }

                    // Snap camera instantly
                    transform.position = new Vector3(_respawnPosition.x + followOffset.x, _respawnPosition.y + followOffset.y, followOffset.z);
                    OnDeathSnap?.Invoke();
                }

                // Second half (1.5s -> 0.0s): Fade in from black (alpha: 1 -> 0)
                float fadeProgress = _deathTimer / halfDuration;
                _blackoutAlpha = Mathf.Clamp01(fadeProgress);
            }

            if (_deathTimer <= 0f)
            {
                _isDeathTransitionActive = false;
                _blackoutAlpha = 0f;
                _deathSnapExecuted = false;
            }
        }

        private void OnGUI()
        {
            // Draw fullscreen pitch-black blackout overlay if alpha > 0
            if (_blackoutAlpha > 0.001f && _blackoutTexture != null)
            {
                Color prevColor = GUI.color;
                GUI.color = new Color(0f, 0f, 0f, _blackoutAlpha);
                GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), _blackoutTexture);
                GUI.color = prevColor;
            }
        }
    }
}
