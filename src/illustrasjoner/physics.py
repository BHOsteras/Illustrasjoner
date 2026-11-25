"""Gjenbrukbare byggeklosser for fysikk-illustrasjoner.

Inneholder faste farger for partikler (slik at et proton alltid ser likt ut
på tvers av illustrasjoner), kinematikk for vekselvirkninger og
tegnefunksjoner for atomkjerner og fotoner som bølgepakker.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import numpy as np
from manim import Dot, VGroup, VMobject

from illustrasjoner.style import palette

ELECTRON_REST_ENERGY_KEV = 510.99895

PROTON_COLOR = palette.danger
NEUTRON_COLOR = palette.muted
ELECTRON_COLOR = palette.primary
PHOTON_COLOR = palette.warning


# --------------------------------------------------------------------------- #
# Kinematikk
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ComptonResult:
    """Resultat av Compton-spredning mot et fritt elektron i ro."""

    incident_energy_kev: float  # E
    scattered_energy_kev: float  # E'
    electron_energy_kev: float  # T, kinetisk energi til rekylelektronet
    photon_angle: float  # θ, spredningsvinkel for fotonet (radianer)
    electron_angle: float  # φ, rekylvinkel for elektronet (radianer, motsatt side)

    @property
    def wavelength_ratio(self) -> float:
        """λ'/λ = E/E'."""
        return self.incident_energy_kev / self.scattered_energy_kev

    @property
    def electron_beta(self) -> float:
        """Rekylelektronets fart som andel av lysfarten, v/c."""
        gamma = 1 + self.electron_energy_kev / ELECTRON_REST_ENERGY_KEV
        return math.sqrt(1 - 1 / gamma**2)


def compton(energy_kev: float, theta: float) -> ComptonResult:
    """Compton-kinematikk for et foton med energi `energy_kev` spredt vinkel `theta`.

    E' = E / (1 + (E/mc²)(1 - cos θ))
    cot φ = (1 + E/mc²) tan(θ/2)
    """
    eps = energy_kev / ELECTRON_REST_ENERGY_KEV
    scattered = energy_kev / (1 + eps * (1 - math.cos(theta)))
    phi = math.atan2(1.0, (1 + eps) * math.tan(theta / 2))
    return ComptonResult(
        incident_energy_kev=energy_kev,
        scattered_energy_kev=scattered,
        electron_energy_kev=energy_kev - scattered,
        photon_angle=theta,
        electron_angle=phi,
    )


# --------------------------------------------------------------------------- #
# Tegning
# --------------------------------------------------------------------------- #


def nucleus(protons: int, neutrons: int, radius: float, seed: int = 1) -> VGroup:
    """Atomkjerne som en tettpakket klynge av protoner og nøytroner.

    Nukleonene tegnes uten omriss slik at kjernen ser riktig ut også når
    kameraet zoomer kraftig inn (strektykkelse skalerer med zoom).
    """
    n = protons + neutrons
    # Heksagonalt gitter, velg de n punktene nærmest sentrum
    lattice = [
        np.array([i + 0.5 * j, j * math.sqrt(3) / 2, 0.0])
        for i in range(-6, 7)
        for j in range(-6, 7)
    ]
    lattice.sort(key=lambda p: (round(float(np.linalg.norm(p)), 6), math.atan2(p[1], p[0])))
    points = lattice[:n]
    points_center = np.mean(points, axis=0)
    points = [p - points_center for p in points]
    extent = max(float(np.linalg.norm(p)) for p in points) + 0.5
    scale = radius / extent

    kinds = ["p"] * protons + ["n"] * neutrons
    random.Random(seed).shuffle(kinds)

    nucleons = VGroup()
    for p, kind in zip(points, kinds, strict=True):
        color = PROTON_COLOR if kind == "p" else NEUTRON_COLOR
        ball = Dot(p * scale, radius=0.5 * scale * 0.96, color=color)
        highlight = Dot(
            p * scale + np.array([-0.15, 0.15, 0]) * scale,
            radius=0.18 * scale,
            color="#FFFFFF",
            fill_opacity=0.35,
        )
        nucleons.add(VGroup(ball, highlight))
    return nucleons


def wave_packet(
    center: float,
    wavelength: float,
    sigma: float,
    amplitude: float = 0.25,
    s_min: float = -math.inf,
    s_max: float = math.inf,
    samples_per_wavelength: int = 40,
) -> VMobject:
    """Foton som en gaussisk bølgepakke langs x-aksen.

    `center` er pakkens sentrum langs aksen. Bare delen med s i
    [s_min, s_max] tegnes, slik at pakken kan "renne inn i" eller "ut av"
    et vekselvirkningspunkt. Roter/flytt resultatet for å plassere det.
    Bølgen forskyves stivt med pakken (ingen dispersjon i vakuum).
    """
    half = 2.5 * sigma
    lo = max(center - half, s_min)
    hi = min(center + half, s_max)
    curve = VMobject()
    if hi - lo < 1e-3:
        return curve
    n = max(2, int((hi - lo) / wavelength * samples_per_wavelength))
    s = np.linspace(lo, hi, n)
    u = s - center
    y = amplitude * np.exp(-((u / sigma) ** 2)) * np.sin(2 * math.pi * u / wavelength)
    curve.set_points_as_corners(np.column_stack([s, y, np.zeros_like(s)]))
    return curve
