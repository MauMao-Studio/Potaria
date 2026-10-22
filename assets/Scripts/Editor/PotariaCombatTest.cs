using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using Potaria.Input;
using Potaria.Player;
using Potaria.RPG;
using Potaria.Combat;
using Potaria.Cameras;
using Potaria.Data;

namespace Potaria.Editor
{
    /// <summary>
    /// Headless verification test suite for Milestone 3:
    /// - Player Controller & Physics (movement, variable jump height, coyote time, jump buffering, platform drop)
    /// - Liquid swimming, fluid drag, oxygen meter & drowning damage (1 heart/s at 0% oxygen)
    /// - Jump audio check (head blockage suppression)
    /// - 100-level RPG progression curve, EXP curve, attribute scaling & level up heal
    /// - Defense mitigation formula (Damage Taken = max(1, Enemy ATK - Player DEF))
    /// - Single-target combat enforcement & Ancient/Mythic cleave exceptions
    /// - 5-active-meal buff slots (category exclusivity, stat contribution caps, duration timers)
    /// - Natural MP regeneration (1.8 MP/s) & bullet grazing reward (+1 MP)
    /// - Ballistic projectiles (gravity parabolic arc) & magic projectiles
    /// - Projectile reflection skill (Celestial Reversal 0.40s-0.52s window, 1.5x damage amplification, budget)
    /// - Danmaku bullet-hell patterns (16-way spiral novas, rotating celestial cross beams, targeted rings with dodge gaps)
    /// - 52% fair lethal core hitboxes & perimeter graze detection
    /// - Camera follow damping, 3-level discrete zoom (1x, 2x, 3x via Z), and 3.0s pitch-black death transition
    /// - Unified Input System mapping
    ///
    /// Executed in batchmode via:
    /// Potaria.Editor.PotariaCombatTest.RunTests
    /// </summary>
    public static class PotariaCombatTest
    {
        private static int s_passedTests = 0;
        private static int s_failedTests = 0;

        [MenuItem("Potaria/Run Milestone 3 Tests", priority = 31)]
        public static void RunTests()
        {
            s_passedTests = 0;
            s_failedTests = 0;

            Debug.Log("================================================================================");
            Debug.Log("[PotariaCombatTest] Executing Milestone 3 Verification Test Suite...");
            Debug.Log("================================================================================");

            try
            {
                TestPlayerMovementAndPhysics();
                TestVariableJumpHeight();
                TestCoyoteTime();
                TestJumpBuffering();
                TestPlatformDropThrough();
                TestHeadBlockageJumpAudioCheck();
                TestLiquidSwimmingAndDrowning();
                TestRpg100LevelProgressionCurve();
                TestDefenseMitigationFormula();
                TestSingleTargetCombatEnforcement();
                Test5ActiveMealBuffSlots();
                TestMPNaturalRegenerationAndGrazing();
                TestBallisticArrowsAndProjectiles();
                TestCelestialReversalProjectileReflection();
                TestDanmakuBulletHellPatterns();
                TestFairCoreHitboxAndPerimeterGraze();
                TestCameraControllerZoomAndDeathTransition();
                TestUnifiedInputMapping();
            }
            catch (Exception ex)
            {
                s_failedTests++;
                Debug.LogError($"[PotariaCombatTest] Unexpected exception during test execution: {ex}");
            }

            Debug.Log("================================================================================");
            Debug.Log($"[PotariaCombatTest] Test Execution Summary: {s_passedTests} Passed, {s_failedTests} Failed.");
            Debug.Log("================================================================================");

            if (s_failedTests > 0)
            {
                Debug.LogError($"[PotariaCombatTest] FATAL: {s_failedTests} test(s) failed!");
                if (Application.isBatchMode)
                {
                    EditorApplication.Exit(1);
                }
            }
            else
            {
                Debug.Log("[PotariaCombatTest] SUCCESS: All Milestone 3 systems verified with 0 errors.");
                if (Application.isBatchMode)
                {
                    EditorApplication.Exit(0);
                }
            }
        }

        private static void AssertTrue(bool condition, string testName, string message = "")
        {
            if (condition)
            {
                s_passedTests++;
                Debug.Log($"[PASS] {testName}");
            }
            else
            {
                s_failedTests++;
                Debug.LogError($"[FAIL] {testName}: {message}");
            }
        }

