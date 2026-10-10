"""
Potaria - Rendering Package (Hardware Abstraction Layer)
Developer: Kurados
Engine: Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)
"""

from src.rendering.base_renderer import (
    BaseRenderer,
    RENDERER_HARDWARE,
    RENDERER_SOFTWARE,
)
from src.rendering.surface_renderer import SurfaceRenderer
from src.rendering.gl_renderer import GLRenderer
from src.rendering.renderer_manager import RendererManager


def get_renderer_manager() -> RendererManager:
    """Returns the singleton RendererManager instance."""
    return RendererManager.get_instance()


def create_renderer(
    renderer_type: str = RENDERER_HARDWARE,
    width: int = 1280,
    height: int = 720,
    title: str = "Potaria",
    fullscreen: bool = False,
) -> BaseRenderer:
    """Factory function to instantiate a specific renderer directly."""
    if renderer_type.lower().strip() == RENDERER_SOFTWARE:
        renderer = SurfaceRenderer(width=width, height=height, title=title, fullscreen=fullscreen)
    else:
        renderer = GLRenderer(width=width, height=height, title=title, fullscreen=fullscreen)
    renderer.initialize()
    return renderer


__all__ = [
    "BaseRenderer",
    "SurfaceRenderer",
    "GLRenderer",
    "RendererManager",
    "RENDERER_HARDWARE",
    "RENDERER_SOFTWARE",
    "get_renderer_manager",
    "create_renderer",
]
