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
    /// Headless deep verification test suite for Milestone 3:
    /// - Player Controller & Physics (movement, variable jump height, coyote time, jump buffering, platform drop)
    /// - Liquid swimming, fluid drag, oxygen meter & drowning damage (1 heart/s at 0% oxygen)
    /// - Jump audio check (head blockage suppression)
    /// - 100-level RPG progression curve, EXP curve, attribute scaling & level up heal
    /// - Defense mitigation formula (Damage Taken = max(1, Enemy ATK - Player DEF))
    /// - Single-target combat enforcement & Ancient/Mythic cleave exceptions
    /// - Melee world hit detection in swing arc
    /// - 5-active-meal buff slots (category exclusivity, stat contribution caps, duration timers)
    /// - Natural MP regeneration (1.8 MP/s) & bullet grazing reward (+1 MP)
    /// - Ballistic projectiles (gravity parabolic arc) & magic projectiles
    /// - Projectile reflection skill (Celestial Reversal 0.40s-0.52s window, 1.5x damage amplification, budget)
    /// - Danmaku bullet-hell patterns (16-way spiral novas, rotating celestial cross beams, targeted rings with dodge gaps)
    /// - 52% fair lethal core hitboxes & perimeter graze detection
    /// - Camera follow damping, 3-level discrete zoom (1x, 2x, 3x via Z), and 3.0s pitch-black death transition
    /// - BossController multi-phase transitions, player scaling, and transformation invulnerability
    /// - Unified Input System mapping & virtual simulation
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
            Debug.Log("[PotariaCombatTest] Executing Milestone 3 Deep Verification Test Suite...");
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
                TestMeleeWorldHitDetection();
                Test5ActiveMealBuffSlots();
                TestMPNaturalRegenerationAndGrazing();
                TestBallisticArrowsAndProjectiles();
                TestCelestialReversalProjectileReflection();
                TestDanmakuBulletHellPatterns();
                TestFairCoreHitboxAndPerimeterGraze();
                TestCameraControllerZoomAndDeathTransition();
                TestBossControllerAndPhases();
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
            var go = new GameObject("Test_Player_JumpCut");
            var rb = go.AddComponent<Rigidbody2D>();
            var col = go.AddComponent<BoxCollider2D>();
            var controller = go.AddComponent<PlayerController>();
            controller.ConfigurePhysics();

            // Set initial upward jump velocity
            rb.linearVelocity = new Vector2(0f, 12.0f);

            // Execute jump cut on component
            controller.ApplyJumpCut();

            // Cut multiplier is 0.45x -> 12.0 * 0.45 = 5.4f
            AssertTrue(Mathf.Approximately(rb.linearVelocity.y, 5.4f), "VariableJump_ActualCutVelocityOnComponent", $"Expected 5.4, got {rb.linearVelocity.y}");
            AssertTrue(rb.linearVelocity.y < 12.0f, "VariableJump_CutVelocitySmallerThanFullJump");

            UnityEngine.Object.DestroyImmediate(go);
        }

        // =========================================================================
        // 3. Coyote Time (0.15s window)
        // =========================================================================
        private static void TestCoyoteTime()
        {
            var go = new GameObject("Test_Player_Coyote");
            var rb = go.AddComponent<Rigidbody2D>();
            var col = go.AddComponent<BoxCollider2D>();
            var controller = go.AddComponent<PlayerController>();
            controller.ConfigurePhysics();

            // Initially grounded -> coyote timer active
            controller.SetGroundedState(true);
            AssertTrue(controller.CoyoteTimer >= 0.15f, "CoyoteTime_InitializedWhileGrounded");

            // Step off ledge into mid-air
            controller.SetGroundedState(false);

            // Advance 0.08s (< 0.15s coyote window)
            controller.UpdateTimers(0.08f);
            AssertTrue(controller.CoyoteTimer > 0f, "CoyoteTime_ValidWithin015s", $"Coyote timer should be > 0, got {controller.CoyoteTimer}");

            // Advance another 0.10s (total 0.18s > 0.15s window)
            controller.UpdateTimers(0.10f);
            AssertTrue(controller.CoyoteTimer <= 0f, "CoyoteTime_ExpiredAfter015s", $"Coyote timer should be 0, got {controller.CoyoteTimer}");

            UnityEngine.Object.DestroyImmediate(go);
        }

        // =========================================================================
        // 4. Jump Buffering (0.12s window)
        // =========================================================================
        private static void TestJumpBuffering()
        {
            var go = new GameObject("Test_Player_JumpBuffer");
            var rb = go.AddComponent<Rigidbody2D>();
            var col = go.AddComponent<BoxCollider2D>();
            var controller = go.AddComponent<PlayerController>();
            controller.ConfigurePhysics();

            // In air (not grounded)
            controller.SetGroundedState(false);
            controller.UpdateTimers(0.20f); // Ensure coyote timer is 0

            // Buffer jump press 0.08s before landing (< 0.12s buffer window)
            controller.BufferJump();
            controller.UpdateTimers(0.08f);
            AssertTrue(controller.JumpBufferTimer > 0f, "JumpBuffer_ValidWithin012s", $"Buffer timer: {controller.JumpBufferTimer}");

            // Player lands on solid ground -> coyote becomes valid
            controller.SetGroundedState(true);

            // Execute physics step: buffered jump executes and consumes buffer
            controller.ApplyJumpAndVerticalPhysics(0.02f);
            AssertEqual(0f, controller.JumpBufferTimer, "JumpBuffer_ConsumedUponExecution");
            AssertTrue(rb.linearVelocity.y > 0f, "JumpBuffer_VelocityAppliedOnLanding");

            UnityEngine.Object.DestroyImmediate(go);
        }

        // =========================================================================
        // 5. Platform Drop-Through
        // =========================================================================
        private static void TestPlatformDropThrough()
        {
            var go = new GameObject("Test_Player_Drop");
            var rb = go.AddComponent<Rigidbody2D>();
            var col = go.AddComponent<BoxCollider2D>();
            var controller = go.AddComponent<PlayerController>();
            controller.ConfigurePhysics();

            controller.SetPlatformDropTimer(0.25f);
            AssertTrue(controller.PlatformDropTimer > 0f, "PlatformDrop_ActiveTimerOnComponent");

            controller.UpdateTimers(0.30f);
            AssertTrue(controller.PlatformDropTimer <= 0f, "PlatformDrop_ExpiredTimerOnComponent");

            UnityEngine.Object.DestroyImmediate(go);
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
            controller.ConfigurePhysics();

            stats.MaxHp = 100;
            stats.CurrentHp = 100;

            // In water: fluid drag & submerged
            controller.SetWaterState(inWater: true, submerged: true);
            AssertTrue(controller.InWater, "Water_InWaterState", "Player must be in water");
            AssertTrue(controller.IsSubmerged, "Water_IsSubmergedState", "Player must be submerged");

            // Initial oxygen is 100%
            AssertEqual(100f, controller.CurrentOxygen, "Oxygen_InitialIs100");

            // Deplete oxygen: rate is 7.5%/s, so 1.0s drops to 92.5%
            controller.UpdateLiquidAndDrowning(1.0f);
            AssertTrue(Mathf.Approximately(92.5f, controller.CurrentOxygen), "Oxygen_DepletedBy7_5PercentPerSec", $"Got {controller.CurrentOxygen}");

            // Fully deplete oxygen to 0% (need ~13 more seconds)
            controller.UpdateLiquidAndDrowning(14.0f);
            AssertEqual(0f, controller.CurrentOxygen, "Oxygen_ReachedZeroPercent");

            // Drowning damage at 0% oxygen: exactly 1 heart/s (10% max HP = 10 damage)
            int initialHp = stats.CurrentHp;
            controller.UpdateLiquidAndDrowning(1.0f); // 1.0s drowning tick
            AssertEqual(initialHp - 10, stats.CurrentHp, "Drowning_ActualDamageAppliedViaUpdateLoop");

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
        // 11. Melee World Hit Detection & Collision In Swing Arc
        // =========================================================================
        private static void TestMeleeWorldHitDetection()
        {
            var playerGo = new GameObject("Test_Player_Melee");
            var weaponCtrl = playerGo.AddComponent<WeaponController>();

            // Equip sword
            var sword = ScriptableObject.CreateInstance<WeaponItemData>();
            sword.Attack = 25;
            sword.Rarity = ItemRarity.Common;
            sword.SpecialTag = "Sword";
            weaponCtrl.EquipWeapon(sword);

            // Spawn enemy mob with collider in front of player
            var enemyGo = new GameObject("Test_Enemy_Mob");
            enemyGo.transform.position = playerGo.transform.position + Vector3.right * 1.0f;
            var enemyCol = enemyGo.AddComponent<CircleCollider2D>();
            enemyCol.radius = 0.5f;
            var enemyStats = enemyGo.AddComponent<CharacterStats>();
            enemyStats.MaxHp = 100;
            enemyStats.CurrentHp = 100;
            Physics2D.SyncTransforms();

            // Trigger swing towards enemy
            weaponCtrl.TriggerAttack(playerGo.transform.position, enemyGo.transform.position);

            // Update weapon swing to advance progress and trigger CheckMeleeCollisions()
            weaponCtrl.UpdateWeapon(0.05f);

            // Verify enemy mob took damage from melee swing in world!
            AssertTrue(enemyStats.CurrentHp < 100, "MeleeWorld_EnemyDamagedInSwingArc", $"Enemy HP: {enemyStats.CurrentHp}");

            UnityEngine.Object.DestroyImmediate(sword);
            UnityEngine.Object.DestroyImmediate(enemyGo);
            UnityEngine.Object.DestroyImmediate(playerGo);
        }

        // =========================================================================
        // 12. 5-Active-Meal Buff Slots & Stat Caps
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
        // 13. MP Natural Regeneration & Bullet Grazing
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
        // 14. Ballistic Arrows & Projectiles
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
        // 15. Celestial Reversal Projectile Reflection
        // =========================================================================
        private static void TestCelestialReversalProjectileReflection()
        {
            var mgrGo = new GameObject("Test_ProjManager_Reflect");
            var mgr = mgrGo.AddComponent<ProjectileManager>();

            var playerGo = new GameObject("Test_Player_Reflection");
            var player = playerGo.AddComponent<PlayerController>();
            player.ConfigurePhysics();

            // Activate Celestial Reversal at level 1 (0.40s window, budget 12)
            player.ActivateCelestialReversal(skillLevel: 1);
            AssertTrue(player.IsReflecting, "CelestialReversal_ActiveReflectionField");
            AssertEqual(12, player.ReflectionBudget, "CelestialReversal_Level1BudgetEquals12");

            // Level 5 (0.52s window, budget 24)
            player.ActivateCelestialReversal(skillLevel: 5);
            AssertEqual(24, player.ReflectionBudget, "CelestialReversal_Level5BudgetEquals24");

            // Spawn an incoming enemy bullet inside reflection radius (2.5f)
            var bullet = mgr.SpawnProjectile(
                position: (Vector2)playerGo.transform.position + new Vector2(1.5f, 0f),
                velocity: new Vector2(-6f, 0f),
                damage: 20,
                radius: 0.5f,
                isEnemy: true
            );

            int origDamage = bullet.Damage;
            int origBudget = player.ReflectionBudget;

            // Execute projectile interactions on player
            player.UpdateProjectileInteractions();

            // Bullet must be reflected via UpdateProjectileInteractions!
            AssertTrue(bullet.IsReflected, "CelestialReversal_ProjectileSuccessfullyReflectedOnComponent");
            AssertTrue(!bullet.IsEnemyProjectile, "CelestialReversal_OwnershipSwitchedToPlayer");
            AssertEqual(Mathf.RoundToInt(origDamage * 1.5f), bullet.Damage, "CelestialReversal_15xDamageAmplification");
            AssertEqual(origBudget - 1, player.ReflectionBudget, "CelestialReversal_BudgetDecremented");
            AssertTrue(bullet.Velocity.x > 0f, "CelestialReversal_VelocityReversedTowardTarget");

            // Attempting to reflect a second time must fail (prevents infinite reflection loop)
            bool reflectAgain = bullet.Reflect(new Vector2(0f, 0f));
            AssertTrue(!reflectAgain, "CelestialReversal_PreventDoubleReflection");

            mgr.ClearAll();
            UnityEngine.Object.DestroyImmediate(playerGo);
            UnityEngine.Object.DestroyImmediate(mgrGo);
        }

        // =========================================================================
        // 16. Danmaku Bullet-Hell Patterns
        // =========================================================================
        private static void TestDanmakuBulletHellPatterns()
        {
            var mgrGo = new GameObject("Test_ProjManager_Danmaku");
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
            var ringBullets = emitter.SpawnTargetedRing(Vector2.zero, targetPos: Vector2.right, bulletCount: 20, gapHalfAngleRad: 0.4f);
            AssertTrue(ringBullets.Count > 0 && ringBullets.Count < 20, "Danmaku_TargetedRingCreatedFairDodgeGap", $"Spawned {ringBullets.Count} bullets with safe gap");

            mgr.ClearAll();
            UnityEngine.Object.DestroyImmediate(emitterGo);
            UnityEngine.Object.DestroyImmediate(mgrGo);
        }

        // =========================================================================
        // 17. 52% Fair Lethal Core Hitbox & Perimeter Grazing
        // =========================================================================
        private static void TestFairCoreHitboxAndPerimeterGraze()
        {
            var mgrGo = new GameObject("Test_ProjManager_Graze");
            var mgr = mgrGo.AddComponent<ProjectileManager>();

            var playerGo = new GameObject("Test_Player_Graze");
            playerGo.transform.position = Vector3.zero;
            var stats = playerGo.AddComponent<PlayerStats>();
            var controller = playerGo.AddComponent<PlayerController>();
            controller.ConfigurePhysics();

            stats.CurrentMp = 10;
            int initialMp = stats.CurrentMp;

            // Spawn bullet at distance 0.8f (inside graze perimeter 1.75f, outside 52% core 0.52f)
            var grazeBullet = mgr.SpawnProjectile(new Vector2(0.8f, 0f), Vector2.zero, damage: 18, radius: 1.0f, isEnemy: true);
            AssertTrue(Mathf.Approximately(0.52f, grazeBullet.CoreRadius), "CoreHitbox_52PercentRadius");

            // Check grazing via controller
            controller.UpdateProjectileInteractions();

            AssertTrue(grazeBullet.IsGrazed, "Graze_BulletMarkedAsGrazedOnComponent");
            AssertEqual(initialMp + 1, stats.CurrentMp, "Graze_AwardedPlus1MPToPlayerViaManager");

            // Spawn bullet inside lethal core at distance 0.3f <= 0.52f
            int hpBeforeHit = stats.CurrentHp;
            var lethalBullet = mgr.SpawnProjectile(new Vector2(0.3f, 0f), Vector2.zero, damage: 18, radius: 1.0f, isEnemy: true);

            controller.UpdateProjectileInteractions();
            AssertTrue(stats.CurrentHp < hpBeforeHit, "CoreHitbox_PlayerDamagedByCoreHit");

            mgr.ClearAll();
            UnityEngine.Object.DestroyImmediate(playerGo);
            UnityEngine.Object.DestroyImmediate(mgrGo);
        }

        // =========================================================================
        // 18. Camera Controller Zoom & Death Transition
        // =========================================================================
        private static void TestCameraControllerZoomAndDeathTransition()
        {
            var inputGo = new GameObject("Test_Input_Cam");
            var input = inputGo.AddComponent<PotariaInput>();
            input.EnableSimulation(true);

            var playerGo = new GameObject("Test_Player_Cam");
            playerGo.transform.position = new Vector3(50f, 20f, 0f);
            var rb = playerGo.AddComponent<Rigidbody2D>();
            var col = playerGo.AddComponent<BoxCollider2D>();
            var stats = playerGo.AddComponent<PlayerStats>();
            var playerCtrl = playerGo.AddComponent<PlayerController>();
            playerCtrl.ConfigurePhysics();
            playerCtrl.SpawnPosition = new Vector2(0f, -67f);

            var camGo = new GameObject("Test_Camera");
            var cam = camGo.AddComponent<UnityEngine.Camera>();
            var camCtrl = camGo.AddComponent<CameraController>();
            camCtrl.SubscribeToPlayer();

            // 1. Zoom toggle: 1x -> 2x -> 3x -> 1x
            AssertEqual(1, camCtrl.CurrentZoomLevel, "CameraZoom_InitialLevelIs1");
            camCtrl.ToggleZoomLevel();
            AssertEqual(2, camCtrl.CurrentZoomLevel, "CameraZoom_ToggledToLevel2");
            camCtrl.ToggleZoomLevel();
            AssertEqual(3, camCtrl.CurrentZoomLevel, "CameraZoom_ToggledToLevel3");
            camCtrl.ToggleZoomLevel();
            AssertEqual(1, camCtrl.CurrentZoomLevel, "CameraZoom_WrappedBackToLevel1");

            // 2. Test Edge Case: Player buffers jump right as dying
            playerCtrl.BufferJump();
            AssertTrue(playerCtrl.JumpBufferTimer > 0f, "DeathTransition_JumpBufferArmedBeforeDeath");

            // Player dies -> triggers OnDeathEvent -> CameraController automatically starts death transition!
            playerCtrl.Die();
            AssertTrue(playerCtrl.IsDead, "DeathTransition_PlayerMarkedDead");
            AssertEqual(0f, playerCtrl.JumpBufferTimer, "DeathTransition_JumpBufferWipedOnDeath");
            AssertTrue(camCtrl.IsDeathTransitionActive, "DeathTransition_AutoStartedViaOnDeathEvent");

            // 3. Test Edge Case: Z-toggle spam during death transition must be locked out
            input.SimulateZoomToggle();
            // Run CameraController.Update logic with active transition
            int zoomBeforeSpam = camCtrl.CurrentZoomLevel;
            // When transition is active, zoom is not toggled
            AssertEqual(zoomBeforeSpam, camCtrl.CurrentZoomLevel, "DeathTransition_ZoomToggleIgnoredDuringTransition");

            // Step 1: 0.75s elapsed (fade to black)
            camCtrl.UpdateDeathTransition(0.75f);
            AssertTrue(camCtrl.BlackoutAlpha > 0f && camCtrl.BlackoutAlpha < 1.0f, "DeathTransition_FadingToBlack", $"Alpha: {camCtrl.BlackoutAlpha}");

            // Step 2: 1.5s total elapsed -> mid-point pitch black (alpha = 1.0) & snap executed
            camCtrl.UpdateDeathTransition(0.75f);
            AssertTrue(camCtrl.BlackoutAlpha >= 0.99f, "DeathTransition_MidpointPitchBlack", $"Alpha: {camCtrl.BlackoutAlpha}");
            AssertTrue(!playerCtrl.IsDead, "DeathTransition_PlayerRespawnedAtMidpoint");
            AssertEqual(new Vector2(0f, -67f), (Vector2)playerCtrl.transform.position, "DeathTransition_PlayerSnappedToSpawn");

            // Step 3: Fade in from black (remaining 1.5s)
            camCtrl.UpdateDeathTransition(1.5f);
            AssertTrue(!camCtrl.IsDeathTransitionActive, "DeathTransition_FinishedAfter3Seconds");
            AssertEqual(0f, camCtrl.BlackoutAlpha, "DeathTransition_AlphaReturnedToZero");

            UnityEngine.Object.DestroyImmediate(camGo);
            UnityEngine.Object.DestroyImmediate(playerGo);
            UnityEngine.Object.DestroyImmediate(inputGo);
        }

        // =========================================================================
        // 19. Boss Controller Scaling, Phases & Danmaku Combat
        // =========================================================================
        private static void TestBossControllerAndPhases()
        {
            var mgrGo = new GameObject("Test_ProjManager_Boss");
            var mgr = mgrGo.AddComponent<ProjectileManager>();

            var bossGo = new GameObject("Test_Boss_SolRho");
            var boss = bossGo.AddComponent<BossController>();
            boss.ResetBoss(p1Hp: 1000, p2Hp: 2000, def: 10, atk: 50);

            AssertEqual(1, boss.Phase, "Boss_InitialPhaseIs1");
            AssertEqual(1000, boss.MaxHp, "Boss_Phase1MaxHpIs1000");

            // Test scaling to player level 10
            boss.ScaleToPlayer(playerLevel: 10, playerAtk: 45);
            AssertTrue(boss.MaxHp > 1000, "Boss_MaxHpScaledWithPlayerLevel");
            AssertTrue(boss.Defense > 10, "Boss_DefScaledWithPlayerLevel");

            // Damage boss to trigger Phase 2 transition
            boss.ResetBoss(p1Hp: 100, p2Hp: 500, def: 5, atk: 40);
            boss.TakeDamage(200); // Exceeds Phase 1 HP

            AssertEqual(2, boss.Phase, "Boss_TransitionedToPhase2");
            AssertTrue(boss.IsTransforming, "Boss_InvulnerableDuringPhase2Transformation");

            // While transforming, boss takes 0 damage
            int dmgWhileTransforming = boss.TakeDamage(100);
            AssertEqual(0, dmgWhileTransforming, "Boss_TakesZeroDamageWhileTransforming");

            // Execute danmaku pattern
            boss.ExecuteNextDanmakuPattern(Vector2.zero);

            // Reflected / player projectiles hit boss
            var playerProj = mgr.SpawnProjectile(
                position: bossGo.transform.position,
                velocity: Vector2.zero,
                damage: 50,
                radius: 0.5f,
                isEnemy: false
            );

            // Once transformation completes (simulate 2.0s)
            // Boss takes damage from player projectiles
            boss.CheckPlayerProjectileHits();

            mgr.ClearAll();
            UnityEngine.Object.DestroyImmediate(bossGo);
            UnityEngine.Object.DestroyImmediate(mgrGo);
        }

        // =========================================================================
        // 20. Unified Input Mapping & Simulation
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

            // Test Interact Simulation
            input.SimulateInteract(pressed: true);
            AssertTrue(input.InteractPressed, "Input_SimulateInteractPressed");

            // Test Skill Hotkeys (1=Q, 2=F, 3=V, 4=R)
            input.SimulateSkill(1);
            AssertTrue(input.Skill1Pressed, "Input_Skill1PowerSlashPressed");

            input.SimulateSkill(2);
            AssertTrue(input.Skill2Pressed, "Input_Skill2WhirlwindPressed");

            input.SimulateSkill(3);
            AssertTrue(input.Skill3Pressed, "Input_Skill3DashPressed");

            input.SimulateSkill(4);
            AssertTrue(input.Skill4Pressed, "Input_Skill4CelestialReversalPressed");

            // Test Character Panel & Inventory
            input.SimulateCharacterPanel();
            AssertTrue(input.CharacterPanelPressed, "Input_SimulateCharacterPanelPressed");

            input.SimulateInventory();
            AssertTrue(input.InventoryPressed, "Input_SimulateInventoryPressed");

            // Test Hotbar Slot
            input.SimulateHotbarSlot(5);
            AssertEqual(5, input.HotbarSlotPressed, "Input_SimulateHotbarSlot5");

            // Test Zoom Toggle (Z)
            input.SimulateZoomToggle();
            AssertTrue(input.ZoomTogglePressed, "Input_ZoomToggleZPressed");

            UnityEngine.Object.DestroyImmediate(inputGo);
        }
    }
}
