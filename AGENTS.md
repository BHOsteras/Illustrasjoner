# Retningslinjer for illustrasjoner

Instruksjoner for AI-agenter som lager eller endrer illustrasjoner i dette prosjektet.
Se `README.md` for oppsett, struktur og rendering.

## Standardstil for nye illustrasjoner

Illustrasjonene skal som regel inn i PowerPoint, der teksten står for seg selv på
lysbildet. Derfor gjelder dette som standard:

- **Ingen tekst** i videoen: ingen titler, etiketter, tegnforklaringer, tallverdier
  eller fotnoter, med mindre brukeren ber om det.
- **Ingen likninger** (`MathTex`/`Tex`), med mindre brukeren ber om det.
- Figuren skal forklare seg selv visuelt gjennom form, farge, bevegelse og plassering.
- **Tynne streker** og **ingen fyllfarger**.
- Bruk `StyledScene` og fargerollene i `palette` (og partikkelfargene i `physics.py`),
  slik at alt holder samme stil.

## Fotoner

Fotoner tegnes alltid med `photon_packet` / `moving_photon` i
`src/illustrasjoner/physics.py` (se `scenes/foton.py` for et minimalt eksempel):

- Bølgepakke sett skrått i 3D: x er forplantningsretningen, **E-feltet svinger langs y**,
  **B-feltet langs z**. E og B er i fase.
- Farger: E-feltet og omhyllingskurven er **gule** (`PHOTON_COLOR`), B-feltet er **blått**.
- Hvert felt har sin egen kantlinje (±gaussisk omhylling) i sitt plan, pluss svake, tynne
  feltstreker fra aksen ut til kurven. En svak linje markerer forplantningsaksen.
- **Bevegelse:** bølgemønsteret står fast i rommet. Det er bare omhyllingskurven som
  vandrer med fast fart (`PHOTON_SPEED`), slik at feltene i hvert punkt vokser fram fra null,
  når et maksimum og forsvinner. Ingen svingning i tid og ingen translasjon av kurvene.
- Pakken starter og slutter utenfor bildet (`photon_travel_range`).
- Når fotoner med ulik energi vises sammen: bølgelengde λ = hc/E
  (`photon_wavelength_pm`) i **felles skala**, samme fart, omhylling og amplitude, slik at
  bare frekvensen skiller dem (se `scenes/fotonenergier.py`).

## Vedlikehold av denne fila

Når brukeren ber om det, eller når en stilmessig beslutning eller annen preferanse ser ut
til å gjelde generelt (ikke bare én illustrasjon), skal agenten **spørre** om den skal
legges inn her. Ikke legg til noe uten å spørre.