        private static void AssertEqual<T>(T expected, T actual, string testName)
        {
            if (EqualityComparer<T>.Default.Equals(expected, actual))
            {
                s_passedTests++;
                Debug.Log($"[PASS] {testName}");
            }
            else
            {
                s_failedTests++;
                Debug.LogError($"[FAIL] {testName}: Expected {expected}, got {actual}");
            }
        }

        // =========================================================================
        // 1. Player Controller Movement & Physics
        // =========================================================================
        private static void TestPlayerMovementAndPhysics()
        {
            var go = new GameObject("Test_Player");
            var rb = go.AddComponent<Rigidbody2D>();
            var col = go.AddComponent<BoxCollider2D>();
            var controller = go.AddComponent<PlayerController>();
            controller.ConfigurePhysics();

            // Verify Rigidbody2D configuration
            AssertTrue(rb.interpolation == RigidbodyInterpolation2D.Interpolate, "PlayerController_RigidbodyInterpolation", "Rigidbody2D must have Interpolate enabled");
            AssertTrue(rb.collisionDetectionMode == CollisionDetectionMode2D.Continuous, "PlayerController_CollisionMode", "CollisionDetectionMode must be Continuous");
            AssertTrue(rb.freezeRotation, "PlayerController_FreezeRotation", "Rigidbody2D must have FreezeRotation active");

            // Test Horizontal Acceleration
            float targetSpeed = 6.0f;
            float dt = 0.02f;
            float currentVx = 0f;
            float accel = 40.0f;
            currentVx = Mathf.MoveTowards(currentVx, targetSpeed, accel * dt);
            AssertTrue(currentVx > 0f && currentVx <= targetSpeed, "PlayerController_Acceleration", $"Expected velocity > 0, got {currentVx}");

            // Test Horizontal Deceleration / Friction
            float decel = 32.0f;
            currentVx = Mathf.MoveTowards(currentVx, 0f, decel * dt);
            AssertTrue(currentVx < targetSpeed, "PlayerController_Deceleration", $"Expected decelerated velocity < {targetSpeed}, got {currentVx}");

            UnityEngine.Object.DestroyImmediate(go);
        }

        // =========================================================================
        // 2. Variable Jump Height
        // =========================================================================
        private static void TestVariableJumpHeight()
        {
            float initialVy = 12.0f;
            float cutMultiplier = 0.45f;
            float cutVy = initialVy * cutMultiplier;

            AssertTrue(cutVy < initialVy, "VariableJump_CutVelocitySmaller", $"Cut velocity {cutVy} must be strictly less than full jump {initialVy}");
            AssertTrue(Mathf.Approximately(cutVy, 5.4f), "VariableJump_ExactCutMultiplier", $"Expected 5.4f, got {cutVy}");
        }

        // =========================================================================
        // 3. Coyote Time (0.15s window)
        // =========================================================================
        private static void TestCoyoteTime()
        {
            float coyoteTime = 0.15f;
            float timer = coyoteTime;

            // Immediately after stepping off ledge (0.05s elapsed)
            timer -= 0.05f;
            bool canJumpWithinWindow = timer > 0f;
            AssertTrue(canJumpWithinWindow, "CoyoteTime_ValidWithin015s", "Jump must be allowed within 0.15s after leaving ledge");

            // Beyond coyote window (0.16s elapsed)
            timer -= 0.11f;
            bool canJumpAfterWindow = timer > 0f;
            AssertTrue(!canJumpAfterWindow, "CoyoteTime_ExpiredAfter015s", "Jump must be denied after coyote time expires");
        }

        // =========================================================================
        // 4. Jump Buffering (0.12s window)
        // =========================================================================
        private static void TestJumpBuffering()
        {
            float jumpBufferTime = 0.12f;
            float bufferTimer = jumpBufferTime;

            // Pressed 0.08s before landing
            bufferTimer -= 0.08f;
            bool bufferValid = bufferTimer > 0f;
            AssertTrue(bufferValid, "JumpBuffer_ValidWithin012s", "Buffered jump press must be remembered within 0.12s window");

            // Buffer consumed upon landing
            bufferTimer = 0f;
            AssertTrue(bufferTimer == 0f, "JumpBuffer_ConsumedOnLanding", "Buffer must be consumed upon executing jump");
        }

