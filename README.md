# aroma-pacifico-presentation

Final presentation and defense script of the Aroma Pacífico pilot

Part of the Aroma Pacífico pilot, the 2026 update of the coffee traceability pilot for Cauca, Huila and Tolima. Work is tracked in [aroma-pacifico-roadmap](https://github.com/aroma-pacifico/aroma-pacifico-roadmap) and on the [Aroma Pacífico Pilot board](https://github.com/orgs/aroma-pacifico/projects/1).

## What lives here

This repository holds the slide decks, demonstration walkthroughs, speaker notes, and defense scripts for the final executive and academic evaluation of the Aroma Pacífico pilot. Distributed AI agent rules and standards are synchronized here from the canonical `aroma-pacifico-ai-agents` repository.

## Tasks delivered here

- [A25](https://github.com/aroma-pacifico/aroma-pacifico-roadmap/issues/38)

## Contents

| Path | Purpose |
|---|---|
| `deck/aroma-pacifico-sustentacion.pptx` | The defense slides in Spanish: 31 slides (cover, team slide, four part dividers, the 24 content slides and a questions slide), 16:9, with Spanish speaker notes and target times |
| `deck/aroma-pacifico-sustentacion.pdf` | PDF export of the same deck, with Roboto embedded; the safe copy to project |
| `deck/content.yaml` | Slide text, speaker notes and the catalog of diagram crops; edit this to change the deck |
| `deck/build_deck.py` | Generator: reads the design tokens and `content.yaml` and writes the PPTX, the PDF and the previews |
| `deck/assets/` | Rendered inputs: a copy of the design tokens, brand marks, icons, diagram crops, design-system previews and the team portraits (`team/`) |
| `deck/previews/slide-NN.png` | One PNG per slide, rendered from the PDF, for visual review |
| `docs/final-presentation.md` | 20-minute slide deck: 24 slides in four parts by role (SR1, SR2, JR1, JR2), with sources and the register of pending content |
| `docs/speaker-script.md` | Spoken script per slide, with timings and the rehearsal log |
| `docs/defense-qa.md` | Short answers to the likely questions of the defense session |
| `docs/case/case-statement.pdf` | Sole source of requirements |

```text
aroma-pacifico-presentation/
|-- README.md
|-- deck/
|   |-- aroma-pacifico-sustentacion.pdf
|   |-- aroma-pacifico-sustentacion.pptx
|   |-- assets/
|   |   |-- brand/
|   |   |-- icons/
|   |   |-- images/
|   |   |-- team/
|   |   `-- tokens.json
|   |-- build_deck.py
|   |-- content.yaml
|   `-- previews/
`-- docs/
    |-- case/
    |   `-- case-statement.pdf
    |-- defense-qa.md
    |-- final-presentation.md
    `-- speaker-script.md
```

## The slide file

The deck is the Spanish rendering of `docs/final-presentation.md`, built on the Aroma Pacífico design system (`aroma-pacifico-design-system`): colors, font family, sizes, spacing and radius come from `tokens/tokens.json`, the marks from `brand/` and the icons from `icons/`. Text and background pairs are taken from `tokens/contrast-report.md`. Diagrams are crops of the merged SVG exports of `aroma-pacifico-diagrams`, so they stay legible when projected. The cover and the team slide that follows it show the four presenters with their names, deck roles and job roles, and each part opens with a divider that names the presenter, their role and the part time. Names, roles and presentation order live once, under `meta.team` in `deck/content.yaml`.

**Opening it.** Open the PPTX in PowerPoint, Keynote, Google Slides or LibreOffice Impress; the speaker notes carry the script of each slide with its target time. To project without font risk, use the PDF.

**Fonts.** The token font is Roboto (regular and bold), with the token fallback chain Noto Sans, system UI fonts and Arial. Install Roboto from Google Fonts (SIL Open Font License) before editing or presenting the PPTX. Without it, PowerPoint substitutes a sans font such as Arial; the generator sizes every text box against both Roboto and Arial metrics, so the deck still fits with the fallback. The PDF embeds Roboto.

**Editing.** Change text and notes in `deck/content.yaml`, not in PowerPoint, so the next build keeps the edit. Small last-minute fixes can be made in PowerPoint, but they are lost on the next build.

**Regenerating.** The build needs Python 3 with `python-pptx`, `PyYAML` and `Pillow` (`pip install --user python-pptx pyyaml pillow`). Rendering the PDF and previews also needs LibreOffice and `pdftoppm` (poppler-utils), with Roboto installed where LibreOffice can see it.

```bash
python3 deck/build_deck.py             # PPTX only
python3 deck/build_deck.py --render    # PPTX, PDF and deck/previews/slide-NN.png
```

If the design tokens, the brand, the icons or a diagram change, refresh the rendered assets first. This step reads the sibling checkouts of `aroma-pacifico-design-system` and `aroma-pacifico-diagrams` and needs Google Chrome or Chromium for headless SVG rendering:

```bash
python3 deck/build_deck.py --refresh-assets \
  --design-system ../aroma-pacifico-design-system \
  --diagrams ../aroma-pacifico-diagrams --render
```

The team portraits are cropped once from the original photos, which are not kept in the repository. `--team-photos` reads them from a folder and writes 3:4 crops of at most 900 pixels in height to `deck/assets/team/`. Each crop places the eyes and sizes the face from the eye midpoint and the eye-to-chin distance recorded per photo under `assets.team` in `content.yaml`; where a crop leaves a photo at the top, the wall color fills the gap and the build prints a warning naming the photo:

```bash
python3 deck/build_deck.py --team-photos <folder-with-the-photos> --render
```

The build prints a warning and exits with status 1 when a text box may overflow. `--font Arial` builds a copy with the fallback font to check the deck without Roboto. After every build, look at the previews before committing.
