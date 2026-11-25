"""Test av LaTeX (MathTex/Tex) med den felles stilen.

Render:
    uv run manim -pqh scenes/latex_demo.py LatexDemo
"""

from manim import *

from illustrasjoner import StyledScene, palette, title


class LatexDemo(StyledScene):
    def construct(self) -> None:
        heading = title("Pytagoras' setning")

        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=96)
        formula[0].set_color(palette.primary)
        formula[2].set_color(palette.secondary)
        formula[4].set_color(palette.tertiary)

        explanation = Tex(
            r"Gjelder for alle rettvinklede trekanter --- æøå fungerer også.",
            font_size=36,
            color=palette.muted,
        ).next_to(formula, DOWN, buff=0.8)

        self.play(Write(heading))
        self.play(Write(formula))
        self.play(FadeIn(explanation, shift=UP * 0.2))
        self.play(Circumscribe(formula, color=palette.warning))
        self.wait()
