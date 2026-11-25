"""Enkel hello world som viser den felles stilen.

Render:
    uv run manim -pqh scenes/hello_world.py HelloWorld
"""

from manim import *

from illustrasjoner import StyledScene, palette, title


class HelloWorld(StyledScene):
    def construct(self) -> None:
        heading = title("Hello, world!")
        subtitle = Text("Illustrasjoner med manim", font_size=32, color=palette.muted)
        subtitle.next_to(heading, DOWN, buff=0.3)

        shapes = (
            VGroup(
                Circle(radius=0.8, color=palette.primary),
                Square(side_length=1.6, color=palette.secondary),
                Triangle(color=palette.tertiary).scale(0.9),
            )
            .arrange(RIGHT, buff=1.0)
            .shift(DOWN * 0.5)
        )

        self.play(Write(heading))
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.play(LaggedStart(*(Create(s) for s in shapes), lag_ratio=0.25))
        self.play(*(s.animate.set_fill(s.get_color(), opacity=0.35) for s in shapes))
        self.wait(0.5)
        # Roter hver figur om sitt eget sentrum (ikke gruppen som helhet)
        self.play(*(Rotate(s, PI / 2) for s in shapes), run_time=1.5)
        self.wait()
