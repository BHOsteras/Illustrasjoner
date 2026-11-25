"""Felles stil og hjelpefunksjoner for manim-illustrasjoner.

Bruk i en scene:

    from manim import *
    from illustrasjoner import StyledScene, palette

    class MinScene(StyledScene):
        def construct(self):
            ...
"""

from illustrasjoner.style import (
    FONT,
    FONT_MONO,
    StyledScene,
    apply_style,
    palette,
    title,
)

__all__ = [
    "FONT",
    "FONT_MONO",
    "StyledScene",
    "apply_style",
    "palette",
    "title",
]