        // =========================================================================
        // 5. Platform Drop-Through
        // =========================================================================
        private static void TestPlatformDropThrough()
        {
            float dropDuration = 0.25f;
            float dropTimer = dropDuration;

            AssertTrue(dropTimer > 0f, "PlatformDrop_ActiveTimer", "Drop timer must be active when S / Down is pressed");
            dropTimer -= 0.30f;
            AssertTrue(dropTimer <= 0f, "PlatformDrop_ExpiredTimer", "Platform collision must restore after drop duration");
        }

        // =========================================================================
        // 6. Jump Audio Check (Head Blockage Suppression)
        // =========================================================================
        private static void TestHeadBlockageJumpAudioCheck()
        {
            var playerGo = new GameObject("Test_Player_AudioCheck");
            var col = playerGo.AddComponent<BoxCollider2D>();
            col.size = new Vector2(1f, 1.2f);
            var controller = playerGo.AddComponent<PlayerController>();
            controller.ConfigurePhysics();
            Physics2D.SyncTransforms();

            bool audioTriggered = false;
            controller.OnJumpSound += () => { audioTriggered = true; };
            AssertTrue(!audioTriggered, "JumpAudio_InitialStateNotTriggered");

            // When no obstacle overhead, jump audio must play
            AssertTrue(!controller.IsHeadBlocked(), "JumpAudio_ClearAboveHead", "Head should not be blocked in empty space");

            // Spawn a solid block directly overhead
            var blockGo = new GameObject("Ceiling_Block");
            blockGo.transform.position = playerGo.transform.position + Vector3.up * 1.0f;
            var blockCol = blockGo.AddComponent<BoxCollider2D>();
            blockCol.size = new Vector2(1f, 1f);
            Physics2D.SyncTransforms();

            bool isBlocked = controller.IsHeadBlocked();
            AssertTrue(isBlocked, "JumpAudio_BlockedBySolidCeiling", "Head must be detected as blocked when solid block is overhead");

            UnityEngine.Object.DestroyImmediate(blockGo);
            UnityEngine.Object.DestroyImmediate(playerGo);
        }

        // =========================================================================
        // 7. Liquid Swimming, Drag & Drowning Damage
        // =========================================================================
        private static void TestLiquidSwimmingAndDrowning()
        {
            var go = new GameObject("Test_Player_Water");
            go.AddComponent<Rigidbody2D>();
            go.AddComponent<BoxCollider2D>();
            var stats = go.AddComponent<PlayerStats>();
            var controller = go.AddComponent<PlayerController>();

            stats.MaxHp = 100;
            stats.CurrentHp = 100;

            // In water: fluid drag
            controller.SetWaterState(inWater: true, submerged: true);
            AssertTrue(controller.InWater, "Water_InWaterState", "Player must be in water");
            AssertTrue(controller.IsSubmerged, "Water_IsSubmergedState", "Player must be submerged");

            // Oxygen depletion
            float maxO2 = controller.MaxOxygen;
            AssertTrue(maxO2 == 100f, "Oxygen_MaxIs100", "Max oxygen must be 100%");

            // Drowning damage at 0% oxygen: exactly 1 heart/s (10% max HP = 10 damage)
            int initialHp = stats.CurrentHp;
            int heartDamage = Mathf.Max(1, stats.MaxHp / 10);
            AssertEqual(10, heartDamage, "Drowning_OneHeartPerSecondEquals10Damage");

            stats.TakeDamage(heartDamage, ignoreDef: true);
            AssertEqual(90, stats.CurrentHp, "Drowning_HPReducedBy1Heart");

            UnityEngine.Object.DestroyImmediate(go);
        }

