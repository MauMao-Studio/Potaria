"""
Potaria - Renderer Hardware Abstraction Layer (HAL)
RendererManager Factory & Central Controller
Developer: Kurados
Engine: Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)
"""

from typing import Optional, Tuple, Union
import pygame

from src.rendering.base_renderer import (
    BaseRenderer,
    RENDERER_HARDWARE,
    RENDERER_SOFTWARE,
)
from src.rendering.surface_renderer import SurfaceRenderer
from src.rendering.gl_renderer import GLRenderer


class RendererManager:
    """
    Central manager for Potaria's graphics backends.
    Allows runtime switching between Hardware (ModernGL) and Compatibility (Software)
    renderers, and provides transparent delegating calls.
    """

    _instance: Optional["RendererManager"] = None

    @classmethod
    def get_instance(cls) -> "RendererManager":
        """Returns the singleton instance of RendererManager."""
        if cls._instance is None:
            cls._instance = RendererManager()
        return cls._instance

    def __init__(self):
        self.width = 1280
        self.height = 720
        self.title = "Potaria"
        self.fullscreen = False
        self.requested_type = RENDERER_HARDWARE
        self.active_renderer: Optional[BaseRenderer] = None

    def initialize(
        self,
        width: int = 1280,
        height: int = 720,
        title: str = "Potaria",
        fullscreen: bool = False,
        requested_type: str = RENDERER_HARDWARE,
    ) -> BaseRenderer:
        """Initializes the active renderer according to requested type."""
        self.width = width
        self.height = height
        self.title = title
        self.fullscreen = fullscreen
        req = str(requested_type or "").lower().strip()
        self.requested_type = RENDERER_SOFTWARE if req == RENDERER_SOFTWARE else RENDERER_HARDWARE

        if self.active_renderer:
            self.active_renderer.cleanup()

        if self.requested_type == RENDERER_SOFTWARE:
            self.active_renderer = SurfaceRenderer(
                width=self.width,
                height=self.height,
                title=self.title,
                fullscreen=self.fullscreen,
            )
        else:
            self.active_renderer = GLRenderer(
                width=self.width,
                height=self.height,
                title=self.title,
                fullscreen=self.fullscreen,
            )

        self.active_renderer.initialize()
        return self.active_renderer

    def switch_renderer(
        self,
        new_type: str,
        fullscreen: Optional[bool] = None,
    ) -> BaseRenderer:
        """
        Switches the rendering backend to new_type ('hardware' or 'software')
        at runtime while preserving window and fullscreen settings.
        """
        fs = self.fullscreen if fullscreen is None else fullscreen
        cand = str(new_type or "").lower().strip()
        norm_type = RENDERER_SOFTWARE if cand == RENDERER_SOFTWARE else RENDERER_HARDWARE
        if norm_type == self.requested_type and self.active_renderer and self.active_renderer.initialized:
            if fullscreen is not None and fullscreen != self.fullscreen:
                self.fullscreen = fullscreen
                self.active_renderer.set_mode(self.width, self.height, fullscreen=self.fullscreen)
            return self.active_renderer

        return self.initialize(
            width=self.width,
            height=self.height,
            title=self.title,
            fullscreen=fs,
            requested_type=norm_type,
        )

    def toggle_renderer(self, fullscreen: Optional[bool] = None) -> BaseRenderer:
        """Toggles between Hardware and Software renderer."""
        next_type = (
            RENDERER_SOFTWARE
            if self.requested_type == RENDERER_HARDWARE
            else RENDERER_HARDWARE
        )
        return self.switch_renderer(next_type, fullscreen=fullscreen)

    @property
    def renderer(self) -> BaseRenderer:
        """Returns the active BaseRenderer instance."""
        if self.active_renderer is None:
            self.initialize(self.width, self.height, self.title, self.fullscreen, self.requested_type)
        return self.active_renderer

    @property
    def surface(self) -> pygame.Surface:
        """Returns the active pygame.Surface for rendering."""
        return self.renderer.get_surface()

    @property
    def is_hardware(self) -> bool:
        """Returns True if the active renderer is using GPU acceleration."""
        return self.renderer.is_hardware_accelerated()

    @property
    def using_fallback(self) -> bool:
        """Returns True if the active renderer is in fallback mode."""
        return getattr(self.renderer, "using_fallback", False)

    def get_status_label(self) -> str:
        """
        Returns the formatted label for the Video Settings button:
        'RENDERER: HARDWARE (MODERNGL)' or 'RENDERER: COMPATIBILITY (SOFTWARE)'.
        """
        if self.requested_type == RENDERER_HARDWARE:
            return "RENDERER: HARDWARE (MODERNGL)"
        return "RENDERER: COMPATIBILITY (SOFTWARE)"

    # Transparent delegation methods
    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)):
        self.renderer.clear(color)

    def present(self):
        self.renderer.present()

    def draw_sprite(
        self,
        surface: pygame.Surface,
        dest: Union[Tuple[int, int], pygame.Rect],
        area: Optional[pygame.Rect] = None,
        special_flags: int = 0,
    ):
        self.renderer.draw_sprite(surface, dest, area, special_flags)

    def draw_surface(
        self,
        surface: pygame.Surface,
        dest: Union[Tuple[int, int], pygame.Rect],
        area: Optional[pygame.Rect] = None,
        special_flags: int = 0,
    ):
        self.renderer.draw_surface(surface, dest, area, special_flags)

    def draw_rect(
        self,
        color: Union[Tuple[int, int, int], Tuple[int, int, int, int]],
        rect: Union[pygame.Rect, Tuple[int, int, int, int]],
        width: int = 0,
        border_radius: int = 0,
    ):
        self.renderer.draw_rect(color, rect, width, border_radius)

    def draw_text(
        self,
        font: pygame.font.Font,
        text: str,
        pos: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        antialias: bool = True,
    ) -> pygame.Rect:
        return self.renderer.draw_text(font, text, pos, color, antialias)

    def draw_line(
        self,
        color: Tuple[int, int, int],
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        width: int = 1,
    ):
        self.renderer.draw_line(color, start_pos, end_pos, width)

    def draw_circle(
        self,
        color: Tuple[int, int, int],
        center: Tuple[int, int],
        radius: float,
        width: int = 0,
    ):
        self.renderer.draw_circle(color, center, radius, width)

    def cleanup(self):
        if self.active_renderer:
            self.active_renderer.cleanup()
            self.active_renderer = None
