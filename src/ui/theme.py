"""
Potaria - Centralized Typography & UI Theme Engine
Provides cached loading and rendering of official game fonts:
1. PixelifySans-Regular.ttf  — dialogue, descriptions, tooltips, and general UI text.
2. PixelifySans-SemiBold.ttf — menu buttons, inventory labels, and item names.
3. PixelifySans-Bold.ttf     — headings, warnings, and important notifications.
4. Cinzel-Black.ttf          — logo and fantasy title branding.
5. Silkscreen-Regular.ttf    — compact HUD labels such as HP, MP, LV, FPS, time, and prompts.

Developer: Kurados
"""

import os
import pygame

# Relative font directory
FONTS_DIR = os.path.join("assets", "fonts")

# Semantic Font Key Constants
FONT_REGULAR = "regular"       # PixelifySans-Regular.ttf
FONT_SEMIBOLD = "semibold"     # PixelifySans-SemiBold.ttf
FONT_BOLD = "bold"             # PixelifySans-Bold.ttf
FONT_TITLE = "title"           # Cinzel-Black.ttf
FONT_COMPACT = "compact"       # Silkscreen-Regular.ttf

FONT_FILENAMES = {
    FONT_REGULAR: "PixelifySans-Regular.ttf",
    FONT_SEMIBOLD: "PixelifySans-SemiBold.ttf",
    FONT_BOLD: "PixelifySans-Bold.ttf",
    FONT_TITLE: "Cinzel-Black.ttf",
    FONT_COMPACT: "Silkscreen-Regular.ttf",
}

# Cache for pygame.font.Font objects: (font_key, size) -> Font
_FONT_CACHE = {}


def _get_font_file_path(font_key):
    filename = FONT_FILENAMES.get(font_key, "PixelifySans-Regular.ttf")
    # Check relative to working directory
    candidates = [
        os.path.join(FONTS_DIR, filename),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "fonts", filename),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def get_font(font_key=FONT_REGULAR, size=14):
    """
    Retrieves a cached pygame.font.Font instance for the specified font key and size.
    Falls back gracefully to pygame.font.SysFont if file is unavailable.
    """
    if not pygame.font.get_init():
        pygame.font.init()

    cache_key = (font_key, int(size))
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    font_path = _get_font_file_path(font_key)
    font_obj = None

    if font_path and os.path.isfile(font_path):
        try:
            font_obj = pygame.font.Font(font_path, int(size))
        except Exception as e:
            font_obj = None

    if font_obj is None:
        # Fallback to system font
        if font_key == FONT_TITLE:
            font_obj = pygame.font.SysFont("Georgia", int(size), bold=True)
        elif font_key in (FONT_BOLD, FONT_SEMIBOLD):
            font_obj = pygame.font.SysFont("Arial", int(size), bold=True)
        elif font_key == FONT_COMPACT:
            font_obj = pygame.font.SysFont("Arial", max(9, int(size) - 2), bold=True)
        else:
            font_obj = pygame.font.SysFont("Arial", int(size))

    _FONT_CACHE[cache_key] = font_obj
    return font_obj


# Convenience accessors
def font_regular(size=14):
    return get_font(FONT_REGULAR, size)


def font_semibold(size=14):
    return get_font(FONT_SEMIBOLD, size)


def font_bold(size=16):
    return get_font(FONT_BOLD, size)


def font_title(size=28):
    return get_font(FONT_TITLE, size)


def font_compact(size=11):
    return get_font(FONT_COMPACT, size)


def clear_font_cache():
    """Clears the font cache."""
    _FONT_CACHE.clear()


def wrap_text_lines(text, font, max_width):
    """
    Wraps a string into a list of lines so none exceeds max_width pixels.
    Supports multiline blocks, bullet points, and preserves natural spacing.
    """
    if not text:
        return []
    
    result = []
    for block in str(text).split("\n"):
        block = block.strip()
        if not block:
            continue
        words = block.split(" ")
        current_line = []
        for word in words:
            if not word:
                continue
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    result.append(" ".join(current_line))
                    current_line = [word]
                else:
                    result.append(word)
                    current_line = []
        if current_line:
            result.append(" ".join(current_line))
    return result if result else [str(text)]
