# Final Presentation: Slide Deck

| Field | Value |
|---|---|
| Status | Agent draft, rehearsal pending |
| Roadmap issue | aroma-pacifico/aroma-pacifico-roadmap#38 (A25) |
| Length | 20 minutes, 18 slides, four presenters by role |
| Companion files | [Speaker script](speaker-script.md), [Defense questions and short answers](defense-qa.md) |
| Source of requirements | `docs/case/case-statement.pdf` |

This deck is the slide content only. Each slide lists its on-screen text, its source in the architecture repository and its time. The slide design (layout, colors, typography) follows the design system of A24 once it merges; until then the slides are plain text blocks. Every figure on a slide is either a figure of the case statement, arithmetic on those figures, or a design target recorded in the decision log. None is a measurement. Content that depends on a task that has not merged is marked `PENDING` and names its source issue; the register at the end of this file lists them all.

## Time plan

| Part | Presenter | Slides | Minutes | Cumulative | Topic |
|---|---|---|---|---|---|
| 1 | SR1 | 1 to 4 | 4:00 | 4:00 | What changes since 2020, the architecture and the governance and security base |
| 2 | SR2 | 5 to 8 | 5:00 | 9:00 | Connectivity: farm, transporter, drone link, collection center and port, with and without signal |
| 3 | JR1 | 9 to 12 | 5:00 | 14:00 | Flight mode, pest-to-fumigation flow, inference and observability |
| 4 | JR2 | 13 to 18 | 6:00 | 20:00 | Why the infrastructure code fits 100 hours, release notes, costs, design system and close |

The case statement asks the team to sustain three things: the connectivity (part 2), the flight mode (part 3) and why the infrastructure code fits 100 hours (part 4). Each has the longest block of its part.

## Part 1: Framing and base (SR1, 4:00)

### Slide 1: The pilot and the defense (0:45)

