# Illustrasjoner

Manim-illustrasjoner til presentasjoner, alle med samme visuelle stil.

## Oppsett

Systemavhengigheter (Fedora), én gang:

```bash
sudo dnf install gcc cairo-devel pango-devel pkgconf-pkg-config
```

Python-miljø (uv lager `.venv/` og installerer alt fra `uv.lock`):

```bash
uv sync
```

For `MathTex`/`Tex` (LaTeX-formler):

```bash
sudo dnf install texlive-scheme-basic texlive-standalone tex-preview \
    texlive-dvisvgm texlive-amsmath texlive-amsfonts texlive-doublestroke \
    texlive-relsize texlive-ragged2e texlive-fundus-calligra texlive-microtype \
    texlive-wasysym texlive-physics texlive-setspace texlive-rsfs texlive-jknapltx \
    texlive-mathastext texlive-babel-english texlive-babel-norsk texlive-hyphen-norwegian
```

## Struktur

```
src/illustrasjoner/style.py   felles stil: palett, fonter, StyledScene, hjelpefunksjoner
src/illustrasjoner/physics.py partikkelfarger, kinematikk (Compton), atomkjerne, bølgepakke
scenes/                       én fil per illustrasjon (eller tema)
manim.cfg                     render-innstillinger (oppløsning, fps, output-mappe)
media/                        generert output (ignoreres av git)
```

## Lage en ny illustrasjon

1. Lag `scenes/<navn>.py`.
2. Arv fra `StyledScene` og bruk fargene fra `palette` (roller som `palette.primary`,
   ikke hex-koder), slik at alt holder samme stil.

```python
from manim import *
from illustrasjoner import StyledScene, palette, title


class MinIllustrasjon(StyledScene):
    def construct(self):
        self.play(Write(title("Overskrift")))
```

## Rendering

```bash
uv run manim -pql scenes/hello_world.py HelloWorld   # rask forhåndsvisning (480p)
uv run manim -pqh scenes/hello_world.py HelloWorld   # full kvalitet (1080p)
uv run manim -s   scenes/hello_world.py HelloWorld   # bare siste bilde som PNG
uv run manim -qh --transparent scenes/...            # gjennomsiktig bakgrunn (.mov)
```

Output havner i `media/videos/<fil>/<kvalitet>/`.

## Kodekvalitet

```bash
uv run ruff check . && uv run ruff format .
```