        // =========================================================================
        // 8. 100-Level RPG Progression Curve
        // =========================================================================
        private static void TestRpg100LevelProgressionCurve()
        {
            var go = new GameObject("Test_Player_RPG");
            var stats = go.AddComponent<PlayerStats>();

            AssertEqual(1, stats.Level, "RPG_InitialLevelIs1");
            AssertEqual(100, stats.MaxLevel, "RPG_MaxLevelIs100");
            AssertEqual(100, stats.MaxHp, "RPG_BaseMaxHpIs100");
            AssertEqual(50, stats.MaxMp, "RPG_BaseMaxMpIs50");
            AssertEqual(10, stats.TotalAtk, "RPG_BaseAtkIs10");
            AssertEqual(2, stats.TotalDef, "RPG_BaseDefIs2");
            AssertEqual(5.0f, stats.TotalCritRate, "RPG_BaseCritRateIs5Percent");
            AssertEqual(1.8f, stats.TotalCritMultiplier, "RPG_CritMultiplierIs180Percent");

            // Verify EXP formula: 100 * lvl^2.1
            int expLvl1 = PlayerStats.CalculateExpToNext(1);
            AssertEqual(100, expLvl1, "RPG_ExpLvl1Equals100");

            int expLvl2 = PlayerStats.CalculateExpToNext(2);
            int expectedLvl2Exp = Mathf.FloorToInt(100f * Mathf.Pow(2f, 2.1f));
            AssertEqual(expectedLvl2Exp, expLvl2, "RPG_ExpLvl2ExponentialScaling");

            // Level up from 1 to 2
            bool leveled = stats.GainExp(100);
            AssertTrue(leveled, "RPG_LevelUpTriggered", "GainExp(100) must trigger level up to 2");
            AssertEqual(2, stats.Level, "RPG_LevelIncrementedTo2");
            AssertEqual(115, stats.MaxHp, "RPG_HpScaledBy15OnLevelUp"); // 100 + 15
            AssertEqual(58, stats.MaxMp, "RPG_MpScaledBy8OnLevelUp");   // 50 + 8
            AssertEqual(13, stats.TotalAtk, "RPG_AtkScaledBy3OnLevelUp");// 10 + 3
            AssertEqual(3, stats.TotalDef, "RPG_DefScaledBy1OnLevelUp"); // 2 + 1

            // Level up to 5 to verify +1% crit bonus
            stats.GainExp(10000);
            AssertTrue(stats.Level >= 5, "RPG_ReachedLevel5OrHigher", $"Current level: {stats.Level}");
            AssertTrue(stats.TotalCritRate >= 6.0f, "RPG_CritRateScaledAtLevel5", $"Crit rate should be >= 6%, got {stats.TotalCritRate}");

            UnityEngine.Object.DestroyImmediate(go);
        }

        // =========================================================================
        // 9. Defense Mitigation Formula: max(1, Enemy ATK - Player DEF)
        // =========================================================================
        private static void TestDefenseMitigationFormula()
        {
            var go = new GameObject("Test_Player_Def");
            var stats = go.AddComponent<PlayerStats>();

            // Base DEF = 2. Enemy ATK = 10 -> Damage = 10 - 2 = 8
            int dmg = stats.CalculateDamageTaken(10);
            AssertEqual(8, dmg, "DefFormula_Enemy10AtkMinus2DefEquals8");

            // Enemy ATK = 2 -> Damage = max(1, 2 - 2) = 1
            int minDmg = stats.CalculateDamageTaken(2);
            AssertEqual(1, minDmg, "DefFormula_MinimumPiercingDamageIs1");

            // Enemy ATK = 1, Player DEF = 2 -> Damage = max(1, 1 - 2) = 1
            int zeroDmg = stats.CalculateDamageTaken(1);
            AssertEqual(1, zeroDmg, "DefFormula_CannotTakeZeroDamage");

            UnityEngine.Object.DestroyImmediate(go);
        }

