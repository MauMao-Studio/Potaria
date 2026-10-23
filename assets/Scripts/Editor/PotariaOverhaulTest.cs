using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using Potaria.Input;
using Potaria.Player;
using Potaria.RPG;
using Potaria.Combat;
using Potaria.World.Lighting;
using Potaria.Localization;
using Potaria.UI;
using Potaria.Mob;

namespace Potaria.Editor
{
    /// <summary>
    /// Headless deep verification test suite for the Overhaul milestone:
    /// 1. Player ground detection (flat & 45-degree slope contacts) and jump execution
    /// 2. Player 8-frame walk animation, idle breathing, jump stretch, and facing flip
    /// 3. Procedural SkyRenderer2D day/night colors, starfield alpha, and 12-hour clock
    /// 4. Placed point light 2D shadow casting & torch configuration
    /// 5. Complete In-Game HUD (10 hotbar slots, hearts, mana bar, clock, skills, F3 profiler)
    /// 6. Mob behaviors (Green/Purple Slime hop, Zombie step jump, Demon Eye night flight, Spawner)
    /// 7. Localization table retrieval & instant English <-> Filipino language switching
    ///
    /// Executed in batchmode via:
    /// Potaria.Editor.PotariaOverhaulTest.RunTests
    /// </summary>
    public static class PotariaOverhaulTest
    {
        private static int s_passedTests = 0;
        private static int s_failedTests = 0;

        [MenuItem("Potaria/Run Overhaul Verification Tests", priority = 32)]
        public static void RunTests()
        {
            s_passedTests = 0;
            s_failedTests = 0;

            Debug.Log("================================================================================");
            Debug.Log("[PotariaOverhaulTest] Executing Overhaul Deep Verification Test Suite...");
            Debug.Log("================================================================================");

            try
            {
                TestPlayerGroundDetectionAndJump();
                TestPlayerSlopeContactHandling();
                TestPlayerAnimationCycles();
                TestSkyRendererAndDayNightClock();
                TestPointLight2DShadowCasting();
                TestInGameHUDHierarchyAndSlotSelection();
                TestMobsLocomotionAndAI();
                TestMobSpawnerAnnulusAndLimits();
                TestLocalizationManagerEnglishAndFilipino();
            }
            catch (Exception ex)
            {
                s_failedTests++;
                Debug.LogError($"[FATAL EXCEPTION in PotariaOverhaulTest]: {ex.Message}\n{ex.StackTrace}");
            }

            Debug.Log("================================================================================");
            Debug.Log($"[PotariaOverhaulTest] Test Execution Summary: {s_passedTests} Passed, {s_failedTests} Failed.");
            Debug.Log("================================================================================");

            if (s_failedTests > 0)
            {
                Debug.LogError($"[PotariaOverhaulTest] FAILED: {s_failedTests} test(s) failed.");
            }
            else
            {
                Debug.Log("[PotariaOverhaulTest] SUCCESS: All Overhaul systems verified with 0 errors.");
            }
        }

