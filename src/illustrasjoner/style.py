"""Én kilde til sannhet for den visuelle stilen.

Endre farger, fonter og standardverdier her, så får alle illustrasjoner
samme uttrykk. Scener bør arve fra `StyledScene` i stedet for `Scene`.
"""

from __future__ import annotations

from dataclasses import dataclass

from manim import (
    UP,
    Circle,
    Dot,
    Line,
    MathTex,
    MovingCameraScene,
    Rectangle,
    Square,
    Tex,
    Text,
    VMobject,
    config,
)

FONT = "Noto Sans"
FONT_MONO = "Noto Sans Mono"


@dataclass(frozen=True)
class Palette:
    """Fargepalett. Bruk navnene (rollene), ikke hex-verdiene, i scenene."""

    background: str = "#0F172A"  # mørk blågrå
    text: str = "#E2E8F0"  # nesten hvit
    muted: str = "#94A3B8"  # sekundær tekst, akser, hjelpelinjer
    primary: str = "#38BDF8"  # hovedaksent (blå)
    secondary: str = "#F472B6"  # andre aksent (rosa)
    tertiary: str = "#A3E635"  # tredje aksent (grønn)
    warning: str = "#FBBF24"  # fremheving / advarsel (gul)
    danger: str = "#F87171"  # feil / negativt (rød)

    @property
    def accents(self) -> list[str]:
        """Aksentfarger i fast rekkefølge, nyttig for serier/kategorier."""
        return [self.primary, self.secondary, self.tertiary, self.warning, self.danger]


palette = Palette()

STROKE_WIDTH = 4


def apply_style() -> None:
    """Sett globale manim-standarder slik at alle objekter følger stilen."""
    config.background_color = palette.background

    Text.set_default(font=FONT, color=palette.text)
    Tex.set_default(color=palette.text)
    MathTex.set_default(color=palette.text)

    for shape in (Circle, Square, Rectangle, Line):
        shape.set_default(color=palette.primary, stroke_width=STROKE_WIDTH)
    Dot.set_default(color=palette.text)


def title(text: str, **kwargs) -> VMobject:
    """Standard tittel øverst i bildet."""
    return Text(text, font_size=48, weight="BOLD", **kwargs).to_edge(UP, buff=0.5)


class StyledScene(MovingCameraScene):
    """Basisklasse for alle scener i prosjektet.

    Arver fra MovingCameraScene slik at kamerazoom/panorering er tilgjengelig.
    """

    def setup(self) -> None:
        apply_style()
        self.camera.background_color = palette.background
        super().setup()