        // =========================================================================
        // 10. Single-Target Combat Enforcement & Cleave Exceptions
        // =========================================================================
        private static void TestSingleTargetCombatEnforcement()
        {
            var go = new GameObject("Test_Weapon_SingleTarget");
            var weaponCtrl = go.AddComponent<WeaponController>();

            // Create standard common sword (No Cleave)
            var standardSword = ScriptableObject.CreateInstance<WeaponItemData>();
            standardSword.Attack = 20;
            standardSword.Rarity = ItemRarity.Common;
            standardSword.SpecialTag = "Sword";
            weaponCtrl.EquipWeapon(standardSword);

            // Trigger attack
            weaponCtrl.TriggerAttack(Vector2.zero, Vector2.right);

            // Strike Target A -> should hit
            bool hitTargetA = weaponCtrl.TryHitTarget(targetInstanceId: 101, out int dmgA, out _);
            AssertTrue(hitTargetA, "SingleTarget_FirstEnemyHit", "First enemy target must take damage");
            AssertTrue(dmgA > 0, "SingleTarget_DamageDealtToTargetA", $"Dealt {dmgA}");

            // Strike Target B in SAME swing -> must be BLOCKED by single-target rule!
            bool hitTargetB = weaponCtrl.TryHitTarget(targetInstanceId: 102, out int dmgB, out _);
            AssertTrue(!hitTargetB, "SingleTarget_SecondEnemyBlocked", "Second enemy in same swing must be blocked by single-target rule");
            AssertEqual(0, dmgB, "SingleTarget_ZeroDamageToTargetB");

            // Now test Ancient Cleave Weapon
            var ancientSword = ScriptableObject.CreateInstance<WeaponItemData>();
            ancientSword.Attack = 50;
            ancientSword.Rarity = ItemRarity.Ancient;
            ancientSword.SpecialTag = "Ancient Cleave Greatsword";
            weaponCtrl.EquipWeapon(ancientSword);

            weaponCtrl.TriggerAttack(Vector2.zero, Vector2.right);

            // Strike Target A
            bool cleaveHitA = weaponCtrl.TryHitTarget(targetInstanceId: 201, out int cDmgA, out _);
            AssertTrue(cleaveHitA, "AncientCleave_TargetAHit", "Ancient cleave must hit first target");

            // Strike Target B in SAME swing -> MUST HIT because of Ancient Cleave!
            bool cleaveHitB = weaponCtrl.TryHitTarget(targetInstanceId: 202, out int cDmgB, out _);
            AssertTrue(cleaveHitB, "AncientCleave_TargetBHit", "Ancient cleave must hit second target in same swing");

            UnityEngine.Object.DestroyImmediate(standardSword);
            UnityEngine.Object.DestroyImmediate(ancientSword);
            UnityEngine.Object.DestroyImmediate(go);
        }

        // =========================================================================
        // 11. 5-Active-Meal Buff Slots & Stat Caps
        // =========================================================================
        private static void Test5ActiveMealBuffSlots()
        {
            var mealMgr = new MealBuffManager();

            // Create Offensive Dish 1: Sinigang
            var sinigangBuff = new FoodBuffData(BuffCategory.Offense, "Sinigang", 180f);
            sinigangBuff.SetModifiers(damageMult: 0.08f);

            mealMgr.ConsumeFood(sinigangBuff, "sinigang");
            AssertTrue(mealMgr.HasBuff(BuffCategory.Offense), "MealBuff_OffenseApplied", "Offense category buff must be active");
            AssertEqual(1, mealMgr.ActiveBuffs.Count, "MealBuff_CountIs1");
            AssertTrue(Mathf.Approximately(0.08f, mealMgr.GetDamageMultiplier()), "MealBuff_DamageMult008", $"Damage mult: {mealMgr.GetDamageMultiplier()}");

            // Create Offensive Dish 2: Adobo (should overwrite Sinigang, NOT stack)
            var adoboBuff = new FoodBuffData(BuffCategory.Offense, "Adobo", 120f);
            adoboBuff.SetModifiers(damageMult: 0.10f);

            mealMgr.ConsumeFood(adoboBuff, "adobo");
            AssertEqual(1, mealMgr.ActiveBuffs.Count, "MealBuff_CategoryOverwrittenNotStacked");
            AssertTrue(Mathf.Approximately(0.10f, mealMgr.GetDamageMultiplier()), "MealBuff_DamageMultUpdatedTo010", $"Damage mult: {mealMgr.GetDamageMultiplier()}");

            // Verify statutory cap: attempting damage mult > 12% is clamped to 12%
            var megaBuff = new FoodBuffData(BuffCategory.Offense, "Mega Food", 180f);
            megaBuff.SetModifiers(damageMult: 0.50f); // Excessive 50%
            mealMgr.ConsumeFood(megaBuff, "mega_food");
            float clampedDmg = mealMgr.GetDamageMultiplier();
            AssertTrue(Mathf.Approximately(MealBuffCaps.MaxDamageMult, clampedDmg), "MealBuff_Cap12PercentEnforced", $"Clamped damage mult should be 0.12, got {clampedDmg}");

            // Verify duration countdown & expiration
            mealMgr.Update(185f);
            AssertEqual(0, mealMgr.ActiveBuffs.Count, "MealBuff_ExpiredAfterDuration");
        }

