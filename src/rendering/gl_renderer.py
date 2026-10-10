"""
Potaria - Renderer Hardware Abstraction Layer (HAL)
GLRenderer Implementation (ModernGL / OpenGL Hardware Acceleration with Safe Fallback)
Developer: Kurados
Engine: Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)
"""

from typing import Optional, Tuple, Union, Dict
import array
import pygame

from src.rendering.base_renderer import (
    BaseRenderer,
    RENDERER_HARDWARE,
    RENDERER_SOFTWARE,
)
from src.rendering.surface_renderer import SurfaceRenderer

try:
    import moderngl
    MODERNGL_AVAILABLE = True
except ImportError:
    moderngl = None
    MODERNGL_AVAILABLE = False


class GLRenderer(BaseRenderer):
    """
    Hardware-accelerated OpenGL / ModernGL Renderer with automatic safety fallback.
    If ModernGL or GPU context creation is unavailable, it gracefully delegates
    100% of operations to SurfaceRenderer with zero crashes or pipeline stalls.
    """

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        title: str = "Potaria",
        fullscreen: bool = False,
    ):
        super().__init__(width=width, height=height, title=title, fullscreen=fullscreen)
        self.fallback_renderer: Optional[SurfaceRenderer] = None
        self._using_fallback = False
        self.fallback_reason = ""

        # ModernGL resources
        self.ctx = None
        self.virtual_surface: Optional[pygame.Surface] = None
        self.screen_texture = None
        self.program = None
        self.vbo = None
        self.vao = None
        self.texture_cache: Dict[int, any] = {}

    @property
    def using_fallback(self) -> bool:
        """Indicates whether this GLRenderer has fallen back to software blitting."""
        return self._using_fallback

    def initialize(self) -> bool:
        """
        Attempts to initialize a ModernGL hardware context.
        If any step fails, seamlessly falls back to SurfaceRenderer.
        """
        if self.initialized or self.ctx or self.fallback_renderer:
            self.cleanup()

        if not pygame.get_init():
            pygame.init()

        if not MODERNGL_AVAILABLE:
            self._engage_fallback("ModernGL library is not installed in the Python environment")
            return True

        if self.title:
            pygame.display.set_caption(self.title)

        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN

        try:
            pygame.display.set_mode((self.width, self.height), flags)
            self.ctx = moderngl.create_context()
        except Exception as e:
            self._engage_fallback(f"OpenGL context creation failed: {e}")
            return True

        try:
            self._init_gl_pipeline()
            self._using_fallback = False
            self.initialized = True
            print(f"[GLRenderer] Hardware acceleration initialized successfully via {self.ctx.info.get('GL_RENDERER', 'OpenGL')}.")
            return True
        except Exception as e:
            self._engage_fallback(f"ModernGL pipeline setup failed: {e}")
            return True

    def _cleanup_gl_resources(self):
        """Safely releases ModernGL textures, buffers, arrays, programs, and contexts."""
        if self.screen_texture:
            try:
                self.screen_texture.release()
            except Exception:
                pass
            self.screen_texture = None

        if self.vbo:
            try:
                self.vbo.release()
            except Exception:
                pass
            self.vbo = None

        if self.vao:
            try:
                self.vao.release()
            except Exception:
                pass
            self.vao = None

        if self.program:
            try:
                self.program.release()
            except Exception:
                pass
            self.program = None

        if self.ctx:
            try:
                self.ctx.release()
            except Exception:
                pass
            self.ctx = None

        self.texture_cache.clear()
        self.virtual_surface = None

    def _engage_fallback(self, reason: str):
        """Activates graceful fallback to SurfaceRenderer."""
        self._cleanup_gl_resources()
        self._using_fallback = True
        self.fallback_reason = reason
        print(f"[GLRenderer] {reason}. Gracefully falling back to native SurfaceRenderer.")
        self.fallback_renderer = SurfaceRenderer(
            width=self.width,
            height=self.height,
            title=self.title,
            fullscreen=self.fullscreen,
        )
        self.fallback_renderer.initialize()
        self.initialized = True

    def _init_gl_pipeline(self):
        """Sets up the ModernGL full-screen quad shader and virtual surface backbuffer."""
        self.virtual_surface = pygame.Surface((self.width, self.height)).convert_alpha()

        # Vertex shader: converts normalized coordinates [-1, 1] and texture coordinates [0, 1]
        vertex_shader = """
        #version 330 core
        in vec2 in_vert;
        in vec2 in_text;
        out vec2 v_text;
        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
            v_text = in_text;
        }
        """

        # Fragment shader: samples the backbuffer texture
        fragment_shader = """
        #version 330 core
        uniform sampler2D u_texture;
        in vec2 v_text;
        out vec4 f_color;
        void main() {
            f_color = texture(u_texture, v_text);
        }
        """

        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )

        # Fullscreen quad vertices: (x, y, u, v)
        quad_data = array.array("f", [
            -1.0,  1.0, 0.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
             1.0,  1.0, 1.0, 0.0,
             1.0, -1.0, 1.0, 1.0,
        ])

        self.vbo = self.ctx.buffer(quad_data)
        self.vao = self.ctx.simple_vertex_array(
            self.program,
            self.vbo,
            "in_vert",
            "in_text",
        )

        self.screen_texture = self.ctx.texture(
            (self.width, self.height),
            4,
            pygame.image.tobytes(self.virtual_surface, "RGBA"),
        )
        self.screen_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        if "u_texture" in self.program:
            try:
                self.program["u_texture"].value = 0
            except Exception:
                pass

        if hasattr(self.ctx, "viewport"):
            try:
                self.ctx.viewport = (0, 0, self.width, self.height)
            except Exception:
                pass

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)):
        if self._using_fallback and self.fallback_renderer:
            self.fallback_renderer.clear(color)
            return

        if self.virtual_surface:
            self.virtual_surface.fill(color)
        if self.ctx:
            r = color[0] / 255.0
            g = color[1] / 255.0
            b = color[2] / 255.0
            self.ctx.clear(r, g, b, 1.0)

    def draw_sprite(
        self,
        surface: pygame.Surface,
        dest: Union[Tuple[int, int], pygame.Rect],
        area: Optional[pygame.Rect] = None,
        special_flags: int = 0,
    ):
        if self._using_fallback and self.fallback_renderer:
            self.fallback_renderer.draw_sprite(surface, dest, area, special_flags)
            return

        if self.virtual_surface:
            self.virtual_surface.blit(surface, dest, area, special_flags)

    def draw_surface(
        self,
        surface: pygame.Surface,
        dest: Union[Tuple[int, int], pygame.Rect],
        area: Optional[pygame.Rect] = None,
        special_flags: int = 0,
    ):
        if self._using_fallback and self.fallback_renderer:
            self.fallback_renderer.draw_surface(surface, dest, area, special_flags)
            return

        if self.virtual_surface:
            self.virtual_surface.blit(surface, dest, area, special_flags)

    def draw_rect(
        self,
        color: Union[Tuple[int, int, int], Tuple[int, int, int, int]],
        rect: Union[pygame.Rect, Tuple[int, int, int, int]],
        width: int = 0,
        border_radius: int = 0,
    ):
        if self._using_fallback and self.fallback_renderer:
            self.fallback_renderer.draw_rect(color, rect, width, border_radius)
            return

        if self.virtual_surface:
            pygame.draw.rect(self.virtual_surface, color, rect, width=width, border_radius=border_radius)

    def draw_text(
        self,
        font: pygame.font.Font,
        text: str,
        pos: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        antialias: bool = True,
    ) -> pygame.Rect:
        if self._using_fallback and self.fallback_renderer:
            return self.fallback_renderer.draw_text(font, text, pos, color, antialias)

        if self.virtual_surface:
            rendered = font.render(text, antialias, color)
            return self.virtual_surface.blit(rendered, pos)
        return pygame.Rect(pos[0], pos[1], 0, 0)

    def draw_line(
        self,
        color: Tuple[int, int, int],
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        width: int = 1,
    ):
        if self._using_fallback and self.fallback_renderer:
            self.fallback_renderer.draw_line(color, start_pos, end_pos, width)
            return

        if self.virtual_surface:
            pygame.draw.line(self.virtual_surface, color, start_pos, end_pos, width)

    def draw_circle(
        self,
        color: Tuple[int, int, int],
        center: Tuple[int, int],
        radius: float,
        width: int = 0,
    ):
        if self._using_fallback and self.fallback_renderer:
            self.fallback_renderer.draw_circle(color, center, radius, width)
            return

        if self.virtual_surface:
            pygame.draw.circle(self.virtual_surface, color, center, int(radius), width)

    def present(self):
        """Presents the frame via ModernGL quad or falls back to standard blit flip."""
        if self._using_fallback and self.fallback_renderer:
            self.fallback_renderer.present()
            return

        if self.ctx and self.screen_texture and self.virtual_surface and self.vao:
            self.screen_texture.write(pygame.image.tobytes(self.virtual_surface, "RGBA"))
            self.screen_texture.use(location=0)
            self.vao.render(moderngl.TRIANGLE_STRIP)
            pygame.display.flip()

    def get_surface(self) -> pygame.Surface:
        """Returns the target surface for backward compatibility."""
        if self._using_fallback and self.fallback_renderer:
            return self.fallback_renderer.get_surface()

        if self.virtual_surface is None:
            self.initialize()
        return self.virtual_surface if self.virtual_surface is not None else (
            self.fallback_renderer.get_surface() if self.fallback_renderer else pygame.Surface((self.width, self.height))
        )

    def set_mode(self, width: int, height: int, fullscreen: bool = False) -> bool:
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        if self._using_fallback and self.fallback_renderer:
            return self.fallback_renderer.set_mode(width, height, fullscreen)
        res = self.initialize()
        if self.ctx and hasattr(self.ctx, "viewport"):
            try:
                self.ctx.viewport = (0, 0, self.width, self.height)
            except Exception:
                pass
        return res

    def is_hardware_accelerated(self) -> bool:
        return not self._using_fallback

    def get_renderer_type(self) -> str:
        if self._using_fallback:
            return RENDERER_SOFTWARE
        return RENDERER_HARDWARE

    def get_status_description(self) -> str:
        """Returns human-readable renderer status."""
        if not self._using_fallback:
            return "Hardware (ModernGL)"
        if self.fallback_reason:
            return f"Compatibility (Software - Fallback: {self.fallback_reason})"
        return "Compatibility (Software)"

    def cleanup(self):
        if self.fallback_renderer:
            self.fallback_renderer.cleanup()
            self.fallback_renderer = None

        self._cleanup_gl_resources()
        self._using_fallback = False
        self.fallback_reason = ""
        self.initialized = False