| On the slide | Source |
|---|---|
| Aroma Pacífico: 2026 update of the coffee traceability pilot, Cauca, Huila and Tolima | Case statement, "Contexto" |
| 200 farms, 3 collection centers, 60 transporters, delivery at the port of Buenaventura | Case statement, "Cifras del piloto" |
| Plan-only delivery: design, modular Terraform, no apply, no deployment | [Architecture, section 1](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#1-executive-summary) |
| Agenda: four parts by role, three things we sustain (connectivity, flight mode, IaC in 100 hours) | [Architecture, section 16](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#16-defense-guide) |

### Slide 2: What changes since 2020 (1:15)

| 2020 assumption | 2026 design | Source |
|---|---|---|
| Data coverage on most farms; device publishes straight to the ingestion point | Every flow has an exit protocol, a local buffer of at most 24 hours and a defined behavior without signal | [Architecture, section 12](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#12-store-and-forward-and-no-signal-behavior) |
| Collection center and port without LAN or WAN | Segmented LAN per center with a 100 Mbps WAN; no Federation equipment at the port | [Architecture, section 5](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#5-point-3-network-and-connectivity) |
| A mobile network generation that may be switched off | No dependency on a switched-off generation; LTE-based bearer, satellite IP bearer for farms out of coverage | [Connectivity](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/connectivity.md) |
| 2020 prices and services | Not a valid quote; cost document is new | A23 (see slide 16) |

Closing line of the slide: the 2020 record of what is kept and what is retired is [section 13 of the architecture document](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#13-the-2020-pilot-what-is-kept-changed-and-retired).

### Slide 3: The architecture at a glance (1:15)

Full-slide image: the complete diagram, `aroma-pacifico-diagrams/complete/architecture.png` ([SVG](https://github.com/aroma-pacifico/aroma-pacifico-diagrams/blob/main/complete/architecture.svg) for the print version). A second image, `aroma-pacifico-diagrams/complete/architecture-iac.png`, is held in reserve for slide 13.

| Callout on the image | Text |
|---|---|
| Cloud | AWS primary, one Region (`us-east-1`), Azure prepared only as an undeployed export target (ADR-001) |
| Accounts | One organization, five member accounts: security, network, production, test, development |
| Edge | Two solar nodes per farm, drone ground station, transporter and farmer apps, a LAN per center |
| Boxes | D01 to D13 mark what the infrastructure code builds |

### Slide 4: Governance and security base (0:45)

| Topic | On the slide | Source |
|---|---|---|
| Governance | Service control policies, tag policy, budgets and organization trail applied from the root; five transversal tags carry the cost split | [Landing zone](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/landing-zone.md) |
| Identities | Separate identities and least privilege for six roles; MFA for collection-center operator, drone operator, platform operator and the agronomist | [Security and identity](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/security-and-identity.md) |
| Data | TLS in transit, customer-managed keys at rest, 5-year retention, buyer sees origin, process dates, status and drying variables only | Same |
| Revocation | A lost drone or a decommissioned node is revoked and stops publishing | Same, section 10 |

## Part 2: Connectivity (SR2, 5:00)

### Slide 5: One rule for every flow (1:30)

Statement on the slide: identity, not address. Farms, phones and drones hold no cloud address; they authenticate by certificate or token, so growing from 200 to 1,000 farms adds identities, not subnets.

| Fact | Value | Source |
|---|---|---|
| Telemetry protocol | MQTT over TLS, X.509 device certificate, QoS 1, to the regional IoT endpoint | Architecture, section 12 |
| Crop reading cadence | Every 4 hours, 6 readings a day; drying every hour while a lot is open | Case statement |
| Alert latency | Under 5 minutes with a delivery route (design target, first receipt on push or SMS) | Case statement; ASM-224 |
| Addressing | Centers 10.41, 10.42, 10.43; AWS supernet 10.80.0.0/13, one /16 per environment (`dev` 80, `qa` 81, `pdn` 82) | [Addressing plan](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/addressing-plan.md) |

### Slide 6: Without signal (1:30)

| Actor | Buffer | Behavior without signal | Released when |
|---|---|---|---|
| Farm node | Encrypted ring buffer, at most 24 hours | Keeps reading; on reconnection publishes a live reading first, then drains oldest first; alert raised at drain, marked delayed | Each reading is acknowledged |
| Farm out of coverage | Same node | Same MQTT over a satellite IP bearer; no new radio base, no weekly visit | Next contact |
| Transporter app | Encrypted outbox, at least 7 days of positions | Position every 5 minutes; custody events never evicted; positions thinned to one per 15 minutes before any drop | API confirms persistence |
| Drone | Mission preloaded at the municipal seat or the center | Flight proceeds; record stays in the buffer; no fumigation closure without the record | Persistence receipt for each object |

Source: [architecture, section 12](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#12-store-and-forward-and-no-signal-behavior). The numeric values beyond the case statement are assumptions ASM-073 to ASM-079.

### Slide 7: Collection center and port (1:00)

| Item | Design | Source |
|---|---|---|
| LAN | One pattern, three centers; seven zones with the reserved /24 blocks, one SSID per client zone; visitors have no route to logistics or management | [Collection-center network](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/collection-center-network.md) |
| WAN | 100 Mbps symmetric; two IPsec tunnels to a Transit Gateway with a cellular backup | Architecture, section 1 |
| Capacity | At an assumed 50 percent active clients at the peak: 68 Mbps down and 17 up needed, against 90 planned (ASM-084, ASM-085) | Architecture, section 5 |
| Port | No Federation equipment; the platform records only the delivery event, sent by the transporter app | [Connectivity, section 10](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/connectivity.md#10-port-of-buenaventura) |

### Slide 8: Firewall and what we did not buy (1:00)

| On the slide | Source |
|---|---|
| Perimeter firewall per center and a cloud firewall; policy tables with source, destination, port, action and permanent or temporary | [Firewall policy](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/firewall-policy.md) |
| No NAT gateway and no network firewall appliance in the cloud; AWS services reached through endpoints | Architecture, section 15 |
| Data tier has no route to the internet and is never reachable from a center | Architecture, section 5 |
| Transition line to part 3: the same link logic decides how a drone mission survives a dropped link | Slide 9 |

## Part 3: Flight mode and workloads (JR1, 5:00)

### Slide 9: Combined flight mode (1:30)

| Mode | Services | Why |
|---|---|---|
| Area | Delimit the plot, estimate the harvest | Steady state of every farm; one flight per harvest for the estimate |
| Precision | Confirm the alert, fumigate the focus, verify the same plot | Entered only through a crop alert |
| Switch | `crop_alert_raised` then `focus_confirmed` | Only a confirmed focus can lead to a fumigation order |

Statement on the slide: only the combined mode covers the five mandatory services, none of which can be replaced by another. A contracted certified operator flies; a Federation agronomist authorizes each fumigation as a human identity with MFA. Source: [ADR-002](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-002-drone-flight-mode-and-governance.md).

### Slide 10: From alert to closed case (1:15)

Image: the pest-to-fumigation sequence and state machine from `aroma-pacifico-diagrams` (drone fumigation sequence, merged in the diagrams repository). Text under the image:

| Gate | Rule |
|---|---|
| Order cannot leave | No plot polygon, or no closed flight record |
| Fumigation stays open | Until the verification object arrives and is persisted |
| Authorization | Human identity only; no trigger executes it |
| Link drops over the plot | Mission already loaded; record published on restore |

Source: [drone service](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/drone-service.md).

### Slide 11: Event-driven inference (1:00)

| On the slide | Source |
|---|---|
| Four functions, one per trigger: telemetry batch, focus confirmation, verification, harvest estimate | [Inference functions](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/inference-functions.md) |
| A function reads a persisted object, calls managed inference in `us-east-1`, writes the result with timestamp, confidence and source object | Same |
| No model is trained; no persistent compute waits for objects; a failed invocation leaves the source object and the case state unchanged | Case statement, Part E |
| Data that leaves Colombia: stored and processed in `us-east-1`; only screened crop images and alert-opening readings reach the model | Architecture, section 1 |

### Slide 12: Observability and the two SLOs (1:15)

| SLO | SLI | Objective (design target) | Source |
|---|---|---|---|
| Crop alert delivery | Share of alert openings whose first receipt arrives within 300 seconds of the reading | 95 percent over a rolling 28 days | ASM-224 |
| Sack lookup availability | Share of lookup requests answered without a 5XX or 429 | 99.5 percent over a rolling 28 days | ASM-225 |

Below the table, one line for the five detections of the case statement (silent nodes over 24 hours, undelivered alerts, flights without a persisted record, fumigations without closure, failed invocations that did not change state) and one line for the two dashboards, operational and cost. Source: [observability](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/observability.md). Nothing is deployed: these are definitions, and their tests are future work.

## Part 4: Infrastructure as code, change, cost and close (JR2, 6:00)

### Slide 13: Why the code fits 100 hours (2:00)

Image: `architecture-iac.png`, the diagram with boxes D01 to D13.

| What the code covers | What it deliberately leaves out |
|---|---|
| Terraform, one tool whose 26 binding rules already exist | The landing zone (designed, not coded) |
| One pattern environment planned (`qa`), one stack per domain | The 200 farms and the three centers |
| One pattern module: telemetry ingestion; one farm module; one function pattern (threshold) | The other three inference functions, the sack lookup module, application code |
| Remote state: one encrypted, versioned, natively locked S3 bucket per environment | Cognito pools and CodeDeploy deployments |
| Secrets out of the repository and out of the state | Observability, release notes, costs, design system and this defense (they are separate deliverables outside the 100 hours) |

Sources: [ADR-003](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-003-iac-tool-remote-state-and-pattern-module.md) and [100-hour plan, section 2](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/iac-plan-100h.md#2-scope-what-counts-in-the-100-hours).

### Slide 14: The 100-hour plan in numbers (1:15)

| Check | Value | Source |
|---|---|---|
| Tasks | 13 issues, B01 to B13, split into 19 parts, each with owner, order, dependency and diagram box | Plan, section 4.1 |
| Total | 98 hours booked; 2 hours reserve | Plan, section 9 |
| Largest task | 10 hours (limit is 10) | Plan, section 9 |
| Capacity | 4 people at 5 hours a day for 10 working days is 200 hours; 49 percent booked | Plan, section 6.1 |
| Finish | Working hour 38 of 50, Day 8 of 10 | Plan, section 9 |
| Top risks | Plan evidence needs a human-provisioned account (PD-019); feature behavior not yet re-checked live (PD-200) | Plan, section 8 |
| Result of the final validation (B13) | PENDING: source aroma-pacifico/aroma-pacifico-roadmap#33 | not merged |

### Slide 15: Controlled change and release notes (1:00)

| On the slide | Source |
|---|---|
| Pull request gates, saved `qa` plan, `pdn` applies only the reviewed saved plan after a named human approval | [Automation and pipelines](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/automation-and-pipelines.md) |
| No production change between 05:00 and 18:00 in harvest week, except an incident | Case statement, "Automatización y cambio" |
| Two release note templates, application and infrastructure, each with one completed example; both state what changes, the window, impact, approval, notice to the Federation and rollback | [Release notes](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/release-notes/README.md) |
| The examples are fictional and claim no approval or notice | Same |

### Slide 16: Cost (0:45)

| On the slide | Status |
|---|---|
| Cost of a normal month, a harvest month, one farm's hardware and the drone campaign | PENDING: source aroma-pacifico/aroma-pacifico-roadmap#36 (A23, cost document) |
| Function invocations in harvest and the cost per thousand | PENDING: same source |
| Decisions that lower or avoid cost (no NAT gateway, CloudFront in front of the lookup, contracted drone service, one Region, on-demand database) | Available now: [architecture, section 15](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#15-decisions-that-lower-or-avoid-cost); amounts PENDING |

Do not write a price on this slide before the cost document merges.

### Slide 17: Design system (0:30)

| On the slide | Status |
|---|---|
| Logo, palette with sack states and crop alert, typography, spacing, base components, usage rules | PENDING: source aroma-pacifico/aroma-pacifico-roadmap#37 (A24, design system) |
| The system applied to the farmer app, the transporter app and the sack lookup | PENDING: same source |

### Slide 18: Close and what stays open (0:30)

| On the slide | Source |
|---|---|
| Three things sustained: connectivity, flight mode, IaC in 100 hours | Slides 5 to 9 and 13 to 14 |
| Open decisions owned by the Federation (clarification session answers, thresholds, drone operator contract) | [Architecture, section 17](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#17-open-decisions-for-the-defense) |
| Nothing was applied or deployed; every latency, recovery time and capacity is a design target | Architecture, section 2 |
| Questions | [Defense questions](defense-qa.md) |

## Pending content register

| Slide | Missing content | Source issue | Update when it merges |
|---|---|---|---|
| 14 | Result and evidence of the final validation of the executable plan | aroma-pacifico/aroma-pacifico-roadmap#33 (B13) | Replace the pending row with the evidence and the module tag it used |
| 16 | Every amount: normal month, harvest month, farm hardware, drone campaign, invocation cost | aroma-pacifico/aroma-pacifico-roadmap#36 (A23) | Copy the totals and their assumption IDs; recheck the script and answer 6 of the defense questions |
| 17 | The design system and its application to the three apps | aroma-pacifico/aroma-pacifico-roadmap#37 (A24) | Add a screenshot of the applied sheet; apply the palette and typography to the whole deck |
| 3, 10, 13 | Final diagram exports, if the diagrams repository changes them | aroma-pacifico-diagrams `complete/` | Re-export the images used on the slides |
| 18 | Answers of the clarification session | PD-005 in the decision log | Update open decisions and any answer that changes |