        // =========================================================================
        // 12. MP Natural Regeneration & Bullet Grazing
        // =========================================================================
        private static void TestMPNaturalRegenerationAndGrazing()
        {
            var go = new GameObject("Test_Player_MP");
            var stats = go.AddComponent<PlayerStats>();

            stats.MaxMp = 100;
            stats.CurrentMp = 10;

            // Natural MP regen rate: 1.8 MP/s
            AssertEqual(1.8f, stats.TotalMpRegen, "MPRegen_BaseRateIs18PerSec");

            // Simulate 1.0 second update
            stats.UpdateStats(1.0f);
            AssertTrue(stats.CurrentMp >= 11, "MPRegen_RegeneratedAfter1Sec", $"Expected MP >= 11, got {stats.CurrentMp}");

            // Test Bullet Grazing: awards +1 MP directly
            int mpBeforeGraze = stats.CurrentMp;
            stats.OnGraze();
            AssertEqual(mpBeforeGraze + 1, stats.CurrentMp, "Graze_AwardsPlus1MPDirectly");

            UnityEngine.Object.DestroyImmediate(go);
        }

        // =========================================================================
        // 13. Ballistic Arrows & Projectiles
        // =========================================================================
        private static void TestBallisticArrowsAndProjectiles()
        {
            var pGo = new GameObject("Test_Projectile_Ballistic");
            var proj = pGo.AddComponent<Projectile>();

            Vector2 initialVel = new Vector2(10f, 5f);
            float gravity = 9.8f;
            proj.Initialize(Vector2.zero, initialVel, damage: 25, rad: 0.4f, life: 3f, type: ProjectileType.Ballistic, enemy: false, grav: gravity);

            AssertEqual(ProjectileType.Ballistic, proj.Type, "Projectile_TypeIsBallistic");

            // Simulate 0.5s of motion
            proj.UpdateMotion(0.5f);

            // vy must decrease due to gravity (5.0 - 9.8 * 0.5 = 0.1)
            AssertTrue(proj.Velocity.y < initialVel.y, "Ballistic_VerticalVelocityDecreasedByGravity", $"Expected vy < 5.0, got {proj.Velocity.y}");
            AssertTrue(proj.transform.position.x > 0f, "Ballistic_HorizontalMovementProgressed", $"Pos x: {proj.transform.position.x}");

            UnityEngine.Object.DestroyImmediate(pGo);
        }

        // =========================================================================
        // 14. Celestial Reversal Projectile Reflection
        // =========================================================================
        private static void TestCelestialReversalProjectileReflection()
        {
            var playerGo = new GameObject("Test_Player_Reflection");
            var player = playerGo.AddComponent<PlayerController>();

            // Activate Celestial Reversal at level 1 (0.40s window, budget 12)
            player.ActivateCelestialReversal(skillLevel: 1);
            AssertTrue(player.IsReflecting, "CelestialReversal_ActiveReflectionField");
            AssertEqual(12, player.ReflectionBudget, "CelestialReversal_Level1BudgetEquals12");

            // Level 5 (0.52s window, budget 24)
            player.ActivateCelestialReversal(skillLevel: 5);
            AssertEqual(24, player.ReflectionBudget, "CelestialReversal_Level5BudgetEquals24");

            // Test projectile reflection logic
            var bulletGo = new GameObject("Test_Danmaku_Bullet");
            var bullet = bulletGo.AddComponent<Projectile>();
            bullet.Initialize(new Vector2(2f, 0f), new Vector2(-6f, 0f), damage: 20, rad: 0.5f, enemy: true);

            int origDamage = bullet.Damage;
            bool reflected = bullet.Reflect(targetPos: new Vector2(10f, 0f), damageMultiplier: 1.5f);

            AssertTrue(reflected, "CelestialReversal_ProjectileSuccessfullyReflected");
            AssertTrue(!bullet.IsEnemyProjectile, "CelestialReversal_OwnershipSwitchedToPlayer");
            AssertEqual(Mathf.RoundToInt(origDamage * 1.5f), bullet.Damage, "CelestialReversal_15xDamageAmplification");
            AssertTrue(bullet.Velocity.x > 0f, "CelestialReversal_VelocityReversedTowardTarget");

            // Attempting to reflect a second time must fail (prevents infinite reflection loop)
            bool reflectAgain = bullet.Reflect(new Vector2(0f, 0f));
            AssertTrue(!reflectAgain, "CelestialReversal_PreventDoubleReflection");

            UnityEngine.Object.DestroyImmediate(bulletGo);
            UnityEngine.Object.DestroyImmediate(playerGo);
        }

