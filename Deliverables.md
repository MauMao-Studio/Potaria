# Potaria Performance Optimization Deliverables

## A. Performance Report
- **Total frames measured:** 300
- **Total time:** 2.64 seconds
- **Average Benchmark FPS:** 113.72
- **Profiler FPS:** 111.3
- **1% Low FPS:** 79.3
- **Average Frame Time:** 8.99 ms
- **Max Frame Time:** 131.6 ms
- **Overall Result:** The game easily sustains over 100 FPS on average, hitting a solid 1% low well above the 60 FPS target.

## B. Bottleneck Report
- **Render Sky:** 1.69 ms (18.8%)
- **Render World:** 1.40 ms (15.6%)
- **Update World:** 1.05 ms (11.7%)
- **Render Lighting:** 0.92 ms (10.2%)
- **Render Hud:** 0.74 ms (8.2%)
- All other tracked subsystems (Input, Player, Combat, Particles) consumed < 0.20 ms each.

## C. Optimization Changelog
- **Lighting Optimization:** The BFS lighting algorithm was heavily optimized using `absorb_grid` caching and pre-mapped RGB integers in `src/world/lighting.py`, reducing lighting update costs from ~3.5 ms down to a negligible 0.02 ms per frame.
- **Profiler Integration:** Full profiler instrumentation was injected into `main.py`’s `update_gameplay` and `render` functions using the `PotariaProfiler` class.
- **Profiler Fix:** Fixed an overwrite bug in `profiler.py` to correctly accumulate time spent in subsections (e.g. `update_other`) multiple times per frame.
- **On-Screen Diagnostics:** Implemented the F3 toggle to display real-time subsystem breakdown metrics directly on the screen without impacting frame timings.
- **World Rendering:** World chunks are now actively cached using baked surfaces to limit Pygame blitting overhead to just 6-9 surfaces instead of thousands of individual tiles.

## D. Remaining Bottlenecks
- **Sky Rendering (1.69 ms):** Due to the active iteration over 90 stars calculating sine waves and applying `set_at()` pixel mutations each frame during nighttime.
- **World Rendering (1.40 ms):** Although chunk baking is highly efficient, drawing chunk surfaces combined with dynamic overlay animations (water frames and torches) still dominates frame time.
- **World Update (1.05 ms):** Logic updating Town NPCs, particles, and chunks.

## E. Future Optimization Recommendations
1. **Pre-Rendered Starfield Layers:** The twinkling star logic in `sky.py` should be baked into 3 to 4 distinct semi-transparent star layers that are panned/toggled at different opacities, avoiding costly per-pixel `set_at()` calls.
2. **Dynamic Chunk Throttling:** Throttle off-screen Town NPC and particle logic when they aren't near the player's viewport or if FPS drops.
3. **Dirty-Region Based Screen Updates:** Track explicitly what regions of the screen changed and only pass those rects to `pygame.display.update(rects)` instead of flipping the full screen every frame.
