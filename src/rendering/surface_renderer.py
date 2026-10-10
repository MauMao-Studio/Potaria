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

    def cleanup(self):
        """Releases renderer resources."""
        self.surface = None
        self.initialized = False
