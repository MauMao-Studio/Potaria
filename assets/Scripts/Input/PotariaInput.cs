using System;
using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace Potaria.Input
{
    /// <summary>
    /// Unified Input Manager for Potaria supporting Keyboard & Mouse, Gamepad (Steam Deck / Xbox),
    /// Mobile Touch virtual controls, and automated headless simulation.
    /// Maps directly to the Potaria controls:
    /// - WASD / Arrows: Movement & Platform drop
    /// - Space: Jump
    /// - Left-Click: Attack / Mine
    /// - Right-Click: Interact / Reel
    /// - Q, F, V, R: Skill hotkeys
    /// - C: Character panel
    /// - E: Inventory
    /// - 1-9, 0: Hotbar slots 0-9
    /// - Z: Zoom level toggle
    /// </summary>
    public class PotariaInput : MonoBehaviour
    {
        private static PotariaInput _instance;
        public static PotariaInput Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindFirstObjectByType<PotariaInput>();
                }
                return _instance;
            }
            private set => _instance = value;
        }

        [Header("Virtual / Simulated Controls")]
        [SerializeField] private bool useSimulatedInput = false;

        // Current Input State
        public Vector2 MoveVector { get; private set; }
        public bool JumpPressed { get; private set; }
        public bool JumpHeld { get; private set; }
        public bool JumpReleased { get; private set; }

        public bool AttackPressed { get; private set; }
        public bool AttackHeld { get; private set; }

        public bool InteractPressed { get; private set; }
        public bool InteractHeld { get; private set; }

        public bool DropPlatformPressed { get; private set; }
        public bool DropPlatformHeld { get; private set; }

        public bool Skill1Pressed { get; private set; } // Q (Power Slash)
        public bool Skill2Pressed { get; private set; } // F (Whirlwind)
        public bool Skill3Pressed { get; private set; } // V (Dash)
        public bool Skill4Pressed { get; private set; } // R (Fireball)

        public bool CharacterPanelPressed { get; private set; } // C
        public bool InventoryPressed { get; private set; }      // E
        public bool ZoomTogglePressed { get; private set; }     // Z

        public int HotbarSlotPressed { get; private set; } = -1; // 0-9, or -1 if none

        public Vector2 MouseScreenPosition { get; private set; }
        public Vector2 MouseWorldPosition { get; private set; }
        public Vector2 AimDirection { get; private set; } = Vector2.right;

        // Simulated state storage for tests & virtual touch
        private Vector2 _simMove;
        private bool _simJumpPressed;
        private bool _simJumpHeld;
        private bool _simJumpReleased;
        private bool _simAttackPressed;
        private bool _simAttackHeld;
        private bool _simInteractPressed;
        private bool _simInteractHeld;
        private bool _simDropPressed;
        private bool _simDropHeld;
        private bool _simSkill1;
        private bool _simSkill2;
        private bool _simSkill3;
        private bool _simSkill4;
        private bool _simCharPanel;
        private bool _simInventory;
        private bool _simZoomToggle;
        private int _simHotbarSlot = -1;
        private Vector2 _simAimDir = Vector2.right;
        private Vector2 _simMouseWorld;

        private void Reset()
        {
            if (_instance == null)
            {
                _instance = this;
            }
        }

        private void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        private void OnDestroy()
        {
            if (_instance == this)
            {
                _instance = null;
            }
        }

        private void Update()
        {
            if (useSimulatedInput)
            {
                ApplySimulatedInput();
                return;
            }

            ReadHardwareInput();
        }

        private void ReadHardwareInput()
        {
            float horizontal = 0f;
            float vertical = 0f;

            // 1. Keyboard / Legacy Input fallback
            if (UnityEngine.Input.GetKey(KeyCode.A) || UnityEngine.Input.GetKey(KeyCode.LeftArrow))
                horizontal -= 1f;
            if (UnityEngine.Input.GetKey(KeyCode.D) || UnityEngine.Input.GetKey(KeyCode.RightArrow))
                horizontal += 1f;
            if (UnityEngine.Input.GetKey(KeyCode.W) || UnityEngine.Input.GetKey(KeyCode.UpArrow))
                vertical += 1f;
            if (UnityEngine.Input.GetKey(KeyCode.S) || UnityEngine.Input.GetKey(KeyCode.DownArrow))
                vertical -= 1f;

            MoveVector = new Vector2(horizontal, vertical);
            if (MoveVector.sqrMagnitude > 1f) MoveVector = MoveVector.normalized;

            JumpPressed = UnityEngine.Input.GetKeyDown(KeyCode.Space);
            JumpHeld = UnityEngine.Input.GetKey(KeyCode.Space);
            JumpReleased = UnityEngine.Input.GetKeyUp(KeyCode.Space);

            AttackPressed = UnityEngine.Input.GetMouseButtonDown(0);
            AttackHeld = UnityEngine.Input.GetMouseButton(0);

            InteractPressed = UnityEngine.Input.GetMouseButtonDown(1);
            InteractHeld = UnityEngine.Input.GetMouseButton(1);

            DropPlatformPressed = UnityEngine.Input.GetKeyDown(KeyCode.S) || UnityEngine.Input.GetKeyDown(KeyCode.DownArrow);
            DropPlatformHeld = UnityEngine.Input.GetKey(KeyCode.S) || UnityEngine.Input.GetKey(KeyCode.DownArrow);

            Skill1Pressed = UnityEngine.Input.GetKeyDown(KeyCode.Q);
            Skill2Pressed = UnityEngine.Input.GetKeyDown(KeyCode.F);
            Skill3Pressed = UnityEngine.Input.GetKeyDown(KeyCode.V);
            Skill4Pressed = UnityEngine.Input.GetKeyDown(KeyCode.R);

            CharacterPanelPressed = UnityEngine.Input.GetKeyDown(KeyCode.C);
            InventoryPressed = UnityEngine.Input.GetKeyDown(KeyCode.E);
            ZoomTogglePressed = UnityEngine.Input.GetKeyDown(KeyCode.Z);

            HotbarSlotPressed = -1;
            for (int i = 0; i < 9; i++)
            {
                if (UnityEngine.Input.GetKeyDown(KeyCode.Alpha1 + i))
                {
                    HotbarSlotPressed = i;
                    break;
                }
            }
            if (UnityEngine.Input.GetKeyDown(KeyCode.Alpha0))
            {
                HotbarSlotPressed = 9;
            }

            // Mouse & Aim
            MouseScreenPosition = UnityEngine.Input.mousePosition;
            var cam = UnityEngine.Camera.main;
            if (cam != null)
            {
                var screenPoint = new Vector3(MouseScreenPosition.x, MouseScreenPosition.y, -cam.transform.position.z);
                MouseWorldPosition = cam.ScreenToWorldPoint(screenPoint);
            }

#if ENABLE_INPUT_SYSTEM
            // Check Gamepad via New Input System if connected
            var gamepad = Gamepad.current;
            if (gamepad != null)
            {
                Vector2 stick = gamepad.leftStick.ReadValue();
                if (stick.sqrMagnitude > 0.05f)
                {
                    MoveVector = stick;
                }

                if (gamepad.buttonSouth.wasPressedThisFrame) JumpPressed = true;
                if (gamepad.buttonSouth.isPressed) JumpHeld = true;
                if (gamepad.buttonSouth.wasReleasedThisFrame) JumpReleased = true;

                if (gamepad.buttonWest.wasPressedThisFrame) AttackPressed = true;
                if (gamepad.buttonWest.isPressed) AttackHeld = true;

                if (gamepad.buttonEast.wasPressedThisFrame) InteractPressed = true;

                if (gamepad.dpad.down.isPressed || stick.y < -0.6f)
                {
                    DropPlatformPressed = true;
                    DropPlatformHeld = true;
                }

                if (gamepad.leftShoulder.wasPressedThisFrame) Skill1Pressed = true;
                if (gamepad.rightShoulder.wasPressedThisFrame) Skill2Pressed = true;
                if (gamepad.leftTrigger.wasPressedThisFrame) Skill3Pressed = true;
                if (gamepad.rightTrigger.wasPressedThisFrame) Skill4Pressed = true;

                if (gamepad.startButton.wasPressedThisFrame) InventoryPressed = true;
                if (gamepad.selectButton.wasPressedThisFrame) CharacterPanelPressed = true;
                if (gamepad.rightStickButton.wasPressedThisFrame) ZoomTogglePressed = true;

                Vector2 rightStick = gamepad.rightStick.ReadValue();
                if (rightStick.sqrMagnitude > 0.1f)
                {
                    AimDirection = rightStick.normalized;
                }
            }
#endif
        }

        private void ApplySimulatedInput()
        {
            MoveVector = _simMove;
            JumpPressed = _simJumpPressed;
            JumpHeld = _simJumpHeld;
            JumpReleased = _simJumpReleased;

            AttackPressed = _simAttackPressed;
            AttackHeld = _simAttackHeld;

            InteractPressed = _simInteractPressed;
            InteractHeld = _simInteractHeld;
            DropPlatformPressed = _simDropPressed;
            DropPlatformHeld = _simDropHeld;

            Skill1Pressed = _simSkill1;
            Skill2Pressed = _simSkill2;
            Skill3Pressed = _simSkill3;
            Skill4Pressed = _simSkill4;

            CharacterPanelPressed = _simCharPanel;
            InventoryPressed = _simInventory;
            ZoomTogglePressed = _simZoomToggle;
            HotbarSlotPressed = _simHotbarSlot;

            AimDirection = _simAimDir;
            MouseWorldPosition = _simMouseWorld;

            // Clear one-frame triggers
            _simJumpPressed = false;
            _simJumpReleased = false;
            _simAttackPressed = false;
            _simInteractPressed = false;
            _simDropPressed = false;
            _simSkill1 = false;
            _simSkill2 = false;
            _simSkill3 = false;
            _simSkill4 = false;
            _simCharPanel = false;
            _simInventory = false;
            _simZoomToggle = false;
            _simHotbarSlot = -1;
        }

        // --- Simulation & Mobile API for Tests & Virtual Joysticks ---
        public void EnableSimulation(bool enable)
        {
            useSimulatedInput = enable;
        }

        public void SimulateMove(Vector2 move)
        {
            _simMove = move;
            if (useSimulatedInput) MoveVector = move;
        }

        public void SimulateJump(bool pressed, bool held, bool released = false)
        {
            _simJumpPressed = pressed;
            _simJumpHeld = held;
            _simJumpReleased = released;
            if (useSimulatedInput)
            {
                JumpPressed = pressed;
                JumpHeld = held;
                JumpReleased = released;
            }
        }

        public void SimulateAttack(bool pressed, bool held = false)
        {
            _simAttackPressed = pressed;
            _simAttackHeld = held;
            if (useSimulatedInput)
            {
                AttackPressed = pressed;
                AttackHeld = held;
            }
        }

        public void SimulateDropPlatform(bool pressed, bool held = false)
        {
            _simDropPressed = pressed;
            _simDropHeld = held;
            if (useSimulatedInput)
            {
                DropPlatformPressed = pressed;
                DropPlatformHeld = held;
            }
        }

        public void SimulateSkill(int skillNumber)
        {
            switch (skillNumber)
            {
                case 1: _simSkill1 = true; if (useSimulatedInput) Skill1Pressed = true; break;
                case 2: _simSkill2 = true; if (useSimulatedInput) Skill2Pressed = true; break;
                case 3: _simSkill3 = true; if (useSimulatedInput) Skill3Pressed = true; break;
                case 4: _simSkill4 = true; if (useSimulatedInput) Skill4Pressed = true; break;
            }
        }

        public void SimulateZoomToggle()
        {
            _simZoomToggle = true;
            if (useSimulatedInput) ZoomTogglePressed = true;
        }

        public void SimulateInteract(bool pressed, bool held = false)
        {
            _simInteractPressed = pressed;
            _simInteractHeld = held;
            if (useSimulatedInput)
            {
                InteractPressed = pressed;
                InteractHeld = held;
            }
        }

        public void SimulateCharacterPanel()
        {
            _simCharPanel = true;
            if (useSimulatedInput) CharacterPanelPressed = true;
        }

        public void SimulateInventory()
        {
            _simInventory = true;
            if (useSimulatedInput) InventoryPressed = true;
        }

        public void SimulateHotbarSlot(int slotIndex)
        {
            _simHotbarSlot = Mathf.Clamp(slotIndex, 0, 9);
            if (useSimulatedInput) HotbarSlotPressed = _simHotbarSlot;
        }

        public void SimulateAim(Vector2 worldPos, Vector2 aimDirection)
        {
            _simMouseWorld = worldPos;
            _simAimDir = aimDirection.normalized;
            if (useSimulatedInput)
            {
                MouseWorldPosition = worldPos;
                AimDirection = _simAimDir;
            }
        }

        public void ResetSimulation()
        {
            _simMove = Vector2.zero;
            _simJumpPressed = false;
            _simJumpHeld = false;
            _simJumpReleased = false;
            _simAttackPressed = false;
            _simAttackHeld = false;
            _simInteractPressed = false;
            _simDropPressed = false;
            _simDropHeld = false;
            _simSkill1 = false;
            _simSkill2 = false;
            _simSkill3 = false;
            _simSkill4 = false;
            _simCharPanel = false;
            _simInventory = false;
            _simZoomToggle = false;
            _simHotbarSlot = -1;
            _simAimDir = Vector2.right;
            _simMouseWorld = Vector2.zero;
            MoveVector = Vector2.zero;
            JumpPressed = false;
            JumpHeld = false;
            JumpReleased = false;
            AttackPressed = false;
            AttackHeld = false;
            DropPlatformPressed = false;
            DropPlatformHeld = false;
        }
    }
}
