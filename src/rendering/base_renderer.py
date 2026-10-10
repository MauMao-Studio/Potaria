"""
Potaria - Renderer Hardware Abstraction Layer (HAL)
BaseRenderer Interface
Developer: Kurados
Engine: Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union
import pygame

RENDERER_HARDWARE = "hardware"
RENDERER_SOFTWARE = "software"


class BaseRenderer(ABC):
    """
    Abstract Base Class for Potaria's Hardware Abstraction Layer.
    Decouples core simulation authority and game loops from rendering backends.
    """

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        title: str = "Potaria",
        fullscreen: bool = False,
    ):
        self.width = width
        self.height = height
        self.title = title
        self.fullscreen = fullscreen
        self.initialized = False

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initializes the rendering context / display window.
        Returns True on success, False otherwise.
        """
        pass

    @abstractmethod
    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)):
        """Clears the screen or backbuffer with the specified color."""
        pass

    @abstractmethod
    def draw_sprite(
        self,
        surface: pygame.Surface,
        dest: Union[Tuple[int, int], pygame.Rect],
        area: Optional[pygame.Rect] = None,
        special_flags: int = 0,
    ):
        """Draws a sprite or sub-rectangle of a surface onto the target buffer."""
        pass

    @abstractmethod
    def draw_surface(
        self,
        surface: pygame.Surface,
        dest: Union[Tuple[int, int], pygame.Rect],
        area: Optional[pygame.Rect] = None,
        special_flags: int = 0,
    ):
        """Draws a pygame Surface onto the target buffer."""
        pass

    @abstractmethod
    def draw_rect(
        self,
        color: Union[Tuple[int, int, int], Tuple[int, int, int, int]],
        rect: Union[pygame.Rect, Tuple[int, int, int, int]],
        width: int = 0,
        border_radius: int = 0,
    ):
        """Draws a rectangle with optional border outline and rounded corners."""
        pass

    @abstractmethod
    def draw_text(
        self,
        font: pygame.font.Font,
        text: str,
        pos: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        antialias: bool = True,
    ) -> pygame.Rect:
        """Renders and draws text at the target position, returning the bounding rect."""
        pass

    @abstractmethod
    def draw_line(
        self,
        color: Tuple[int, int, int],
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        width: int = 1,
    ):
        """Draws a line between two points."""
        pass

    @abstractmethod
    def draw_circle(
        self,
        color: Tuple[int, int, int],
        center: Tuple[int, int],
        radius: float,
        width: int = 0,
    ):
        """Draws a circle at the given center coordinates."""
        pass

    @abstractmethod
    def present(self):
        """Presents the rendered frame to the display window (flips backbuffer)."""
        pass

    @abstractmethod
    def get_surface(self) -> pygame.Surface:
        """
        Returns the native pygame.Surface target for direct blitting.
        Provides 100% backward compatibility for legacy rendering systems.
        """
        pass

    @abstractmethod
    def set_mode(self, width: int, height: int, fullscreen: bool = False) -> bool:
        """Reconfigures resolution and fullscreen state."""
        pass

    @abstractmethod
    def is_hardware_accelerated(self) -> bool:
        """Returns True if the backend is actively using hardware GPU acceleration."""
        pass

    @abstractmethod
    def get_renderer_type(self) -> str:
        """Returns 'hardware' or 'software'."""
        pass

    @abstractmethod
    def draw_projectiles_batch(
        self,
        projectiles: list,
        camera: Optional[any] = None,
    ) -> int:
        """
        Renders a high-density batch of projectiles in an optimized pass.
        Returns the count of rendered projectiles.
        """
        pass

    def set_bloom_enabled(self, enabled: bool):
        """Configures GLSL bloom post-processing state."""
        pass

    def set_bloom_intensity(self, intensity: float):
        """Sets bloom post-processing aura intensity."""
        pass

    def set_bloom_threshold(self, threshold: float):
        """Sets bloom luminance extraction threshold."""
        pass

    def get_bloom_params(self) -> dict:
        """Returns active bloom parameters."""
        return {"enabled": False, "intensity": 0.0, "threshold": 0.65}

    @abstractmethod
    def cleanup(self):
        """Releases all graphics and windowing resources cleanly."""
        pass
