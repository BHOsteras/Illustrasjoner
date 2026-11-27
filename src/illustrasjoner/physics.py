"""Gjenbrukbare byggeklosser for fysikk-illustrasjoner.

Inneholder faste farger for partikler (slik at et proton alltid ser likt ut
på tvers av illustrasjoner) og standardtegningen av fotoner som bølgepakker
med E- og B-felt (se AGENTS.md).

Fotoner tegnes i en fast ortografisk 3D-visning: x er forplantningsretningen,
E-feltet ligger langs y og B-feltet langs z. Bølgemønsteret står i ro langs x;
det er bare omhyllingskurven som vandrer (`photon_packet(center, ...)` med
økende `center`).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from manim import DEGREES, ORIGIN, Line, VGroup, VMobject, config

from illustrasjoner.style import palette

PROTON_COLOR = palette.danger
NEUTRON_COLOR = palette.muted
ELECTRON_COLOR = palette.primary
PHOTON_COLOR = palette.warning

HC_KEV_PM = 1239.84198  # h·c i keV·pm


def photon_wavelength_pm(energy_kev: float) -> float:
    """Bølgelengde i pikometer for et foton med gitt energi (λ = hc/E)."""
    return HC_KEV_PM / energy_kev


# --------------------------------------------------------------------------- #
# Fotonstil
# --------------------------------------------------------------------------- #

E_FIELD_COLOR = PHOTON_COLOR
B_FIELD_COLOR = palette.primary  # blå for B, som i vanlig lærebokkonvensjon
ENVELOPE_COLOR = PHOTON_COLOR
AXIS_COLOR = palette.muted

CURVE_WIDTH = 2.0
ENVELOPE_WIDTH = 1.0
ENVELOPE_OPACITY = 0.45
STEM_WIDTH = 0.75
STEM_OPACITY = 0.3
AXIS_WIDTH = 1.0
AXIS_OPACITY = 0.5

PHOTON_SIGMA = 1.2  # bredde på omhyllingskurven (standardavvik)
PHOTON_LENGTH_SIGMAS = 3.3  # pakken tegnes ±så mange sigma fra sentrum
PHOTON_SPEED = 2.0  # "lysfarten" i bildet, enheter per sekund

# Kamera: rotasjon om y (asimut) og deretter om x (høyde), ortografisk
CAMERA_AZIMUTH = -25 * DEGREES
CAMERA_ELEVATION = 20 * DEGREES


def view_matrix(azimuth: float = CAMERA_AZIMUTH, elevation: float = CAMERA_ELEVATION) -> np.ndarray:
    a, e = azimuth, elevation
    ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return rx @ ry


VIEW = view_matrix()


def project(x: np.ndarray, y: np.ndarray, z: np.ndarray, origin: np.ndarray = ORIGIN) -> np.ndarray:
    """3D-punkter (x = forplantning, y = E-retning, z = B-retning) til bildeplanet.

    `origin` er en forskyvning i bildeplanet, f.eks. for å stable flere fotoner.
    """
    pts = np.column_stack([x, y, z]) @ VIEW.T
    pts[:, 2] = 0
    return pts + np.asarray(origin)


def _polyline(points: np.ndarray, color: str, width: float, opacity: float = 1.0) -> VMobject:
    curve = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    curve.set_points_as_corners(points)
    return curve


def photon_travel_range(sigma: float = PHOTON_SIGMA) -> tuple[float, float]:
    """Start- og slutt-x for pakkesentrum, slik at pakken starter og slutter utenfor bildet."""
    x_half = config.frame_width / 2 / VIEW[0, 0]
    half = PHOTON_LENGTH_SIGMAS * sigma
    return -x_half - half, x_half + half


def photon_axis(x_start: float, x_end: float, origin: np.ndarray = ORIGIN) -> VMobject:
    """Svak linje langs forplantningsaksen."""
    xs = np.array([x_start, x_end])
    return _polyline(
        project(xs, np.zeros(2), np.zeros(2), origin), AXIS_COLOR, AXIS_WIDTH, AXIS_OPACITY
    )


def photon_packet(
    center: float,
    wavelength: float,
    sigma: float = PHOTON_SIGMA,
    amplitude: float = 1.4,
    origin: np.ndarray = ORIGIN,
    stems_per_wavelength: int = 6,
    samples_per_wavelength: int = 60,
) -> VGroup:
    """Foton som bølgepakke med E-felt (gult, langs y) og B-felt (blått, langs z).

    `center` er pakkens sentrum langs x. Bølgemønsteret er fast i rommet
    (sin(2πx/λ)); bare den gaussiske omhyllingskurven flytter seg med `center`.
    E og B er i fase. Hvert felt har en kantlinje (±omhylling) i sitt plan.
    `stems_per_wavelength = 0` slår av de tynne feltstrekene.
    """
    half = PHOTON_LENGTH_SIGMAS * sigma
    n = max(2, int(2 * half / wavelength * samples_per_wavelength))
    u = np.linspace(-half, half, n)
    x = center + u
    env = amplitude * np.exp(-0.5 * (u / sigma) ** 2)
    wave = env * np.sin(2 * np.pi * x / wavelength)

    parts = VGroup()
    # B først, slik at E ligger oppå
    for color, in_y in ((B_FIELD_COLOR, False), (E_FIELD_COLOR, True)):

        def pts(v: np.ndarray, xs: np.ndarray, in_y: bool = in_y) -> np.ndarray:
            z0 = np.zeros_like(xs)
            return project(xs, v, z0, origin) if in_y else project(xs, z0, v, origin)

        for sign in (1, -1):
            envelope = _polyline(
                pts(sign * env, x), ENVELOPE_COLOR, ENVELOPE_WIDTH, ENVELOPE_OPACITY
            )
            parts.add(envelope)

        if stems_per_wavelength:
            # Fast avstand i rommet, slik at strekene ikke "glir" med pakken
            spacing = wavelength / stems_per_wavelength
            xs = np.arange(np.ceil(x[0] / spacing), np.floor(x[-1] / spacing) + 1) * spacing
            vs = amplitude * np.exp(-0.5 * ((xs - center) / sigma) ** 2)
            vs *= np.sin(2 * np.pi * xs / wavelength)
            base = project(xs, np.zeros_like(xs), np.zeros_like(xs), origin)
            for b, t in zip(base, pts(vs, xs), strict=True):
                if np.linalg.norm(t - b) > 0.03:
                    parts.add(
                        Line(
                            b,
                            t,
                            stroke_color=color,
                            stroke_width=STEM_WIDTH,
                            stroke_opacity=STEM_OPACITY,
                        )
                    )

        parts.add(_polyline(pts(wave, x), color, CURVE_WIDTH))
    return parts


def moving_photon(center_of: Callable[[], float], **packet_kwargs) -> VGroup:
    """Foton som tegnes på nytt hvert bilde med sentrum `center_of()`.

    Bygger pakken helt på nytt i stedet for `always_redraw`/`become`, som kan gi
    løse streker når antall delobjekter endrer seg fra bilde til bilde.
    Eksempel: `moving_photon(lambda: x0 + v * t.get_value(), wavelength=0.9)`.
    """
    holder = VGroup()

    def rebuild(group: VGroup) -> None:
        group.submobjects = [photon_packet(center_of(), **packet_kwargs)]

    rebuild(holder)
    holder.add_updater(rebuild)
    return holder
