import pygame
import time
import sys
import os

# Ensure we can import src modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import PotariaGame
from src.constants import STATE_PLAYING

def run_benchmark():
    pygame.init()
    game = PotariaGame()
    
    # Force into playing state immediately
    game.menu.state = STATE_PLAYING
    # Just start the game
    game.profiler.enabled = True
    game.show_profiler = True
    
    # We want to run exactly 300 frames
    num_frames = 300
    
    print("Starting benchmark for 300 frames...")
    
    start_time = time.time()
    
    for i in range(num_frames):
        # 1. Process Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        # 2. Update Simulation
        dt = 1.0 / 60.0
        
        game.profiler.start_frame()
        
        # Manually run handle_events to consume inputs if needed, though we just process quit above
        # Instead, just call update_gameplay and render
        game.update_gameplay(dt)
        game.render()
        
        game.profiler.end_frame()
        
        if (i + 1) % 50 == 0:
            print(f"Completed {i + 1} frames...")

    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "="*50)
    print("BENCHMARK RESULTS")
    print("="*50)
    print(f"Total time for {num_frames} frames: {total_time:.2f} seconds")
    print(f"Average Benchmark FPS: {num_frames / total_time:.2f}")
    print("\nProfiler Stats (from game.profiler):")
    print(game.profiler.get_summary_line())
    print("\nSubsystem Breakdown:")
    
    # We use game.profiler.section_averages to print percentage breakdown
    display_order = [
        "input", "update_player", "update_combat", "update_world", 
        "update_lighting", "update_other", "render_sky", "render_world", 
        "render_particles", "render_combat", "render_lighting", "render_hud", "present"
    ]
    
    for sec in display_order:
        ms = game.profiler.section_averages.get(sec, 0.0)
        pct = (ms / game.profiler.avg_frame_ms * 100.0) if game.profiler.avg_frame_ms > 0 else 0.0
        label = sec.replace("_", " ").title()
        print(f"  {label:<18}: {ms:5.2f} ms ({pct:4.1f}%)")
        
    print("="*50)
    pygame.quit()

if __name__ == "__main__":
    run_benchmark()
