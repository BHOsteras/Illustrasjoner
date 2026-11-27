"""Ett foton som bølgepakke som går fra venstre til høyre (standard fotonstil).

Render:
    uv run manim -pqh scenes/foton.py Foton
"""

from __future__ import annotations

from manim import *

from illustrasjoner import StyledScene
from illustrasjoner.physics import (
    PHOTON_SPEED,
    moving_photon,
    photon_axis,
    photon_travel_range,
)

WAVELENGTH = 0.9


class Foton(StyledScene):
    def construct(self) -> None:
        start, end = photon_travel_range()
        run_time = (end - start) / PHOTON_SPEED

        t = ValueTracker(0)
        photon = moving_photon(lambda: start + PHOTON_SPEED * t.get_value(), wavelength=WAVELENGTH)

        self.add(photon_axis(start, end), photon)
        self.play(t.animate.set_value(run_time), run_time=run_time, rate_func=linear)
