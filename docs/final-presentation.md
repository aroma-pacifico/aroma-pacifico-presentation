# Final Presentation: Proposal Deck

| Field | Value |
|---|---|
| Roadmap issue | aroma-pacifico/aroma-pacifico-roadmap#38 (A25) |
| Slide file | [`deck/aroma-pacifico-sustentacion.pptx`](../deck/aroma-pacifico-sustentacion.pptx) (Spanish, with speaker notes) and its [PDF export](../deck/aroma-pacifico-sustentacion.pdf) |
| Length | 60 narrative slides read in 24 minutes, an annex of 69 diagram slides for questions, and the closing slide repeated as slide 130 |
| Companion files | [Guion de la sustentación](guion-sustentacion.md) (generated, slide by slide), [Defense questions and short answers](defense-qa.md) |
| Source of requirements | `docs/case/case-statement.pdf` |

The deck presents the Aroma Pacífico pilot as a complete technical proposal: the solution is shown designed in full, with the architecture, the code that builds it, the plan and the cost. It has no part dividers and no agenda; the narrative carries the order, and who presents each slide lives only in the speaker notes and the guion. Every content slide has a claim title, a subtitle and figures taken from a merged document of `aroma-pacifico-architecture`, `aroma-pacifico-infrastructure`, `aroma-pacifico-terraform-modules` or `aroma-pacifico-design-system`; the source of each slide is written into its speaker notes, not onto the slide. A figure is a case-statement figure, arithmetic on one, or a design target recorded in the decision log, never a measurement.

## Narrative

The slide numbers below are those of the current build; the guion is regenerated with every build and always carries the exact numbers.

| Slides | Presenter | Topic |
|---|---|---|
| 1 to 2 | SR1 | Cover and team, with the newest portrait of each member |
| 3 to 8 | SR1 | The case, the measurable goals, the client's operating rules, the 2020 pilot and its traceability diagram, and the sizing |
| 9 to 15 | SR1 | ADR-001, the target architecture with the complete diagram and two detail views, and the landing zone with its governance |
| 16 to 27 | JR1 | Addressing, connectivity, no-signal behavior, collection center and port, firewall policy, identity, MFA and revocation |
| 28 to 42 | SR2 | Farm monitoring, the drone service (ADR-002, fumigation flow, state machines, ADR-004), inference, sack custody, data paths and pipelines, observability |
| 43 to 52 | JR2 | ADR-003, IaC traceability D01 to D13, the module catalog v0.1.0 to v0.5.0, stacks and environments, the pc-iac rules, CI with Infracost and Floci, CD up with approval, teardown and rollback, the 100-hour plan by role and week and its critical path |
| 53 to 60 | SR1 | Costs (normal and harvest, breakdown, savings, per farm, Infracost), change control and release notes, the design system, the close, and the closing "Gracias" slide with the QR to the project website |
| 61 to 129 | Annex | Every published diagram in full, each followed by its detail views |
| 130 | None | The closing QR slide again, left on screen when the questions end |

The three sequence diagrams of the IaC pipeline (CI, provisioning, teardown and rollback) are declared as optional in `deck/content.yaml`. Each one has its own slide in the IaC section and an annex entry, and both appear automatically once the diagram is merged in `aroma-pacifico-diagrams` and the deck is rebuilt with `--refresh-diagrams`; until then the build skips them with a note, not an error.

## Visual rules

Chrome is limited to the isotype and the slide number. A diagram slide shows the diagram whole, never cropped or stretched: the image is fitted with its aspect ratio kept into a box of 936 by 472 points, 85.2 percent of the slide, from a master render at three times that size. Where the body text of a diagram would show under about 10 px at a 1920 px projection, the annex adds detail slides that zoom into regions of the same render; each detail names its annex ID and the slide of the full view. Every diagram picture, full or detail, links to its high-resolution view at `https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/<slug>`, and a discreet caption under it, "Ver en alta resolución", carries the same link; the slug is the file stem in `aroma-pacifico-web/assets/diagrams/`. LibreOffice keeps both links as annotations in the PDF. The QR code is generated with error correction H in the brand primary on white, with a four-module quiet zone, and is decoded back on every refresh. The build writes `deck/previews/diagram-legibility.txt` with the body text size of every diagram slide, so the rule is checked on every build.

## Verification

Every build renders all slides to `deck/previews/slide-NNN.png` at 1920 px and writes contact sheets of 30 slides (`contact-sheet-N.png`). The visual gate is to inspect every contact sheet and the full-size diagram slides before committing.