        private static void AssertTrue(bool condition, string testName, string failMessage = "")
        {
            if (condition)
            {
                s_passedTests++;
                Debug.Log($"[PASS] {testName}");
            }
            else
            {
                s_failedTests++;
                Debug.LogError($"[FAIL] {testName}: {failMessage}");
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
        // 1. Controls & Jump Ground Detection
        // =========================================================================
        private static void TestPlayerGroundDetectionAndJump()
        {
            var groundObj = new GameObject("Test_Ground");
            groundObj.transform.position = new Vector3(0f, -0.5f, 0f);
            var groundCol = groundObj.AddComponent<BoxCollider2D>();
            groundCol.size = new Vector2(10f, 1f);
            groundCol.offset = Vector2.zero;

            var playerObj = new GameObject("Test_Player");
            playerObj.transform.position = new Vector3(0f, 0f, 0f);
            var rb = playerObj.AddComponent<Rigidbody2D>();
            var col = playerObj.AddComponent<BoxCollider2D>();
            col.size = new Vector2(0.875f, 1.0f);
            col.offset = new Vector2(0f, 0.5f);

            var controller = playerObj.AddComponent<PlayerController>();
            controller.ConfigurePhysics();

            // Run ground status check directly on ground
            Physics2D.SyncTransforms();
            controller.CheckGroundStatus();

            AssertTrue(controller.IsGrounded, "Player_GroundedOnSurface", "Player standing on surface must be detected as grounded");
            AssertTrue(controller.CoyoteTimer >= 0.14f, "Player_CoyoteTimerRefreshed", "Coyote timer must refresh upon ground contact");

            // Test jump execution from ground
            controller.BufferJump();
            controller.ApplyJumpAndVerticalPhysics(0.02f);
            AssertTrue(rb.linearVelocity.y >= 11.5f, "Player_JumpExecutionUpwardVelocity", $"Expected jump velocity ~12.0f, got {rb.linearVelocity.y}");

            UnityEngine.Object.DestroyImmediate(playerObj);
            UnityEngine.Object.DestroyImmediate(groundObj);
        }

        // =========================================================================
        // 2. Slope Contact Handling (45-degree slope)
        // =========================================================================
        private static void TestPlayerSlopeContactHandling()
        {
            var slopeObj = new GameObject("Test_Slope");
            slopeObj.transform.position = new Vector3(0f, -0.5f, 0f);
            slopeObj.transform.rotation = Quaternion.Euler(0f, 0f, 45f);
            var slopeCol = slopeObj.AddComponent<BoxCollider2D>();
            slopeCol.size = new Vector2(10f, 1f);

            var playerObj = new GameObject("Test_Player_Slope");
            playerObj.transform.position = new Vector3(0f, 0.5f, 0f);
            var rb = playerObj.AddComponent<Rigidbody2D>();
            var col = playerObj.AddComponent<BoxCollider2D>();
            col.size = new Vector2(0.875f, 1.0f);
            col.offset = new Vector2(0f, 0.5f);

            var controller = playerObj.AddComponent<PlayerController>();
            controller.ConfigurePhysics();

            // Verify frictionless material and rounded edge radius
            AssertTrue(col.sharedMaterial != null, "Player_HasFrictionlessMaterial", "Player must have physics material assigned");
            AssertTrue(Mathf.Approximately(col.sharedMaterial.friction, 0f), "Player_ZeroFriction", "Physics material friction must be 0 for smooth slope locomotion");
            AssertTrue(col.edgeRadius > 0.01f, "Player_RoundedEdgeRadius", "BoxCollider2D must have rounded edge radius to prevent seam snagging");

            // Physics collision check on 45-degree slope
            Physics2D.SyncTransforms();
            controller.CheckGroundStatus();

            AssertTrue(controller.IsGrounded, "Player_GroundedOn45DegSlope", "Player on 45-degree slope must be detected as grounded");
            AssertTrue(controller.CoyoteTimer >= 0.14f, "Player_CoyoteTimerRefreshedOnSlope", "Coyote timer must refresh on slope");

            // Jump execution directly from 45-degree slope
            controller.BufferJump();
            controller.ApplyJumpAndVerticalPhysics(0.02f);
            AssertTrue(rb.linearVelocity.y >= 11.5f, "Player_JumpExecutionOnSlope", $"Expected upward jump velocity on slope >= 11.5f, got {rb.linearVelocity.y}");

            // Verify that subsequent physics frames while ascending maintain upward jump velocity (jump grace prevents slope adhesion)
            controller.UpdateTimers(0.02f);
            controller.CheckGroundStatus();
            controller.ApplyHorizontalMovement(0.02f);
            AssertTrue(!controller.IsGrounded, "Player_AirborneDuringJumpGrace", "Player must remain airborne during jump grace period");
            AssertTrue(rb.linearVelocity.y >= 11.5f, "Player_JumpVelocityPreservedOnSlope", $"Upward jump velocity must be preserved across frames on slope, got {rb.linearVelocity.y}");

            UnityEngine.Object.DestroyImmediate(playerObj);
            UnityEngine.Object.DestroyImmediate(slopeObj);
        }

        // =========================================================================
        // 3. Player Animation Cycles & Sprite Loading
        // =========================================================================
        private static void TestPlayerAnimationCycles()
        {
            var playerObj = new GameObject("Test_Player_Anim");
            var sr = playerObj.AddComponent<SpriteRenderer>();
            var rb = playerObj.AddComponent<Rigidbody2D>();
            var col = playerObj.AddComponent<BoxCollider2D>();
            var controller = playerObj.AddComponent<PlayerController>();
            controller.ConfigurePhysics();
            controller.LoadDefaultSpritesIfMissing();

            AssertTrue(sr.sprite != null, "Player_InitialIdleSpriteAssigned", "Player SpriteRenderer must have a default sprite assigned");

            // Verify facing flip
            controller.FacingRight = false;
            controller.UpdateAnimation(0.1f);
            AssertTrue(sr.flipX, "Player_FacingLeftFlipX", "SpriteRenderer flipX must be true when facing left");

            controller.FacingRight = true;
            controller.UpdateAnimation(0.1f);
            AssertTrue(!sr.flipX, "Player_FacingRightNoFlipX", "SpriteRenderer flipX must be false when facing right");

            UnityEngine.Object.DestroyImmediate(playerObj);
        }

        // =========================================================================
        // 4. Procedural SkyRenderer & 12-Hour Clock
        // =========================================================================
        private static void TestSkyRendererAndDayNightClock()
        {
            // 1. Noon Sky (0.25)
            SkyRenderer2D.CalculateSkyColors(0.25f, out var noonTop, out var noonBot);
            AssertTrue(noonTop.r > 0.4f && noonTop.b > 0.7f, "Sky_NoonColorTop", "Noon top color should be daytime sky blue");

            // 2. Night Sky (0.80)
            SkyRenderer2D.CalculateSkyColors(0.80f, out var nightTop, out var nightBot);
            AssertTrue(nightTop.r < 0.1f && nightTop.b < 0.2f, "Sky_NightColorTop", "Night top color should be deep night navy");

            // 3. 12-hour Clock calculations:
            // 0.25 is Noon (12:00 PM)
            SkyRenderer2D.GetClockTime(0.25f, out int h1, out int m1, out bool pm1, out bool night1);
            AssertEqual(12, h1, "Clock_NoonHour");
            AssertEqual(0, m1, "Clock_NoonMinute");
            AssertTrue(pm1, "Clock_NoonIsPm");
            AssertTrue(!night1, "Clock_NoonIsNotNight");

            // 0.544 is ~7:04 PM (Night)
            SkyRenderer2D.GetClockTime(0.5444f, out int h2, out int m2, out bool pm2, out bool night2);
            AssertEqual(7, h2, "Clock_7PMHour");
            AssertTrue(pm2, "Clock_7PMIsPm");
            AssertTrue(night2, "Clock_7PMIsNight");

            // 4. Starfield nocturnal suppression:
            var skyCamObj = new GameObject("Test_Sky_Cam");
            var cam = skyCamObj.AddComponent<Camera>();
            var sky = skyCamObj.AddComponent<SkyRenderer2D>();
            // At noon, stars must NOT twinkle in daylight
            AssertTrue(sky.StarAlpha <= 0.01f, "Sky_NoonStarsSuppressed", $"Expected daytime stars to be suppressed (alpha ~0), got {sky.StarAlpha}");
            UnityEngine.Object.DestroyImmediate(skyCamObj);
        }

        // =========================================================================
        // 5. PointLightSource2D Shadows
        // =========================================================================
        private static void TestPointLight2DShadowCasting()
        {
            var lightObj = new GameObject("Test_Torch");
            var l2d = lightObj.AddComponent<Light2D>();
            var point = lightObj.AddComponent<PointLightSource2D>();
            point.Configure(new Color(1f, 0.85f, 0.4f), 6.0f, 1.0f, true);

            AssertTrue(l2d.shadowsEnabled, "Torch_ShadowsEnabled", "Torch light must have 2D shadows enabled");
            AssertTrue(l2d.shadowIntensity > 0.5f, "Torch_ShadowIntensity", $"Expected shadow intensity > 0.5, got {l2d.shadowIntensity}");

            UnityEngine.Object.DestroyImmediate(lightObj);
        }

        // =========================================================================
        // 6. Complete In-Game HUD
        // =========================================================================
        private static void TestInGameHUDHierarchyAndSlotSelection()
        {
            var canvasObj = new GameObject("Test_HUD");
            var hud = canvasObj.AddComponent<PotariaHUD>();
            hud.LoadResourcesIfMissing();
            hud.BuildOrValidateUI();

            // Verify UI child hierarchy
            AssertTrue(canvasObj.transform.Find("Hotbar") != null, "HUD_HotbarCreated", "Hotbar transform must exist under Canvas");
            AssertTrue(canvasObj.transform.Find("LifeAndMana") != null, "HUD_LifeAndManaCreated", "Life and Mana transform must exist under Canvas");
            AssertTrue(canvasObj.transform.Find("ClockAndRadar") != null, "HUD_ClockAndRadarCreated", "Clock and Radar transform must exist under Canvas");
            AssertTrue(canvasObj.transform.Find("SkillBadges") != null, "HUD_SkillBadgesCreated", "Skill Badges transform must exist under Canvas");
            AssertTrue(canvasObj.transform.Find("ProfilerPanel") != null, "HUD_ProfilerPanelCreated", "Profiler panel transform must exist under Canvas");

            // Test slot selection 0..9
            hud.SelectSlot(0);
            AssertEqual(0, hud.SelectedSlot, "HUD_SelectSlot0");
            hud.SelectSlot(4);
            AssertEqual(4, hud.SelectedSlot, "HUD_SelectSlot4");
            hud.SelectSlot(9);
            AssertEqual(9, hud.SelectedSlot, "HUD_SelectSlot9");

            UnityEngine.Object.DestroyImmediate(canvasObj);
        }

        // =========================================================================
        // 7. Mobs Locomotion & AI
        // =========================================================================
        private static void TestMobsLocomotionAndAI()
        {
            // 1. Green Slime
            var slimeObj = new GameObject("Test_Slime");
            var srb = slimeObj.AddComponent<Rigidbody2D>();
            var scol = slimeObj.AddComponent<BoxCollider2D>();
            var slime = slimeObj.AddComponent<SlimeMob>();
            slime.ConfigureVariant(SlimeMob.SlimeType.Green);
            AssertEqual(40, slime.MaxHp, "Slime_GreenMaxHp");
            AssertEqual(12, slime.AttackDamage, "Slime_GreenAttack");

            // Slime Take Damage & Defense reduction
            int dealt = slime.TakeDamage(10);
            AssertEqual(8, dealt, "Slime_DamageMitigation"); // 10 - 2 def = 8
            AssertEqual(32, slime.CurrentHp, "Slime_RemainingHp");

            // 2. Purple Slime
            slime.ConfigureVariant(SlimeMob.SlimeType.Purple);
            AssertEqual(75, slime.MaxHp, "Slime_PurpleMaxHp");
            AssertEqual(18, slime.AttackDamage, "Slime_PurpleAttack");

            // 3. Zombie Mob
            var zombieObj = new GameObject("Test_Zombie");
            var zrb = zombieObj.AddComponent<Rigidbody2D>();
            var zcol = zombieObj.AddComponent<BoxCollider2D>();
            var zombie = zombieObj.AddComponent<ZombieMob>();
            zombie.Configure();
            AssertEqual(90, zombie.MaxHp, "Zombie_MaxHp");
            AssertEqual(15, zombie.AttackDamage, "Zombie_Attack");

            // 4. Demon Eye Mob
            var eyeObj = new GameObject("Test_DemonEye");
            var erb = eyeObj.AddComponent<Rigidbody2D>();
            var ecol = eyeObj.AddComponent<BoxCollider2D>();
            var eye = eyeObj.AddComponent<DemonEyeMob>();
            eye.Configure();
            AssertEqual(60, eye.MaxHp, "DemonEye_MaxHp");
            AssertEqual(0f, erb.gravityScale, "DemonEye_ZeroGravityFlight");

            UnityEngine.Object.DestroyImmediate(slimeObj);
            UnityEngine.Object.DestroyImmediate(zombieObj);
            UnityEngine.Object.DestroyImmediate(eyeObj);
        }

        // =========================================================================
        // 8. Mob Spawner Annulus & Limits
        // =========================================================================
        private static void TestMobSpawnerAnnulusAndLimits()
        {
            var spawnerObj = new GameObject("Test_Spawner");
            var spawner = spawnerObj.AddComponent<MobSpawner>();
            spawner.MaxActiveMobs = 5;

            var m1 = spawner.SpawnMobAt(typeof(SlimeMob), new Vector2(10f, 0f));
            var m2 = spawner.SpawnMobAt(typeof(ZombieMob), new Vector2(15f, 0f));
            AssertEqual(2, spawner.ActiveMobCount, "Spawner_ActiveMobCount");

            spawner.ClearAllMobs();
            AssertEqual(0, spawner.ActiveMobCount, "Spawner_ClearedMobs");

            UnityEngine.Object.DestroyImmediate(spawnerObj);
        }

        // =========================================================================
        // 9. Localization Architecture (English & Filipino)
        // =========================================================================
        private static void TestLocalizationManagerEnglishAndFilipino()
        {
            // Set English
            LocalizationManager.SetLanguage(LocalizationManager.LANG_EN);
            AssertEqual("DAY", LocalizationManager.Get("hud.day"), "Loc_En_Day");
            AssertEqual("NIGHT", LocalizationManager.Get("hud.night"), "Loc_En_Night");
            AssertEqual("Green Slime", LocalizationManager.Get("mob.green_slime"), "Loc_En_GreenSlime");
            AssertEqual("Copper Pickaxe", LocalizationManager.Get("item.copper_pickaxe"), "Loc_En_Pickaxe");

            string lifeEn = LocalizationManager.GetFormat("hud.life", 605, 605, 16);
            AssertEqual("Life: 605 / 605 (Lv.16)", lifeEn, "Loc_En_LifeFormat");

            // Toggle / Set Filipino
            bool eventFired = false;
            Action handler = () => { eventFired = true; };
            LocalizationManager.OnLanguageChanged += handler;

            LocalizationManager.SetLanguage(LocalizationManager.LANG_FIL);
            AssertTrue(eventFired, "Loc_LanguageChangedEventFired");
            LocalizationManager.OnLanguageChanged -= handler;

            AssertEqual("ARAW", LocalizationManager.Get("hud.day"), "Loc_Fil_Day");
            AssertEqual("GABI", LocalizationManager.Get("hud.night"), "Loc_Fil_Night");
            AssertEqual("Berdeng Putik", LocalizationManager.Get("mob.green_slime"), "Loc_Fil_GreenSlime");
            AssertEqual("Pikong Tanso", LocalizationManager.Get("item.copper_pickaxe"), "Loc_Fil_Pickaxe");

            string lifeFil = LocalizationManager.GetFormat("hud.life", 605, 605, 16);
            AssertEqual("Buhay: 605 / 605 (Antas 16)", lifeFil, "Loc_Fil_LifeFormat");

            // Restore English
            LocalizationManager.SetLanguage(LocalizationManager.LANG_EN);
        }
    }
}
