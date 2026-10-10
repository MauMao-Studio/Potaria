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


_logged_fallback_global: bool = False

class GLRenderer(BaseRenderer):
    """
    Hardware-accelerated OpenGL / ModernGL Renderer with automatic safety fallback.
    If ModernGL or GPU context creation is unavailable, it gracefully delegates
    100% of operations to SurfaceRenderer with zero crashes or pipeline stalls.
    """

    VERTEX_SHADER: str = """
    #version 330 core
    in vec2 in_vert;
    in vec2 in_text;
    out vec2 v_text;
    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
        v_text = in_text;
    }
    """

    FRAGMENT_SHADER: str = """
    #version 330 core
    uniform sampler2D u_texture;
    uniform vec2 u_resolution;
    uniform float u_time;

    uniform int u_shaders_enabled;
    uniform int u_bloom_enabled;
    uniform float u_bloom_intensity;
    uniform float u_bloom_threshold;

    uniform int u_vignette_enabled;
    uniform float u_vignette_intensity;

    uniform int u_water_distortion_enabled;
    uniform float u_water_distortion_intensity;

    uniform int u_color_grading_mode;
    uniform float u_saturation;
    uniform float u_contrast;

    in vec2 v_text;
    out vec4 f_color;

    float luminance(vec3 color) {
        return dot(color, vec3(0.2126, 0.7152, 0.0722));
    }

    vec3 adjust_saturation(vec3 color, float sat) {
        float l = luminance(color);
        return mix(vec3(l), color, sat);
    }

    vec3 adjust_contrast(vec3 color, float cont) {
        return (color - 0.5) * cont + 0.5;
    }

    void main() {
        vec2 uv = v_text;
        if (u_shaders_enabled == 1 && u_water_distortion_enabled == 1) {
            float wave_x = sin(v_text.y * 50.0 + u_time * 3.0) * 0.0016 * u_water_distortion_intensity;
            float wave_y = cos(v_text.x * 40.0 + u_time * 2.5) * 0.0012 * u_water_distortion_intensity;
            uv += vec2(wave_x, wave_y);
        }

        vec4 base_color = texture(u_texture, uv);

        if (u_shaders_enabled == 0) {
            f_color = base_color;
            return;
        }

        vec3 rgb = base_color.rgb;

        // Bloom extraction and multi-sample accumulation
        if (u_bloom_enabled == 1 && u_bloom_intensity > 0.0) {
            vec2 texel = 1.0 / u_resolution;
            vec3 bloom_acc = vec3(0.0);
            float total_weight = 0.0;

            for (int x = -3; x <= 3; x++) {
                for (int y = -3; y <= 3; y++) {
                    float dist = length(vec2(float(x), float(y)));
                    if (dist > 3.5) continue;
                    float weight = exp(-0.5 * (dist * dist) / 3.0);
                    vec2 offset = vec2(float(x), float(y)) * texel * 1.6;
                    vec4 s = texture(u_texture, uv + offset);
                    float luma = luminance(s.rgb);
                    if (luma > u_bloom_threshold) {
                        bloom_acc += s.rgb * weight * (luma - u_bloom_threshold);
                    }
                    total_weight += weight;
                }
            }

            if (total_weight > 0.0) {
                bloom_acc /= total_weight;
            }

            float pulse = 1.0 + 0.06 * sin(u_time * 3.0);
            rgb += bloom_acc * u_bloom_intensity * 2.5 * pulse;
        }

        // Color Grading Modes
        // 0: Standard, 1: Vibrant, 2: Cinematic Warm, 3: Cool / Spectral
        if (u_color_grading_mode == 1) {
            rgb = adjust_saturation(rgb, u_saturation > 0.0 ? u_saturation : 1.18);
            rgb = adjust_contrast(rgb, u_contrast > 0.0 ? u_contrast : 1.08);
        } else if (u_color_grading_mode == 2) {
            rgb.r *= 1.06;
            rgb.g *= 1.02;
            rgb.b *= 0.94;
            rgb = adjust_contrast(rgb, 1.10);
        } else if (u_color_grading_mode == 3) {
            rgb.r *= 0.92;
            rgb.g *= 1.04;
            rgb.b *= 1.12;
            rgb = adjust_contrast(rgb, 1.06);
        }

        // Vignette & Ambiance
        if (u_vignette_enabled == 1 && u_vignette_intensity > 0.0) {
            vec2 coord = (v_text - 0.5) * vec2(u_resolution.x / u_resolution.y, 1.0);
            float d = length(coord);
            float vig = smoothstep(0.85, 0.25, d * (0.8 + u_vignette_intensity * 0.5));
            rgb *= mix(1.0, vig, u_vignette_intensity);
        }

        rgb = clamp(rgb, 0.0, 1.0);
        f_color = vec4(rgb, base_color.a);
    }
    """

    @classmethod
    def reset_fallback_log(cls):
        """Resets the fallback warning logged state (primarily for automated unit tests)."""
        global _logged_fallback_global
        _logged_fallback_global = False

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

        # Graphics and Post-Processing Settings
        self.shaders_enabled: bool = True
        self.bloom_enabled: bool = True
        self.bloom_intensity: float = 0.8
        self.bloom_threshold: float = 0.65
        self.vignette_enabled: bool = True
        self.vignette_intensity: float = 0.35
        self.water_distortion_enabled: bool = True
        self.water_distortion_intensity: float = 1.0
        self.color_grading_mode: int = 1
        self.saturation: float = 1.18
        self.contrast: float = 1.08
        self.lighting_quality: str = "high"
        self.particle_density: str = "high"
        self.time: float = 0.0
        self.last_batch_count: int = 0
        self.total_batched_projectiles: int = 0

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
        global _logged_fallback_global
        if not _logged_fallback_global:
            print(f"[GLRenderer] {reason}. Gracefully falling back to native SurfaceRenderer.")
            _logged_fallback_global = True
        self.fallback_renderer = SurfaceRenderer(
            width=self.width,
            height=self.height,
            title=self.title,
            fullscreen=self.fullscreen,
        )
        self.fallback_renderer.initialize()
        if hasattr(self.fallback_renderer, "set_bloom_enabled"):
            self.fallback_renderer.set_bloom_enabled(self.bloom_enabled)
            self.fallback_renderer.set_bloom_intensity(self.bloom_intensity)
            self.fallback_renderer.set_bloom_threshold(self.bloom_threshold)
            self.fallback_renderer.set_shaders_enabled(self.shaders_enabled)
            self.fallback_renderer.set_vignette_enabled(self.vignette_enabled)
            self.fallback_renderer.set_vignette_intensity(self.vignette_intensity)
            self.fallback_renderer.set_water_distortion_enabled(self.water_distortion_enabled)
            self.fallback_renderer.set_water_distortion_intensity(self.water_distortion_intensity)
            self.fallback_renderer.set_color_grading_mode(self.color_grading_mode)
            self.fallback_renderer.set_saturation(self.saturation)
            self.fallback_renderer.set_contrast(self.contrast)
            self.fallback_renderer.set_lighting_quality(self.lighting_quality)
            self.fallback_renderer.set_particle_density(self.particle_density)
        self.initialized = True

    def _init_gl_pipeline(self):
        """Sets up the ModernGL full-screen quad shader and virtual surface backbuffer."""
        self.virtual_surface = pygame.Surface((self.width, self.height)).convert_alpha()

        self.program = self.ctx.program(
            vertex_shader=self.VERTEX_SHADER,
            fragment_shader=self.FRAGMENT_SHADER,
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

        self._update_shader_uniforms()

        if hasattr(self.ctx, "viewport"):
            try:
                self.ctx.viewport = (0, 0, self.width, self.height)
            except Exception:
                pass

    def _update_shader_uniforms(self):
        """Updates active shader uniforms for bloom, vignette, water distortion, color grading, resolution, and time."""
        if not self.program:
            return
        uniform_map = {
            "u_texture": 0,
            "u_resolution": (float(self.width), float(self.height)),
            "u_time": float(self.time),
            "u_shaders_enabled": 1 if self.shaders_enabled else 0,
            "u_bloom_enabled": 1 if self.bloom_enabled else 0,
            "u_bloom_intensity": float(self.bloom_intensity),
            "u_bloom_threshold": float(self.bloom_threshold),
            "u_vignette_enabled": 1 if self.vignette_enabled else 0,
            "u_vignette_intensity": float(self.vignette_intensity),
            "u_water_distortion_enabled": 1 if self.water_distortion_enabled else 0,
            "u_water_distortion_intensity": float(self.water_distortion_intensity),
            "u_color_grading_mode": int(self.color_grading_mode),
            "u_saturation": float(self.saturation),
            "u_contrast": float(self.contrast),
        }
        for name, val in uniform_map.items():
            try:
                if name in self.program:
                    self.program[name].value = val
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
            self.time += 0.016
            self.screen_texture.write(pygame.image.tobytes(self.virtual_surface, "RGBA"))
            self.screen_texture.use(location=0)
            self._update_shader_uniforms()
            self.vao.render(moderngl.TRIANGLE_STRIP)
            pygame.display.flip()

    def draw_projectiles_batch(
        self,
        projectiles: list,
        camera: Optional[any] = None,
    ) -> int:
        """
        Renders a high-density batch of projectiles in an optimized pass.
        Returns the count of successfully rendered projectiles.
        """
        if self._using_fallback and self.fallback_renderer:
            return self.fallback_renderer.draw_projectiles_batch(projectiles, camera)

        if not self.virtual_surface or not projectiles:
            return 0

        target_surf = self.virtual_surface
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
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_bloom_enabled"):
                self.fallback_renderer.set_bloom_enabled(enabled)
        else:
            self._update_shader_uniforms()

    def set_bloom_intensity(self, intensity: float):
        self.bloom_intensity = max(0.0, min(5.0, float(intensity)))
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_bloom_intensity"):
                self.fallback_renderer.set_bloom_intensity(intensity)
        else:
            self._update_shader_uniforms()

    def set_bloom_threshold(self, threshold: float):
        self.bloom_threshold = max(0.0, min(1.0, float(threshold)))
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_bloom_threshold"):
                self.fallback_renderer.set_bloom_threshold(threshold)
        else:
            self._update_shader_uniforms()

    def get_bloom_params(self) -> dict:
        return {
            "enabled": self.bloom_enabled,
            "intensity": self.bloom_intensity,
            "threshold": self.bloom_threshold,
        }

    def set_shaders_enabled(self, enabled: bool):
        self.shaders_enabled = bool(enabled)
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_shaders_enabled"):
                self.fallback_renderer.set_shaders_enabled(enabled)
        else:
            self._update_shader_uniforms()

    def is_shaders_enabled(self) -> bool:
        return self.shaders_enabled

    def set_vignette_enabled(self, enabled: bool):
        self.vignette_enabled = bool(enabled)
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_vignette_enabled"):
                self.fallback_renderer.set_vignette_enabled(enabled)
        else:
            self._update_shader_uniforms()

    def set_vignette_intensity(self, intensity: float):
        self.vignette_intensity = max(0.0, min(1.0, float(intensity)))
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_vignette_intensity"):
                self.fallback_renderer.set_vignette_intensity(intensity)
        else:
            self._update_shader_uniforms()

    def set_water_distortion_enabled(self, enabled: bool):
        self.water_distortion_enabled = bool(enabled)
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_water_distortion_enabled"):
                self.fallback_renderer.set_water_distortion_enabled(enabled)
        else:
            self._update_shader_uniforms()

    def set_water_distortion_intensity(self, intensity: float):
        self.water_distortion_intensity = max(0.0, min(3.0, float(intensity)))
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_water_distortion_intensity"):
                self.fallback_renderer.set_water_distortion_intensity(intensity)
        else:
            self._update_shader_uniforms()

    def set_color_grading_mode(self, mode: Union[int, str]):
        if isinstance(mode, str):
            mapping = {"standard": 0, "vibrant": 1, "cinematic": 2, "cool": 3}
            self.color_grading_mode = mapping.get(mode.lower().strip(), 0)
        else:
            self.color_grading_mode = int(mode)
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_color_grading_mode"):
                self.fallback_renderer.set_color_grading_mode(self.color_grading_mode)
        else:
            self._update_shader_uniforms()

    def set_saturation(self, saturation: float):
        self.saturation = max(0.0, min(2.5, float(saturation)))
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_saturation"):
                self.fallback_renderer.set_saturation(saturation)
        else:
            self._update_shader_uniforms()

    def set_contrast(self, contrast: float):
        self.contrast = max(0.0, min(2.5, float(contrast)))
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_contrast"):
                self.fallback_renderer.set_contrast(contrast)
        else:
            self._update_shader_uniforms()

    def set_lighting_quality(self, quality: str):
        self.lighting_quality = str(quality).lower().strip()
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_lighting_quality"):
                self.fallback_renderer.set_lighting_quality(quality)

    def set_particle_density(self, density: str):
        self.particle_density = str(density).lower().strip()
        if self._using_fallback and self.fallback_renderer:
            if hasattr(self.fallback_renderer, "set_particle_density"):
                self.fallback_renderer.set_particle_density(density)

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
        self.time = 0.0
        self.last_batch_count = 0
        self.initialized = False
