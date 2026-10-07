"""
Potaria Headless & Automated Benchmark Tool
Measures reproducible performance baseline across representative gameplay scenarios.
"""
import os
import sys
import time
import math
import random

# Headless video driver so it runs anywhere without needing physical window interaction
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import PotariaGame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, STATE_PLAYING,
    WORLD_TYPE_INFINITE, DIFFICULTY_NORMAL, MODE_ADVENTURE
)

def run_benchmark(num_frames=600, scenario="heavy"):
    print(f"=== Starting Potaria Performance Benchmark ({scenario}, {num_frames} frames) ===")
    game = PotariaGame()
    # Start singleplayer world directly
    game.reset_new_session("BenchmarkWorld", WORLD_TYPE_INFINITE, DIFFICULTY_NORMAL, MODE_ADVENTURE, seed=12345)
    game.menu.state = STATE_PLAYING
    game.paused = False

    # Warm up world chunks and audio
    for _ in range(30):
        game.update_gameplay(1.0 / 60.0)
        game.render()

    if scenario == "heavy":
        # Spawn representative monsters, mini-boss, projectiles
        game.execute_cheat("/spawn zombie 8")
        game.execute_cheat("/spawn slime 8")
        game.execute_cheat("/spawn bat 6")
        game.execute_cheat("/spawn ignis 1")
        game.execute_cheat("/weapons")

    # Metrics collectors
    frame_times = []
    section_times = {
        "input": [],
        "update_player": [],
        "update_combat": [],
        "update_world": [],
        "update_lighting": [],
        "update_other": [],
        "render_sky": [],
        "render_world": [],
        "render_particles": [],
        "render_combat": [],
        "render_lighting": [],
        "render_hud": [],
        "render_other": [],
        "present": [],
        "total_frame": []
    }

    start_bench = time.perf_counter()

    for f in range(num_frames):
        t0 = time.perf_counter()
        dt = 1.0 / 60.0

        # Simulate player movement & actions
        game.player.x += math.sin(f * 0.05) * 4.0
        game.player.y += math.cos(f * 0.03) * 1.5
        if f % 15 == 0:
            # Player swings weapon or shoots
            game.handle_primary_action(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2)

        # 1. Input handling
        t_input_start = time.perf_counter()
        # Mock event processing
        pygame.event.pump()
        t_input_end = time.perf_counter()
        section_times["input"].append((t_input_end - t_input_start) * 1000.0)

        # 2. Gameplay Updates with detailed section timings
        t_up_start = time.perf_counter()
        
        # Player
        t_pl_0 = time.perf_counter()
        game.player.update(dt, game.world)
        game.camera.set_target(game.player.center_x, game.player.center_y)
        game.camera.update(dt)
        t_pl_1 = time.perf_counter()
        section_times["update_player"].append((t_pl_1 - t_pl_0) * 1000.0)

        # World
        t_w_0 = time.perf_counter()
        game.world.update(dt)
        t_w_1 = time.perf_counter()
        section_times["update_world"].append((t_w_1 - t_w_0) * 1000.0)

        # Combat & Entities
        t_c_0 = time.perf_counter()
        game.combat.update(dt, game.world, game.player, game.sky.is_night)
        t_c_1 = time.perf_counter()
        section_times["update_combat"].append((t_c_1 - t_c_0) * 1000.0)

        # Lighting computation
        t_l_0 = time.perf_counter()
        min_tx = int(game.camera.x // 32) - 1
        max_tx = int((game.camera.x + SCREEN_WIDTH) // 32) + 2
        min_ty = max(0, int(game.camera.y // 32) - 1)
        max_ty = min(game.world.height - 1, int((game.camera.y + SCREEN_HEIGHT) // 32) + 2)
        game.lighting.compute_viewport_light(
            game.world, min_tx, min_ty, max_tx, max_ty,
            ambient_sunlight=game.sky.ambient_sunlight
        )
        t_l_1 = time.perf_counter()
        section_times["update_lighting"].append((t_l_1 - t_l_0) * 1000.0)

        # Other updates (sky, inventory, particles)
        t_o_0 = time.perf_counter()
        game.sky.update(dt)
        game.inventory.update(dt)
        game.particle_system.update(dt)
        if game.vfx_manager:
            game.vfx_manager.update(dt)
        t_o_1 = time.perf_counter()
        section_times["update_other"].append((t_o_1 - t_o_0) * 1000.0)

        # 3. Rendering sections
        # Sky
        t_r_sky_0 = time.perf_counter()
        game.sky.render(game.screen, game.camera)
        t_r_sky_1 = time.perf_counter()
        section_times["render_sky"].append((t_r_sky_1 - t_r_sky_0) * 1000.0)

        # World
        t_r_w_0 = time.perf_counter()
        game.world.render(game.screen, game.camera)
        t_r_w_1 = time.perf_counter()
        section_times["render_world"].append((t_r_w_1 - t_r_w_0) * 1000.0)

        # Particles
        t_r_p_0 = time.perf_counter()
        game.particle_system.render(game.screen, game.camera)
        t_r_p_1 = time.perf_counter()
        section_times["render_particles"].append((t_r_p_1 - t_r_p_0) * 1000.0)

        # Combat (Mobs, Boss, Projectiles, Dropped Items)
        t_r_c_0 = time.perf_counter()
        game.combat.render(game.screen, game.camera)
        active_item = game.inventory.get_active_item()
        held_icon = game.asset_factory.items.get(active_item.item_id) if active_item else None
        game.player.render(game.screen, game.camera, held_item_icon=held_icon, held_item=active_item)
        t_r_c_1 = time.perf_counter()
        section_times["render_combat"].append((t_r_c_1 - t_r_c_0) * 1000.0)

        # Lighting Blit
        t_r_l_0 = time.perf_counter()
        cam_x = int(round(game.camera.x - game.camera.shake_offset_x))
        cam_y = int(round(game.camera.y - game.camera.shake_offset_y))
        min_tx = int(cam_x // 32) - 1
        min_ty = max(0, int(cam_y // 32) - 1)
        light_screen_x = min_tx * 32 - cam_x
        light_screen_y = min_ty * 32 - cam_y
        game.lighting.render_lighting(game.screen, light_screen_x, light_screen_y)
        t_r_l_1 = time.perf_counter()
        section_times["render_lighting"].append((t_r_l_1 - t_r_l_0) * 1000.0)

        # HUD & UI
        t_r_h_0 = time.perf_counter()
        game.hud.render(
            game.screen, game.player, game.inventory, game.crafting,
            game.camera, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            world=game.world, combat=game.combat
        )
        t_r_h_1 = time.perf_counter()
        section_times["render_hud"].append((t_r_h_1 - t_r_h_0) * 1000.0)

        # Present / Flip
        t_pres_0 = time.perf_counter()
        pygame.display.flip()
        t_pres_1 = time.perf_counter()
        section_times["present"].append((t_pres_1 - t_pres_0) * 1000.0)

        t_end = time.perf_counter()
        frame_ms = (t_end - t0) * 1000.0
        frame_times.append(frame_ms)
        section_times["total_frame"].append(frame_ms)

    total_bench_time = time.perf_counter() - start_bench
    avg_frame_ms = sum(frame_times) / len(frame_times)
    max_frame_ms = max(frame_times)
    min_frame_ms = min(frame_times)

    sorted_times = sorted(frame_times)
    p99_idx = int(len(sorted_times) * 0.99)
    p999_idx = min(len(sorted_times) - 1, int(len(sorted_times) * 0.999))
    one_percent_low_ms = sorted_times[p99_idx]
    point_one_low_ms = sorted_times[p999_idx]

    avg_fps = 1000.0 / avg_frame_ms if avg_frame_ms > 0 else 0
    one_percent_fps = 1000.0 / one_percent_low_ms if one_percent_low_ms > 0 else 0
    point_one_fps = 1000.0 / point_one_low_ms if point_one_low_ms > 0 else 0

    print("\n" + "=" * 55)
    print(f"BENCHMARK RESULTS: {scenario.upper()} SCENARIO ({num_frames} frames)")
    print("=" * 55)
    print(f"Average FPS:        {avg_fps:.1f} FPS")
    print(f"1% Low FPS:         {one_percent_fps:.1f} FPS")
    print(f"0.1% Low FPS:       {point_one_fps:.1f} FPS")
    print(f"Average Frame Time: {avg_frame_ms:.2f} ms")
    print(f"Maximum Frame Time: {max_frame_ms:.2f} ms")
    print(f"Minimum Frame Time: {min_frame_ms:.2f} ms")
    print("-" * 55)
    print("SECTION BREAKDOWN (Average ms & % of frame):")
    for sec_name, vals in section_times.items():
        if sec_name == "total_frame" or not vals:
            continue
        avg_s = sum(vals) / len(vals)
        pct = (avg_s / avg_frame_ms) * 100.0 if avg_frame_ms > 0 else 0
        print(f"  {sec_name:<20}: {avg_s:6.3f} ms  ({pct:5.1f}%)")
    print("=" * 55 + "\n")

    return {
        "avg_fps": avg_fps,
        "one_percent_fps": one_percent_fps,
        "point_one_fps": point_one_fps,
        "avg_frame_ms": avg_frame_ms,
        "max_frame_ms": max_frame_ms,
        "sections": {k: (sum(v)/len(v) if v else 0.0) for k, v in section_times.items()}
    }

if __name__ == "__main__":
    run_benchmark(num_frames=300, scenario="heavy")
