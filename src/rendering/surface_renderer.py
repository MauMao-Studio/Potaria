"""
Potaria - Renderer Hardware Abstraction Layer (HAL)
SurfaceRenderer Implementation (Native Pygame-ce Software Blitting)
Developer: Kurados
Engine: Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)
"""

from typing import Optional, Tuple, Union
import os
import pygame
from src.rendering.base_renderer import BaseRenderer, RENDERER_SOFTWARE

os.environ.setdefault("SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS", "0")


class SurfaceRenderer(BaseRenderer):
    """
    Native Pygame-ce Software Renderer.
    Wraps standard SDL 2 blitting operations, maintaining 100% exact parity
    with the existing game engine and full compatibility across all environments.
    """

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        title: str = "Potaria",
        fullscreen: bool = False,
    ):
        super().__init__(width=width, height=height, title=title, fullscreen=fullscreen)
        self.surface: Optional[pygame.Surface] = None
        self.ui_surface: Optional[pygame.Surface] = None
        self.display_width: int = width
        self.display_height: int = height
        self.shaders_enabled: bool = True
        self.bloom_enabled: bool = False
        self.bloom_intensity: float = 0.0
        self.bloom_threshold: float = 0.65
        self.vignette_enabled: bool = False
        self.vignette_intensity: float = 0.35
        self.water_distortion_enabled: bool = False
        self.water_distortion_intensity: float = 1.0
        self.color_grading_mode: int = 0
        self.saturation: float = 1.0
        self.contrast: float = 1.0
        self.lighting_quality: str = "high"
        self.particle_density: str = "high"
        self.last_batch_count: int = 0
        self.total_batched_projectiles: int = 0

    def _get_desktop_resolution(self) -> Tuple[int, int]:
        """Returns the primary monitor desktop resolution for borderless fullscreen."""
        desktop_sizes = getattr(pygame.display, "get_desktop_sizes", lambda: [])()
        if desktop_sizes:
            return desktop_sizes[0]
        info = pygame.display.Info()
        w = getattr(info, "current_w", 0)
        h = getattr(info, "current_h", 0)
        if w > 0 and h > 0:
            return (w, h)
        return (1920, 1080)

    def _sync_window_frame_and_pos(self):
        """Synchronizes SDL2 window borderless frame, size, and position for runtime fullscreen toggling."""
        try:
            win_cls = getattr(getattr(pygame, "window", None), "Window", None)
            if win_cls and hasattr(win_cls, "from_display_module"):
                win = win_cls.from_display_module()
                if self.fullscreen:
                    win.borderless = True
                    win.size = self._get_desktop_resolution()
                    win.position = (0, 0)
                else:
                    win.borderless = False
                    win.size = (
                        getattr(self, "display_width", self.width),
                        getattr(self, "display_height", self.height),
                    )
                    if hasattr(pygame, "WINDOWPOS_CENTERED"):
                        win.position = (pygame.WINDOWPOS_CENTERED, pygame.WINDOWPOS_CENTERED)
        except Exception:
            pass

    def initialize(self) -> bool:
        """Initializes the Pygame display mode with double-buffering and crisp scaling."""
        if not pygame.get_init():
            pygame.init()

        os.environ["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"
        if self.title:
            pygame.display.set_caption(self.title)

        flags = pygame.DOUBLEBUF | pygame.SCALED
        if self.fullscreen:
            os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
            flags |= pygame.NOFRAME
        else:
            os.environ["SDL_VIDEO_WINDOW_POS"] = "centered"

        try:
            self.surface = pygame.display.set_mode((self.width, self.height), flags)
            self._sync_window_frame_and_pos()
        except pygame.error:
            # Fallback for environments where SCALED or NOFRAME might fail (e.g., dummy driver)
            try:
                fallback_flags = pygame.DOUBLEBUF
                if self.fullscreen:
                    fallback_flags |= pygame.NOFRAME
                self.surface = pygame.display.set_mode((self.width, self.height), fallback_flags)
                self._sync_window_frame_and_pos()
            except pygame.error:
                self.surface = pygame.display.set_mode((self.width, self.height))

        self.initialized = True
        return True

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)):
        """Fills the primary display surface with a solid color and clears the UI layer."""
        if self.surface:
            self.surface.fill(color)
        if self.ui_surface:
            self.ui_surface.fill((0, 0, 0, 0))

    def draw_sprite(
        self,
        surface: pygame.Surface,
        dest: Union[Tuple[int, int], pygame.Rect],
        area: Optional[pygame.Rect] = None,
        special_flags: int = 0,
    ):
        """Blits a sprite surface directly to the target surface."""
        if self.surface:
            self.surface.blit(surface, dest, area, special_flags)

    def draw_surface(
        self,
        surface: pygame.Surface,
        dest: Union[Tuple[int, int], pygame.Rect],
        area: Optional[pygame.Rect] = None,
        special_flags: int = 0,
    ):
        """Blits an arbitrary surface directly to the target surface."""
        if self.surface:
            self.surface.blit(surface, dest, area, special_flags)

    def draw_rect(
        self,
        color: Union[Tuple[int, int, int], Tuple[int, int, int, int]],
        rect: Union[pygame.Rect, Tuple[int, int, int, int]],
        width: int = 0,
        border_radius: int = 0,
    ):
        """Draws a geometric rectangle onto the display surface."""
        if self.surface:
            pygame.draw.rect(self.surface, color, rect, width=width, border_radius=border_radius)

    def draw_text(
        self,
        font: pygame.font.Font,
        text: str,
        pos: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        antialias: bool = True,
    ) -> pygame.Rect:
        """Renders text and blits it at the given coordinates."""
        if self.surface:
            rendered = font.render(text, antialias, color)
            return self.surface.blit(rendered, pos)
        return pygame.Rect(pos[0], pos[1], 0, 0)

    def draw_line(
        self,
        color: Tuple[int, int, int],
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        width: int = 1,
    ):
        """Draws a line on the display surface."""
        if self.surface:
            pygame.draw.line(self.surface, color, start_pos, end_pos, width)

    def draw_circle(
        self,
        color: Tuple[int, int, int],
        center: Tuple[int, int],
        radius: float,
        width: int = 0,
    ):
        """Draws a circle on the display surface."""
        if self.surface:
            pygame.draw.circle(self.surface, color, center, int(radius), width)

    def present(self):
        """Presents the frame by compositing the UI layer and flipping the display buffer."""
        if self.surface and self.ui_surface:
            self.surface.blit(self.ui_surface, (0, 0))
        pygame.display.flip()

    def get_surface(self) -> pygame.Surface:
        """Returns the active display surface for seamless compatibility."""
        if self.surface is None:
            self.initialize()
        return self.surface

    def get_ui_surface(self) -> pygame.Surface:
        """Returns the dedicated UI surface for clean, bloom-free interface rendering."""
        if self.ui_surface is None or self.ui_surface.get_size() != (self.width, self.height):
            self.ui_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        return self.ui_surface

    def set_mode(self, width: int, height: int, fullscreen: bool = False) -> bool:
        """Reconfigures resolution and fullscreen state."""
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        return self.initialize()

    def set_display_resolution(self, width: int, height: int, fullscreen: Optional[bool] = None) -> bool:
        """Sets target display resolution mode."""
        prev_fs = self.fullscreen
        fs = self.fullscreen if fullscreen is None else fullscreen
        self.display_width = width
        self.display_height = height
        self.fullscreen = fs
        if fs != prev_fs:
            return self.set_mode(self.width, self.height, fullscreen=fs)
        try:
            win = pygame.window.Window.from_display_module()
            if not fs:
                win.borderless = False
                win.size = (width, height)
            else:
                win.borderless = True
                win.size = self._get_desktop_resolution()
                win.position = (0, 0)
            return True
        except Exception:
            return self.set_mode(self.width, self.height, fullscreen=fs)

    def is_hardware_accelerated(self) -> bool:
        """SurfaceRenderer uses CPU-side software blitting."""
        return False

    def get_renderer_type(self) -> str:
        """Returns 'software'."""
        return RENDERER_SOFTWARE

    def draw_projectiles_batch(
        self,
        projectiles: list,
        camera: Optional[any] = None,
    ) -> int:
        """
        Renders a high-density batch of projectiles using optimized C-level multi-blitting.
        Returns the count of successfully rendered projectiles.
        """
        if not self.surface or not projectiles:
            return 0

        target_surf = self.surface
        rendered_count = 0
        batch_blits = []

        sw = self.width
        sh = self.height

        for p in projectiles:
            if isinstance(p, tuple):
                if len(p) >= 2 and isinstance(p[0], pygame.Surface):
                    batch_blits.append((p[0], p[1]))
                    rendered_count += 1
                continue

            if hasattr(p, "life") and p.life <= 0:
                continue

            if hasattr(p, "x") and hasattr(p, "y"):
                px = float(p.x)
                py = float(p.y)
            elif hasattr(p, "pos") and hasattr(p.pos, "x") and hasattr(p.pos, "y"):
                px = float(p.pos.x)
                py = float(p.pos.y)
            else:
                px, py = None, None

            if px is not None and py is not None:
                if camera and hasattr(camera, "world_to_screen"):
                    sx, sy = camera.world_to_screen(px, py)
                else:
                    sx, sy = px, py

                rad = getattr(p, "radius", 10.0)
                pad = int(rad + 32)
                if sx < -pad or sx > sw + pad or sy < -pad or sy > sh + pad:
                    continue

                if getattr(p, "sprite", None) is not None and getattr(p, "shape", "") == "sprite":
                    sp = p.sprite
                    batch_blits.append((sp, (int(sx - sp.get_width() // 2), int(sy - sp.get_height() // 2))))
                    rendered_count += 1
                elif hasattr(p, "shape") and hasattr(p, "color"):
                    import math
                    from src.entities.bullet_hell import get_bullet_surface
                    angle_deg = math.degrees(math.atan2(getattr(p, "vy", 0.0), getattr(p, "vx", 1.0)))
                    bsurf = get_bullet_surface(
                        shape=p.shape,
                        color=p.color,
                        core_color=getattr(p, "core_color", (255, 255, 255)),
                        radius=int(rad),
                        angle_deg=angle_deg,
                    )
                    hw = bsurf.get_width() // 2
                    hh = bsurf.get_height() // 2
                    batch_blits.append((bsurf, (int(sx - hw), int(sy - hh))))
                    rendered_count += 1
                elif hasattr(p, "render"):
                    p.render(target_surf, camera)
                    rendered_count += 1
            elif hasattr(p, "render"):
                p.render(target_surf, camera)
                rendered_count += 1

        if batch_blits:
            target_surf.fblits(batch_blits)

        self.last_batch_count = rendered_count
        self.total_batched_projectiles += rendered_count
        return rendered_count

    def set_bloom_enabled(self, enabled: bool):
        self.bloom_enabled = bool(enabled)

    def set_bloom_intensity(self, intensity: float):
        self.bloom_intensity = max(0.0, min(5.0, float(intensity)))

    def set_bloom_threshold(self, threshold: float):
        self.bloom_threshold = max(0.0, min(1.0, float(threshold)))

    def get_bloom_params(self) -> dict:
        return {
            "enabled": self.bloom_enabled,
            "intensity": self.bloom_intensity,
            "threshold": self.bloom_threshold,
        }

    def set_shaders_enabled(self, enabled: bool):
        self.shaders_enabled = bool(enabled)

    def is_shaders_enabled(self) -> bool:
        return self.shaders_enabled

    def set_vignette_enabled(self, enabled: bool):
        self.vignette_enabled = bool(enabled)

    def set_vignette_intensity(self, intensity: float):
        self.vignette_intensity = max(0.0, min(1.0, float(intensity)))

    def set_water_distortion_enabled(self, enabled: bool):
        self.water_distortion_enabled = bool(enabled)

    def set_water_distortion_intensity(self, intensity: float):
        self.water_distortion_intensity = max(0.0, min(3.0, float(intensity)))

    def set_color_grading_mode(self, mode: Union[int, str]):
        if isinstance(mode, str):
            mapping = {"standard": 0, "vibrant": 1, "cinematic": 2, "cool": 3}
            self.color_grading_mode = mapping.get(mode.lower().strip(), 0)
        else:
            self.color_grading_mode = int(mode)

    def set_saturation(self, saturation: float):
        self.saturation = max(0.0, min(2.5, float(saturation)))

    def set_contrast(self, contrast: float):
        self.contrast = max(0.0, min(2.5, float(contrast)))

    def set_lighting_quality(self, quality: str):
        self.lighting_quality = str(quality).lower().strip()

    def set_particle_density(self, density: str):
        self.particle_density = str(density).lower().strip()

    def get_graphics_params(self) -> dict:
        return {
            "shaders_enabled": self.shaders_enabled,
            "bloom_enabled": self.bloom_enabled,
            "bloom_intensity": self.bloom_intensity,
            "bloom_threshold": self.bloom_threshold,
            "vignette_enabled": self.vignette_enabled,
            "vignette_intensity": self.vignette_intensity,
            "water_distortion_enabled": self.water_distortion_enabled,
            "water_distortion_intensity": self.water_distortion_intensity,
            "color_grading_mode": self.color_grading_mode,
            "saturation": self.saturation,
            "contrast": self.contrast,
            "lighting_quality": self.lighting_quality,
            "particle_density": self.particle_density,
        }

    def cleanup(self):
        """Releases renderer resources."""
        self.surface = None
        self.ui_surface = None
        self.initialized = False
