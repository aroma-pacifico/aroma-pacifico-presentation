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
| `deck/aroma-pacifico-sustentacion.pptx` | The proposal deck in Spanish, 16:9: 60 narrative slides and an annex with every diagram in full and in detail, with Spanish speaker notes that name the presenter, the target time and the source |
| `deck/aroma-pacifico-sustentacion.pdf` | PDF export of the same deck, with Roboto embedded; the safe copy to project |
| `deck/content.yaml` | Slide text, speaker notes, the frame of the guion, the diagram catalog with its detail regions, and the team; edit this to change the deck |
| `deck/build_deck.py` | Generator: reads the design tokens and `content.yaml` and writes the PPTX, the guion, the PDF, the previews and the contact sheets |
| `deck/assets/` | Rendered inputs: a copy of the design tokens, brand marks, icons, the diagram renders and their detail views (`diagrams/`), design-system previews, the QR code and the team portraits (`team/`) |
| `deck/previews/` | One 1920 px PNG per slide (`slide-NNN.png`), contact sheets of 30 slides and the diagram legibility report, for the visual gate |
| `docs/final-presentation.md` | Overview of the deck: narrative, presenters by slide range and the visual rules |
| `docs/guion-sustentacion.md` | Spanish script, slide by slide, with presenters, times, transitions and the annex map; generated from `content.yaml` |
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
|   |   |-- diagrams/
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
    `-- guion-sustentacion.md
```

## The slide file

The deck is a complete project proposal, described in `docs/final-presentation.md` and built on the Aroma Pacífico design system (`aroma-pacifico-design-system`): colors, font family, sizes, spacing and radius come from `tokens/tokens.json`, the marks from `brand/` and the icons from `icons/`. Text and background pairs are taken from `tokens/contrast-report.md`. Diagrams come from the merged SVG exports of `aroma-pacifico-diagrams`: each is shown whole, fitted into 85 percent of the slide, and the annex adds zoomed detail slides wherever its text would be under about 10 px at 1920 px. Chrome is limited to the isotype and the slide number. The cover and the team slide show the four presenters with their names and roles; who presents each slide appears only in the speaker notes and the guion. Names, roles and presentation order live once, under `meta.team` in `deck/content.yaml`.

**Opening it.** Open the PPTX in PowerPoint, Keynote, Google Slides or LibreOffice Impress; the speaker notes carry the presenter, the target time, the source and the script of each slide, the same text as `docs/guion-sustentacion.md`. To project without font risk, use the PDF.

**Fonts.** The token font is Roboto (regular and bold), with the token fallback chain Noto Sans, system UI fonts and Arial. Install Roboto from Google Fonts (SIL Open Font License) before editing or presenting the PPTX. Without it, PowerPoint substitutes a sans font such as Arial; the generator sizes every text box against both Roboto and Arial metrics, so the deck still fits with the fallback. The PDF embeds Roboto.

**Editing.** Change text and notes in `deck/content.yaml`, never in PowerPoint and never in the guion, so the next build keeps the edit. The target time of a slide is its notes read at 130 words per minute, and the build warns when the talk leaves the 20 to 25 minute target.

**Regenerating.** The build needs Python 3 with `python-pptx`, `PyYAML`, `Pillow` and `segno` (`pip install --user python-pptx pyyaml pillow segno`). Rendering the PDF and previews also needs LibreOffice and `pdftoppm` (poppler-utils), with Roboto installed where LibreOffice can see it.

```bash
python3 deck/build_deck.py             # PPTX and docs/guion-sustentacion.md
python3 deck/build_deck.py --render    # also the PDF, deck/previews/slide-NNN.png and the contact sheets
```

If the design tokens, the brand, the icons or a diagram change, refresh the rendered assets first. This step reads the sibling checkouts of `aroma-pacifico-design-system` and `aroma-pacifico-diagrams` and needs Google Chrome or Chromium for headless SVG rendering:

```bash
python3 deck/build_deck.py --refresh-assets \
  --design-system ../aroma-pacifico-design-system \
  --diagrams ../aroma-pacifico-diagrams --render
```

When only the diagrams change, for example when a new diagram of the catalog merges, `--refresh-diagrams` re-renders the diagrams, their detail views and the QR code without touching the other assets. Diagrams marked `optional` in the catalog are skipped with a note until they exist.

```bash
python3 deck/build_deck.py --refresh-diagrams --diagrams ../aroma-pacifico-diagrams --render
```

The team portraits are cropped once from the original photos, which are not kept in the repository. `--team-photos` reads them from a folder, takes the newest file of each member (by modification time, for example `jeanpaul-v2.jpeg` over `jeanpaul.jpeg`) and writes 3:4 crops of at most 900 pixels in height to `deck/assets/team/`. Each crop places the eyes and sizes the face from the eye midpoint and the eye-to-chin distance recorded per photo file under `assets.team` in `content.yaml`; where a crop leaves a photo at the top, the wall color fills the gap and the build prints a warning naming the photo:

```bash
python3 deck/build_deck.py --team-photos <folder-with-the-photos> --render
```

The build prints a warning and exits with status 1 when a text box may overflow, a diagram stays under about 9 px at 1920 px, or the talk leaves its time target; skipped optional diagrams are printed as notes and do not fail the build. `--font Arial` builds a copy with the fallback font to check the deck without Roboto. After every build, inspect the contact sheets and the full-size diagram slides before committing.
