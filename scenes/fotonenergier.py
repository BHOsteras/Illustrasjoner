"""Tre fotoner (30, 70 og 120 keV) som går side om side fra venstre til høyre.

Bølgelengdene er λ = hc/E, tegnet i samme skala, så frekvensene står i
forholdet 30 : 70 : 120. Alle går med samme fart (lysfarten), og pakkene har
samme omhylling og amplitude, slik at bare frekvensen skiller dem.

Render:
    uv run manim -pqh scenes/fotonenergier.py FotonEnergier
"""

from __future__ import annotations

from manim import *

from illustrasjoner import StyledScene
from illustrasjoner.physics import (
    PHOTON_SPEED,
    moving_photon,
    photon_axis,
    photon_travel_range,
    photon_wavelength_pm,
)

ENERGIES_KEV = (30, 70, 120)  # øverst til nederst
ROW_SPACING = 2.3
AMPLITUDE = 0.75
SIGMA = 1.4

# Felles skala: 30 keV (λ ≈ 41 pm) tegnes med bølgelengde 1.6 enheter
UNITS_PER_PM = 1.6 / photon_wavelength_pm(ENERGIES_KEV[0])


class FotonEnergier(StyledScene):
    def construct(self) -> None:
        start, end = photon_travel_range(SIGMA)
        run_time = (end - start) / PHOTON_SPEED
        t = ValueTracker(0)

        for i, energy in enumerate(ENERGIES_KEV):
            origin = UP * ROW_SPACING * (1 - i)
            wavelength = photon_wavelength_pm(energy) * UNITS_PER_PM

            photon = moving_photon(
                lambda: start + PHOTON_SPEED * t.get_value(),
                wavelength=wavelength,
                sigma=SIGMA,
                amplitude=AMPLITUDE,
                origin=origin,
            )
            self.add(photon_axis(start, end, origin), photon)

        self.play(t.animate.set_value(run_time), run_time=run_time, rate_func=linear)