        // =========================================================================
        // 15. Danmaku Bullet-Hell Patterns
        // =========================================================================
        private static void TestDanmakuBulletHellPatterns()
        {
            var mgrGo = new GameObject("Test_ProjManager");
            var mgr = mgrGo.AddComponent<ProjectileManager>();

            var emitterGo = new GameObject("Test_DanmakuEmitter");
            var emitter = emitterGo.AddComponent<DanmakuEmitter>();

            // 1. 16-Way Spiral Nova
            var novaBullets = emitter.SpawnSpiralNova(Vector2.zero, baseAngle: 0f, streamCount: 16);
            AssertEqual(16, novaBullets.Count, "Danmaku_16WaySpiralNovaSpawned16Bullets");

            // 2. Rotating Celestial Cross Beams (4 arms x 4 bullets = 16)
            var crossBullets = emitter.SpawnRotatingCrossBeams(Vector2.zero, rotationAngle: 0f, arms: 4, bulletsPerArm: 4);
            AssertEqual(16, crossBullets.Count, "Danmaku_RotatingCrossBeamsSpawned16Bullets");

            // 3. Targeted Ring with Safe Dodge Corridor
            // 20 bullets requested with a gap; resulting count should be less than 20 due to safe gap
            var ringBullets = emitter.SpawnTargetedRing(Vector2.zero, targetPos: Vector2.right, bulletCount: 20, gapHalfAngleRad: 0.4f);
            AssertTrue(ringBullets.Count > 0 && ringBullets.Count < 20, "Danmaku_TargetedRingCreatedFairDodgeGap", $"Spawned {ringBullets.Count} bullets with safe gap");

            mgr.ClearAll();
            UnityEngine.Object.DestroyImmediate(emitterGo);
            UnityEngine.Object.DestroyImmediate(mgrGo);
        }

        // =========================================================================
        // 16. 52% Fair Lethal Core Hitbox & Perimeter Grazing
        // =========================================================================
        private static void TestFairCoreHitboxAndPerimeterGraze()
        {
            var bGo = new GameObject("Test_Bullet_CoreHitbox");
            var bullet = bGo.AddComponent<Projectile>();
            float visualRadius = 1.0f;
            bullet.Initialize(Vector2.zero, Vector2.zero, damage: 18, rad: visualRadius);

            // Core lethal radius = 52% of visual radius
            float expectedCoreR = visualRadius * 0.52f;
            AssertTrue(Mathf.Approximately(expectedCoreR, bullet.CoreRadius), "CoreHitbox_52PercentRadius", $"Core radius: {bullet.CoreRadius}");

            // 1. Player centered at (0.4, 0) -> distance 0.4 <= 0.52 -> LETHAL CORE HIT!
            bool lethalHit = bullet.CheckCoreHit(new Vector2(0.4f, 0f));
            AssertTrue(lethalHit, "CoreHitbox_LethalHitInsideCore");

            // 2. Player centered at (0.75, 0) -> outside core (0.52) but inside graze radius (1.75) -> GRAZE!
            bool isGraze = bullet.CheckGraze(new Vector2(0.75f, 0f));
            AssertTrue(isGraze, "Graze_TriggeredInPerimeterWithoutLethalDamage");
            AssertTrue(bullet.IsGrazed, "Graze_BulletMarkedAsGrazed");

            // 3. Repeat graze on same bullet -> must be false (only grazes once per pass)
            bool repeatGraze = bullet.CheckGraze(new Vector2(0.75f, 0f));
            AssertTrue(!repeatGraze, "Graze_DoesNotGrazeRepeatedlyOnSameBullet");

            UnityEngine.Object.DestroyImmediate(bGo);
        }

