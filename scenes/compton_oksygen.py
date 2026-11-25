"""Compton-spredning på et oksygenatom.

Viser et oksygen-16-atom (8 p, 8 n, 8 e⁻ i K- og L-skall, Bohr-modell),
der et 100 keV røntgenfoton Compton-sprees på et ytre (L-skall) elektron.
Målgruppe: radiografer og radiologer.

Fysikken er korrekt innenfor modellen:
- Kinematikken (E', T, θ, φ) følger Compton-formelen, og bevegelsesmengde er bevart.
- Bølgelengdeforholdet λ'/λ = E/E' er tegnet i riktig forhold.
- Fotonene beveger seg med samme fart (c), rekylelektronet med v/c ≈ 0,30.
- Kjerne og skall er ikke i skala (kjernen er i virkeligheten titusenvis av ganger mindre).

Render:
    uv run manim -pqh scenes/compton_oksygen.py ComptonOksygen
"""

from __future__ import annotations

import math

import numpy as np
from manim import *

from illustrasjoner import StyledScene, palette, title
from illustrasjoner.physics import (
    ELECTRON_COLOR,
    NEUTRON_COLOR,
    PHOTON_COLOR,
    PROTON_COLOR,
    compton,
    nucleus,
    wave_packet,
)

# --- Fysikk ----------------------------------------------------------------
PHOTON_ENERGY_KEV = 100.0
SCATTER_ANGLE = math.radians(135)
KIN = compton(PHOTON_ENERGY_KEV, SCATTER_ANGLE)

# --- Geometri (manim-enheter) ----------------------------------------------
ATOM_CENTER = np.array([0.0, 0.7, 0.0])
NUCLEUS_RADIUS = 0.06
SHELLS = {  # navn: (radius, antall elektroner, vinkelfart rad/s)
    "K": (0.75, 2, 2 * PI / 2.5),
    "L": (1.8, 6, 2 * PI / 6.0),
}
# Fotonet treffer et L-elektron i bunnen av L-skallet
HIT_POINT = ATOM_CENTER + np.array([0.0, -SHELLS["L"][0], 0.0])

# --- Fart og bølgepakker ------------------------------------------------------
C = 2.0  # lysfart i enheter/s
V_ELECTRON = KIN.electron_beta * C
WAVELENGTH_IN = 0.35
WAVELENGTH_OUT = WAVELENGTH_IN * KIN.wavelength_ratio
SIGMA_IN = 2.2 * WAVELENGTH_IN
SIGMA_OUT = 2.2 * WAVELENGTH_OUT
PHOTON_START_DISTANCE = 9.0  # pakkens sentrum starter så langt til venstre for treffpunktet

DIR_IN = RIGHT
DIR_PHOTON_OUT = rotate_vector(RIGHT, -KIN.photon_angle)  # ned til venstre
DIR_ELECTRON_OUT = rotate_vector(RIGHT, KIN.electron_angle)  # opp til høyre

ZOOM_WIDTH = 0.6  # kamerabredde ved start (zoomet inn på kjernen)


def label(text: str, size: int = 26, color: str = palette.text, **kwargs) -> Text:
    return Text(text, font_size=size, color=color, **kwargs)


