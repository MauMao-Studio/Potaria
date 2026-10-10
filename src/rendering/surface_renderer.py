"""
Potaria - Renderer Hardware Abstraction Layer (HAL)
SurfaceRenderer Implementation (Native Pygame-ce Software Blitting)
Developer: Kurados
Engine: Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)
"""

from typing import Optional, Tuple, Union
import pygame
from src.rendering.base_renderer import BaseRenderer, RENDERER_SOFTWARE


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
        self.bloom_enabled: bool = False
        self.bloom_intensity: float = 0.0
        self.bloom_threshold: float = 0.65
        self.last_batch_count: int = 0
        self.total_batched_projectiles: int = 0

    def initialize(self) -> bool:
        """Initializes the Pygame display mode with double-buffering and crisp scaling."""
        if not pygame.get_init():
            pygame.init()

        if self.title:
            pygame.display.set_caption(self.title)

        flags = pygame.DOUBLEBUF | pygame.SCALED
        if self.fullscreen:
            flags |= pygame.FULLSCREEN

        try:
            self.surface = pygame.display.set_mode((self.width, self.height), flags)
        except pygame.error:
            # Fallback for environments where SCALED or FULLSCREEN might fail (e.g., dummy driver)
            try:
                fallback_flags = pygame.DOUBLEBUF
                if self.fullscreen:
                    fallback_flags |= pygame.FULLSCREEN
                self.surface = pygame.display.set_mode((self.width, self.height), fallback_flags)
            except pygame.error:
                self.surface = pygame.display.set_mode((self.width, self.height))

        self.initialized = True
        return True

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)):
        """Fills the primary display surface with a solid color."""
        if self.surface:
            self.surface.fill(color)

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
        """Presents the frame by flipping the display buffer."""
        pygame.display.flip()

    def get_surface(self) -> pygame.Surface:
        """Returns the active display surface for seamless compatibility."""
        if self.surface is None:
            self.initialize()
        return self.surface

    def set_mode(self, width: int, height: int, fullscreen: bool = False) -> bool:
        """Reconfigures resolution and fullscreen state."""
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        return self.initialize()

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

    def cleanup(self):
        """Releases renderer resources."""
        self.surface = None
        self.initialized = False
