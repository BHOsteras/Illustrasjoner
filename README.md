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
src/illustrasjoner/physics.py partikkelfarger og standardtegning av fotoner
scenes/                       én fil per illustrasjon (eller tema)
manim.cfg                     render-innstillinger (oppløsning, fps, output-mappe)
media/                        generert output (ignoreres av git)
```

## Lage en ny illustrasjon

1. Lag `scenes/<navn>.py`.
2. Arv fra `StyledScene` og bruk fargene fra `palette` (roller som `palette.primary`,
   ikke hex-koder), slik at alt holder samme stil.
3. Følg stilreglene i `AGENTS.md` (bl.a. ingen tekst eller likninger som standard).

```python
from manim import *
from illustrasjoner import StyledScene, palette


class MinIllustrasjon(StyledScene):
    def construct(self):
        self.play(Create(Circle(radius=1.5, color=palette.primary)))
```

## Rendering

```bash
uv run manim -pql scenes/foton.py Foton            # rask forhåndsvisning (480p)
uv run manim -pqh scenes/foton.py Foton            # full kvalitet (1080p)
uv run manim -s   scenes/foton.py Foton            # bare siste bilde som PNG
uv run manim -qh --transparent scenes/...          # gjennomsiktig bakgrunn (.mov)
uv run manim -pqh scenes/foton.py Foton -o navn    # velg navn på utfila
```

Det siste argumentet er navnet på scene-klassen i fila, ikke navnet på utfila.

Output havner i `media/videos/<fil>/<kvalitet>/`.

## Kodekvalitet

```bash
uv run ruff check . && uv run ruff format .
```