class ComptonOksygen(StyledScene):
    def construct(self) -> None:
        self.clock = ValueTracker(0.0)
        self.hit_time: float | None = None
        self.target: tuple[str, int] | None = None

        self.intro_nucleus()
        self.zoom_out_to_atom()
        self.compton_scattering()

    # ------------------------------------------------------------------ #
    # Tid og posisjoner
    # ------------------------------------------------------------------ #
    def tick(self, *animations: Animation, run_time: float) -> None:
        """Spill animasjoner mens scenens klokke (orbitaler, foton) går."""
        self.play(
            *animations,
            self.clock.animate(rate_func=linear).increment_value(run_time),
            run_time=run_time,
        )

    @property
    def t(self) -> float:
        return self.clock.get_value()

    def electron_position(self, shell: str, index: int, t: float) -> np.ndarray:
        radius, count, omega = SHELLS[shell]
        if self.target == (shell, index) and self.hit_time is not None and t >= self.hit_time:
            return HIT_POINT + (t - self.hit_time) * V_ELECTRON * DIR_ELECTRON_OUT
        angle = self.phase(shell) + index * TAU / count + omega * t
        return ATOM_CENTER + radius * np.array([math.cos(angle), math.sin(angle), 0.0])

    @staticmethod
    def phase(shell: str) -> float:
        return {"K": PI / 2, "L": PI / 6}[shell]

    # ------------------------------------------------------------------ #
    # 1. Kjernen, zoomet inn
    # ------------------------------------------------------------------ #
    def intro_nucleus(self) -> None:
        frame = self.camera.frame
        frame.set(width=ZOOM_WIDTH).move_to(ATOM_CENTER)

        self.core = nucleus(8, 8, NUCLEUS_RADIUS).move_to(ATOM_CENTER)
        zoom = ZOOM_WIDTH / config.frame_width

        heading = label("Oksygen-16-kjernen", size=40, weight=BOLD).scale(zoom)
        heading.move_to(ATOM_CENTER + UP * 0.115)
        protons = label("8 protoner", color=PROTON_COLOR, size=30).scale(zoom)
        neutrons = label("8 nøytroner", color=NEUTRON_COLOR, size=30).scale(zoom)
        legend = VGroup(protons, neutrons).arrange(DOWN, aligned_edge=LEFT, buff=0.012)
        legend.next_to(self.core, RIGHT, buff=0.05)

        self.play(
            LaggedStart(*(GrowFromCenter(n) for n in self.core), lag_ratio=0.08),
            run_time=2.0,
        )
        self.play(FadeIn(heading), FadeIn(legend, shift=LEFT * 0.01))
        self.wait(1.5)
        self.intro_labels = VGroup(heading, legend)

    # ------------------------------------------------------------------ #
    # 2. Zoom ut: kjernen blir bitteliten, elektronene i skall
    # ------------------------------------------------------------------ #
    def zoom_out_to_atom(self) -> None:
        frame = self.camera.frame
        w0, w1 = ZOOM_WIDTH, config.frame_width
        c0, c1 = ATOM_CENTER.copy(), ORIGIN.copy()

        def zoom(mob: Mobject, alpha: float) -> None:
            # Logaritmisk zoom føles jevn over store skalaforskjeller
            width = w0 * (w1 / w0) ** alpha
            progress = (width - w0) / (w1 - w0)
            mob.set(width=width).move_to(interpolate(c0, c1, progress))

        self.play(
            UpdateFromAlphaFunc(frame, zoom, rate_func=smooth),
            FadeOut(self.intro_labels, rate_func=rush_from),
            run_time=3.5,
        )

        # Skall og elektroner
        shells = VGroup()
        self.electrons: dict[tuple[str, int], Dot] = {}
        for name, (radius, count, _) in SHELLS.items():
            shells.add(
                Circle(
                    radius=radius, color=palette.muted, stroke_width=1.5, stroke_opacity=0.5
                ).move_to(ATOM_CENTER)
            )
            for i in range(count):
                dot = Dot(radius=0.06, color=ELECTRON_COLOR)
                dot.add_updater(
                    lambda m, s=name, i=i: m.move_to(self.electron_position(s, i, self.t))
                )
                self.electrons[(name, i)] = dot

        self.shell_labels = {
            "K": label("K: 2 e⁻", size=22, color=palette.muted),
            "L": label("L: 6 e⁻", size=22, color=palette.muted),
        }
        self.shell_labels["K"].move_to(ATOM_CENTER + rotate_vector(RIGHT * 1.27, PI / 5))
        self.shell_labels["L"].next_to(
            ATOM_CENTER + rotate_vector(RIGHT * SHELLS["L"][0], PI / 5), UR, buff=0.1
        )

        heading = title("Oksygenatomet (¹⁶O)")
        legend = self.make_legend()
        self.footnote = label(
            "Bohr-modell, ikke i skala: kjernen er i virkeligheten titusenvis av ganger mindre",
            size=20,
            color=palette.muted,
        ).to_edge(DOWN, buff=0.3)

        k_electrons = [self.electrons[("K", i)] for i in range(2)]
        l_electrons = [self.electrons[("L", i)] for i in range(6)]
        for dot in self.electrons.values():
            dot.update()

        self.tick(Create(shells[0]), *(FadeIn(e, scale=0.3) for e in k_electrons), run_time=1.2)
        self.tick(
            Create(shells[1]),
            LaggedStart(*(FadeIn(e, scale=0.3) for e in l_electrons), lag_ratio=0.15),
            run_time=1.8,
        )
        self.tick(
            Write(heading),
            FadeIn(self.shell_labels["K"]),
            FadeIn(self.shell_labels["L"]),
            run_time=1.5,
        )
        self.tick(FadeIn(legend, shift=RIGHT * 0.2), FadeIn(self.footnote), run_time=1.0)
        self.tick(run_time=4.0)

        self.heading = heading

    def make_legend(self) -> VGroup:
        def row(icon: Mobject, text: str) -> VGroup:
            return VGroup(icon, label(text, size=22)).arrange(RIGHT, buff=0.2)

        photon_icon = wave_packet(0, 0.16, 0.18, amplitude=0.09).set_stroke(PHOTON_COLOR, 3)
        legend = VGroup(
            row(Dot(radius=0.07, color=PROTON_COLOR), "Proton"),
            row(Dot(radius=0.07, color=NEUTRON_COLOR), "Nøytron"),
            row(Dot(radius=0.06, color=ELECTRON_COLOR), "Elektron"),
            row(photon_icon, "Foton"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        # Ikoner sentrert i en felles kolonne, tekst venstrejustert etter bredeste ikon
        icon_x = legend[0][0].get_x()
        text_x = icon_x + max(r[0].width for r in legend) / 2 + 0.2
        for r in legend:
            r[0].set_x(icon_x)
            r[1].set_x(text_x, direction=LEFT)
        return legend.to_corner(UL, buff=0.5).shift(DOWN * 0.9)

    # ------------------------------------------------------------------ #
    # 3. Compton-spredning
    # ------------------------------------------------------------------ #
    def choose_target(self) -> None:
        """Velg L-elektronet som når treffpunktet først etter at fotonet er fremme."""
        _, count, omega = SHELLS["L"]
        arrival = self.t + PHOTON_START_DISTANCE / C
        hit_angle = -PI / 2
        best: tuple[float, int] | None = None
        for i in range(count):
            angle = self.phase("L") + i * TAU / count + omega * arrival
            delay = ((hit_angle - angle) % TAU) / omega
            if best is None or delay < best[0]:
                best = (delay, i)
        assert best is not None
        delay, index = best
        self.target = ("L", index)
        self.hit_time = arrival + delay

    def compton_scattering(self) -> None:
        self.choose_target()
        assert self.hit_time is not None
        hit_time = self.hit_time

        def incoming() -> VMobject:
            s = C * (self.t - hit_time)
            return (
                wave_packet(s, WAVELENGTH_IN, SIGMA_IN, s_max=0.0)
                .set_stroke(PHOTON_COLOR, 4)
                .shift(HIT_POINT)
            )

        def scattered() -> VMobject:
            s = C * (self.t - hit_time)
            return (
                wave_packet(s, WAVELENGTH_OUT, SIGMA_OUT, s_min=0.0)
                .set_stroke(PHOTON_COLOR, 4)
                .rotate(-KIN.photon_angle, about_point=ORIGIN)
                .shift(HIT_POINT)
            )

        photon_in = always_redraw(incoming)
        photon_out = always_redraw(scattered)
        self.add(photon_in, photon_out)

        new_heading = title("Compton-spredning")
        in_label = VGroup(
            label("Røntgenfoton"),
            label(f"E = {PHOTON_ENERGY_KEV:.0f} keV", color=PHOTON_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        in_label.move_to(np.array([-5.0, HIT_POINT[1] + 0.85, 0]))

        # Fram til treffet
        self.tick(
            Transform(self.heading, new_heading),
            FadeOut(self.footnote),
            run_time=1.0,
        )
        self.tick(FadeIn(in_label, shift=RIGHT * 0.2), run_time=1.0)
        self.tick(run_time=hit_time - self.t)

        # Treffet
        target_dot = self.electrons[self.target]
        track = TracedPath(
            target_dot.get_center, stroke_color=ELECTRON_COLOR, stroke_width=2, stroke_opacity=0.6
        )
        self.add(track)
        self.tick(
            Flash(HIT_POINT, color=PHOTON_COLOR, line_length=0.25, flash_radius=0.2),
            run_time=0.6,
        )
        out_label = VGroup(
            label("Spredt foton"),
            label(f"E′ ≈ {KIN.scattered_energy_kev:.0f} keV", color=PHOTON_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        out_label.move_to(HIT_POINT + 2.2 * DIR_PHOTON_OUT).shift(LEFT * 2.0)

        e_label = VGroup(
            label("Rekylelektron"),
            label(f"T ≈ {KIN.electron_energy_kev:.0f} keV", color=ELECTRON_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        e_label.move_to(HIT_POINT + 5.8 * DIR_ELECTRON_OUT).shift(DOWN * 0.95)

        ion_label = VGroup(
            label("Ionisert atom"),
            label("O⁺", color=palette.secondary, size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        ion_label.next_to(ATOM_CENTER + RIGHT * SHELLS["L"][0], RIGHT, buff=0.5).shift(UP * 0.4)

        new_l_label = label("L: 5 e⁻", size=22, color=palette.muted).move_to(
            self.shell_labels["L"], aligned_edge=LEFT
        )

        self.tick(FadeIn(out_label), FadeIn(e_label), run_time=1.4)
        self.tick(
            FadeIn(ion_label),
            Transform(self.shell_labels["L"], new_l_label),
            run_time=1.2,
        )

        # Vinkler
        reference = DashedLine(
            HIT_POINT, HIT_POINT + 1.4 * DIR_IN, color=palette.muted, stroke_width=2
        )
        theta_arc = Arc(
            radius=0.55,
            start_angle=0,
            angle=-KIN.photon_angle,
            arc_center=HIT_POINT,
            color=PHOTON_COLOR,
            stroke_width=2.5,
        )
        phi_arc = Arc(
            radius=1.0,
            start_angle=0,
            angle=KIN.electron_angle,
            arc_center=HIT_POINT,
            color=ELECTRON_COLOR,
            stroke_width=2.5,
        )
        theta_sym = MathTex(r"\theta", color=PHOTON_COLOR, font_size=34).move_to(
            HIT_POINT + rotate_vector(RIGHT * 0.85, -KIN.photon_angle / 2)
        )
        phi_sym = MathTex(r"\phi", color=ELECTRON_COLOR, font_size=34).move_to(
            HIT_POINT + rotate_vector(RIGHT * 1.25, KIN.electron_angle / 2)
        )
        self.tick(
            Create(reference),
            Create(theta_arc),
            Create(phi_arc),
            FadeIn(theta_sym),
            FadeIn(phi_sym),
            run_time=1.5,
        )

        # Formel og energibalanse
        formula = MathTex(r"E' = \frac{E}{1 + (E / m_e c^2)(1 - \cos\theta)}", font_size=38)
        numbers = label(
            f"θ = {math.degrees(KIN.photon_angle):.0f}°,  "
            f"φ ≈ {math.degrees(KIN.electron_angle):.0f}°",
            size=22,
            color=palette.muted,
        )
        balance = label("E = E′ + T  (+ bindingsenergi ≈ 14 eV)", size=22, color=palette.muted)
        panel = VGroup(formula, numbers, balance).arrange(DOWN, buff=0.25)
        panel.to_corner(DR, buff=0.5)

        self.tick(Write(formula), run_time=2.0)
        self.tick(FadeIn(numbers), FadeIn(balance), run_time=1.0)
        self.tick(run_time=5.0)