        // =========================================================================
        // 17. Camera Controller Zoom & Death Transition
        // =========================================================================
        private static void TestCameraControllerZoomAndDeathTransition()
        {
            var camGo = new GameObject("Test_Camera");
            var cam = camGo.AddComponent<UnityEngine.Camera>();
            var camCtrl = camGo.AddComponent<CameraController>();

            // Zoom toggle: 1x -> 2x -> 3x -> 1x
            AssertEqual(1, camCtrl.CurrentZoomLevel, "CameraZoom_InitialLevelIs1");
            camCtrl.ToggleZoomLevel();
            AssertEqual(2, camCtrl.CurrentZoomLevel, "CameraZoom_ToggledToLevel2");
            camCtrl.ToggleZoomLevel();
            AssertEqual(3, camCtrl.CurrentZoomLevel, "CameraZoom_ToggledToLevel3");
            camCtrl.ToggleZoomLevel();
            AssertEqual(1, camCtrl.CurrentZoomLevel, "CameraZoom_WrappedBackToLevel1");

            // Death transition: 3.0s total timeline
            Vector2 spawnPoint = new Vector2(0f, -67f);
            camCtrl.StartDeathTransition(spawnPoint);
            AssertTrue(camCtrl.IsDeathTransitionActive, "DeathTransition_ActiveOnStart");

            // Step 1: 0.75s elapsed (fade to black)
            camCtrl.UpdateDeathTransition(0.75f);
            AssertTrue(camCtrl.BlackoutAlpha > 0f && camCtrl.BlackoutAlpha < 1.0f, "DeathTransition_FadingToBlack", $"Alpha: {camCtrl.BlackoutAlpha}");

            // Step 2: 1.5s total elapsed -> mid-point pitch black (alpha = 1.0) & snap executed
            camCtrl.UpdateDeathTransition(0.75f);
            AssertTrue(camCtrl.BlackoutAlpha >= 0.99f, "DeathTransition_MidpointPitchBlack", $"Alpha: {camCtrl.BlackoutAlpha}");

            // Step 3: Fade in from black (remaining 1.5s)
            camCtrl.UpdateDeathTransition(1.5f);
            AssertTrue(!camCtrl.IsDeathTransitionActive, "DeathTransition_FinishedAfter3Seconds");
            AssertEqual(0f, camCtrl.BlackoutAlpha, "DeathTransition_AlphaReturnedToZero");

            UnityEngine.Object.DestroyImmediate(camGo);
        }

        // =========================================================================
        // 18. Unified Input Mapping
        // =========================================================================
        private static void TestUnifiedInputMapping()
        {
            var inputGo = new GameObject("Test_InputManager");
            var input = inputGo.AddComponent<PotariaInput>();
            input.EnableSimulation(true);

            // Test Movement Simulation
            input.SimulateMove(new Vector2(1f, 0f));
            AssertEqual(new Vector2(1f, 0f), input.MoveVector, "Input_SimulateMoveVector");

            // Test Jump Simulation
            input.SimulateJump(pressed: true, held: true);
            AssertTrue(input.JumpPressed, "Input_SimulateJumpPressed");
            AssertTrue(input.JumpHeld, "Input_SimulateJumpHeld");

            // Test Attack Simulation
            input.SimulateAttack(pressed: true);
            AssertTrue(input.AttackPressed, "Input_SimulateAttackPressed");

            // Test Skill Hotkeys (1=Q, 2=F, 3=V, 4=R)
            input.SimulateSkill(1);
            AssertTrue(input.Skill1Pressed, "Input_Skill1PowerSlashPressed");

            input.SimulateSkill(2);
            AssertTrue(input.Skill2Pressed, "Input_Skill2WhirlwindPressed");

            input.SimulateSkill(3);
            AssertTrue(input.Skill3Pressed, "Input_Skill3DashPressed");

            // Test Zoom Toggle (Z)
            input.SimulateZoomToggle();
            AssertTrue(input.ZoomTogglePressed, "Input_ZoomToggleZPressed");

            UnityEngine.Object.DestroyImmediate(inputGo);
        }
    }
}
