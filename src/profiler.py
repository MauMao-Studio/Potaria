"""
Potaria - Lightweight Real-Time Performance Profiler & Frame-Time Telemetry
Instruments gameplay update & rendering pipelines with high-resolution timers.
Zero overhead when disabled.
Developer: Kurados
"""
import time
import collections

class ProfilerSection:
    __slots__ = ("name", "profiler")

    def __init__(self, name, profiler):
        self.name = name
        self.profiler = profiler

    def __enter__(self):
        if self.profiler.enabled:
            self.profiler._section_starts[self.name] = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.profiler.enabled:
            t1 = time.perf_counter()
            t0 = self.profiler._section_starts.pop(self.name, t1)
            delta = (t1 - t0) * 1000.0
            self.profiler._current_frame_sections[self.name] = self.profiler._current_frame_sections.get(self.name, 0.0) + delta


class PotariaProfiler:
    def __init__(self, history_size=120):
        self.enabled = False
        self.history_size = history_size
        self._frame_start = 0.0
        self._section_starts = {}
        self._current_frame_sections = {}

        self.frame_times = collections.deque(maxlen=history_size)
        self.section_history = collections.defaultdict(lambda: collections.deque(maxlen=history_size))

        # Cached statistics
        self.avg_fps = 0.0
        self.one_percent_low_fps = 0.0
        self.point_one_percent_low_fps = 0.0
        self.avg_frame_ms = 0.0
        self.max_frame_ms = 0.0
        self.min_frame_ms = 0.0
        self.section_averages = {}

        self._stats_update_timer = 0.0

    def start_frame(self):
        if not self.enabled:
            return
        self._frame_start = time.perf_counter()
        self._current_frame_sections.clear()

    def end_frame(self):
        if not self.enabled:
            return
        t_end = time.perf_counter()
        frame_ms = (t_end - self._frame_start) * 1000.0
        self.frame_times.append(frame_ms)

        for sec_name, sec_ms in self._current_frame_sections.items():
            self.section_history[sec_name].append(sec_ms)

        self._recalculate_stats()

    def section(self, name):
        """Context manager for timing a named execution section."""
        return ProfilerSection(name, self)

    def start_section(self, name):
        """Explicit section start timer."""
        if self.enabled:
            self._section_starts[name] = time.perf_counter()

    def end_section(self, name):
        """Explicit section end timer."""
        if self.enabled:
            t1 = time.perf_counter()
            t0 = self._section_starts.pop(name, t1)
            delta = (t1 - t0) * 1000.0
            self._current_frame_sections[name] = self._current_frame_sections.get(name, 0.0) + delta

    def _recalculate_stats(self):
        if not self.frame_times:
            return

        times = list(self.frame_times)
        n = len(times)
        self.avg_frame_ms = sum(times) / n
        self.max_frame_ms = max(times)
        self.min_frame_ms = min(times)

        self.avg_fps = (1000.0 / self.avg_frame_ms) if self.avg_frame_ms > 0 else 0.0

        sorted_times = sorted(times)
        p99_idx = min(n - 1, int(n * 0.99))
        p999_idx = min(n - 1, int(n * 0.999))

        low_99_ms = sorted_times[p99_idx]
        low_999_ms = sorted_times[p999_idx]

        self.one_percent_low_fps = (1000.0 / low_99_ms) if low_99_ms > 0 else 0.0
        self.point_one_percent_low_fps = (1000.0 / low_999_ms) if low_999_ms > 0 else 0.0

        for sec_name, vals in self.section_history.items():
            if vals:
                self.section_averages[sec_name] = sum(vals) / len(vals)

    def get_summary_line(self):
        """Returns single-line performance summary string."""
        return (
            f"FPS: {self.avg_fps:.1f} (1% Low: {self.one_percent_low_fps:.1f}, "
            f"Max: {self.max_frame_ms:.1f}ms, Avg: {self.avg_frame_ms:.2f}ms)"
        )

    def render_overlay(self, screen, font, x=10, y=70):
        """Draws the detailed real-time profiler overlay on screen."""
        if not self.enabled:
            return

        import pygame

        lines = [
            "--- POTARIA REAL-TIME PROFILER (F3) ---",
            self.get_summary_line(),
            f"Frame Budget (60 FPS = 16.67ms): {self.avg_frame_ms / 16.67 * 100.0:.1f}% used",
            "-" * 42,
            "BREAKDOWN (Average per frame):"
        ]

        # Order sections logically
        display_order = [
            "input",
            "update_player",
            "update_combat",
            "update_world",
            "update_lighting",
            "update_other",
            "render_sky",
            "render_world",
            "render_particles",
            "render_combat",
            "render_lighting",
            "render_hud",
            "present"
        ]

        total_tracked = sum(self.section_averages.get(s, 0.0) for s in display_order)

        for sec in display_order:
            ms = self.section_averages.get(sec, 0.0)
            pct = (ms / self.avg_frame_ms * 100.0) if self.avg_frame_ms > 0 else 0.0
            label = sec.replace("_", " ").title()
            lines.append(f"  {label:<18}: {ms:5.2f} ms ({pct:4.1f}%)")

        for sec, ms in self.section_averages.items():
            if sec not in display_order and sec != "total_frame":
                pct = (ms / self.avg_frame_ms * 100.0) if self.avg_frame_ms > 0 else 0.0
                lines.append(f"  {sec:<18}: {ms:5.2f} ms ({pct:4.1f}%)")

        max_w = 0
        rendered = []
        for line in lines:
            col = (255, 230, 80) if line.startswith("---") or line.startswith("FPS") else (220, 230, 245)
            s = font.render(line, True, col)
            max_w = max(max_w, s.get_width())
            rendered.append(s)

        padding = 8
        line_h = 16
        bg_w = max_w + padding * 2
        bg_h = len(rendered) * line_h + padding * 2

        bg_surf = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        bg_surf.fill((12, 16, 26, 225))
        screen.blit(bg_surf, (x, y))
        pygame.draw.rect(screen, (80, 100, 140, 200), (x, y, bg_w, bg_h), 1, border_radius=4)

        cur_y = y + padding
        for s in rendered:
            screen.blit(s, (x + padding, cur_y))
            cur_y += line_h
