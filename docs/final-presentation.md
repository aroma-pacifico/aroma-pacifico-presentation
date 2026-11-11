# Final Presentation: Slide Deck

| Field | Value |
|---|---|
| Status | Agent draft, rehearsal pending |
| Roadmap issue | aroma-pacifico/aroma-pacifico-roadmap#38 (A25) |
| Length | 20 minutes, 18 slides, four presenters by role |
| Companion files | [Speaker script](speaker-script.md), [Defense questions and short answers](defense-qa.md) |
| Source of requirements | `docs/case/case-statement.pdf` |

This deck is the slide content only. Each slide lists its on-screen text, its source in the architecture repository and its time. The slide specifications incorporate the visual design system of A24 (brand assets, typography, outdoor contrast rules, and palette) and the pilot cost model of A23. Every figure on a slide is either a figure of the case statement, arithmetic on those figures, or a design target recorded in the decision log. None is a measurement. Content that depends on a task that has not merged is marked `PENDING` and names its source issue (specifically B13 final validation); the register at the end of this file lists open dependencies.

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
| Security module | Merged `modules/security` (box D06, B06): eight rotated customer-managed keys (CMKs), staff Cognito pool with TOTP MFA, field pool passwordless, seven role groups | `aroma-pacifico-terraform-modules` PR #12 |
| Data & Revocation | TLS in transit, CMKs at rest, 5-year retention; immediate revocation IAM role for lost drones or decommissioned nodes | [Security and identity, section 10](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/security-and-identity.md#10-revocation-flow-for-a-compromised-farm-node-or-drone); PR #12 |

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
| Codified inference pattern: merged `modules/inference-functions` (box D10, B10) with SQS queue, dead-letter queue, least-privilege IAM role, and Lambda invoking Amazon Nova Pro via Bedrock | `aroma-pacifico-terraform-modules` PR #14 |
| Standardized result contract: functions persist timestamp (`result_at`), confidence, and source object (`source`); zero persistent compute (no EC2, ECS, or provisioned concurrency) | Same; case statement, Part E |
| Data leaving Colombia: stored and processed in `us-east-1`; only screened crop images and alert-opening readings reach the model | Architecture, section 1 |
| Drone capability orchestrator (event-driven): the custom bus and its rules route each mission event to its capability, per-function queues buffer it with retries and a dead-letter queue, and the mission state machine in DynamoDB is the source of truth; no central workflow engine in the pilot | [ADR-004](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-004-drone-capability-orchestration.md) |

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
| Reusable IaC modules: telemetry ingestion (`modules/telemetry-ingestion`), farm monitoring (`modules/farm-monitoring`), base security (`modules/security`, B06/PR #12), and inference function pattern (`modules/inference-functions`, B10/PR #14) | The other three inference functions, the sack lookup module, application code |
| Remote state: one encrypted, versioned, natively locked S3 bucket per environment | CodeDeploy deployments and manual cluster infrastructure |
| Environment isolation and secrets (B03/PR #6): `environments/{dev,qa,pdn}/*.tfvars.example`, external injection via GitHub OIDC and `TF_VAR_*`, no plaintext secrets in repository or state (ADR-003) | Observability, release notes, costs, design system and this defense (separate deliverables outside the 100 hours) |

Sources: [ADR-003](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-003-iac-tool-remote-state-and-pattern-module.md), [100-hour plan, section 2](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/iac-plan-100h.md#2-scope-what-counts-in-the-100-hours), `aroma-pacifico-infrastructure` PR #6, and `aroma-pacifico-terraform-modules` PRs #12 and #14.

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

| Cost Domain | On the slide (exact figures from cost document) | Architectural Source |
|---|---|---|
| Normal Month OPEX | $2,728.62 USD total pilot spend: farm connectivity $920.00, center links $645.00, drone campaign average $583.33, AWS cloud workloads $580.29 (within $650.00 budget ceiling) | [Pilot costs, sections 1 and 7](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/pilot-costs.md#1-executive-summary-and-scope); ASM-230, ASM-250 |
| Harvest Month OPEX | $10,666.92 USD total pilot spend: farm connectivity $920.00, center links $645.00, drone harvest campaign $8,500.00, AWS cloud workloads $601.92 (within $700.00 budget ceiling) | Same, sections 1, 5, 7 |
| One Farm's Hardware CAPEX | $370.00 USD per farm: Crop node $175.00, Drying node $180.00, mounting kit $15.00. Total 200 farms CAPEX: $74,000.00 USD. Monthly recurring connectivity: $920.00 USD across 400 nodes | Same, section 3; ASM-231 |
| Commercial Drone Campaign | $8,500.00 USD per harvest campaign; 7 annual campaigns (4 harvest, 3 off-harvest, 1,105 total flights) = $45,250.00 USD annual operator contract | Same, section 5; ADR-002, ASM-238 |
| Harvest Invocations | 108,270 invocations, 420 model calls, $5.21 USD compute and model spend ($0.00477/1k telemetry evals, $5.164/1k confirmations/verifications, $21.65/1k estimations) | Same, section 6; ASM-169, ASM-237 |
| Key Savings Decisions | 1. VPC endpoints vs Network Firewall and NAT saves $10,856.40/yr net OPEX (ASM-127)<br>2. CloudFront serverless front door vs ALB saves $490.56/yr net OPEX (ASM-155)<br>3. Episode-only Bedrock inference vs all readings saves $632.68/yr net OPEX (ASM-167)<br>*(Total 6 decisions avoid $47,532.88/yr OPEX and $230,000.00 CAPEX)* | Same, section 9; ASM-251, [Architecture, section 15](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#15-decisions-that-lower-or-avoid-cost) |

### Slide 17: Design system (0:30)

| Design Element | Specification & Implementation | Source & Standards |
|---|---|---|
| Brand Assets | Pure SVG vector marks: logo, isotype (coffee bean over Pacific waves), single-ink (`#1A1714`), and negative white versions; 25% clear space, 48 px / 24 px minimum reproduction limits | `aroma-pacifico-design-system` [`brand/`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/tree/main/brand); case statement point 7 |
| Semantic Palettes | 4 Sack status badges: En preparación (`#FBF1DC`/`#5C3D00`), En viaje (`#E3EEFB`/`#0B3A6E`), Aceptado (`#E2F3E6`/`#0F4D22`), Rechazado (`#FBE4E2`/`#7A1610`)<br>5 Crop alert severities: Critical (`#FBE4E2`/`#7A1610`), Caution (`#FBF1DC`/`#5C3D00`), Notice (`#E3EEFB`/`#0B3A6E`), Resolved (`#E2F3E6`/`#0F4D22`), No-Data (`#ECE6DE`/`#1A1714`) | Same, [`tokens/tokens.json`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/tokens/tokens.json); PD-154, ASM-096 |
| Outdoor Usability Rules | OUTDOOR-1 to OUTDOOR-8: minimum 7.0:1 (WCAG Level AAA) relative luminance contrast (48 checked token pairs, 0 failures), 48x48/56x56 px touch targets, high-reflectance light backgrounds (`#FFFFFF`, `#F6F2EC`), redundant icon+text encoding, and `[data-contrast="outdoor"]` 21:1 mode | Same, [`components/`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/tree/main/components), [`tokens/contrast-report.md`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/tokens/contrast-report.md) |
| Typography & Base UI | Roboto / Noto Sans system stack; 8-unit spatial system; 15 outline SVG icons (24x24 px, 2 px stroke); buttons, fields, alerts, sack cards, badges | Same, [`components/components.css`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/components/components.css) |
| Applied Across Three Apps | Master design sheet applied to Coffee Grower offline-first PWA, Transporter logistics tracking, and Public Sack Lookup with 4 data groups (origin, dates, status, drying stats) and zero personal data | Same, [`docs/design-system.md`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/docs/design-system.md), [`examples/design-sheet.html`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/examples/design-sheet.html); ASM-096 |

### Slide 18: Close and what stays open (0:30)

| On the slide | Source |
|---|---|
| Three things sustained: connectivity, flight mode, IaC in 100 hours | Slides 5 to 9 and 13 to 14 |
| Open decisions owned by the Federation (clarification session answers, thresholds, drone operator contract RFP validation) | [Architecture, section 17](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#17-open-decisions-for-the-defense) |
| Nothing was applied or deployed; every latency, recovery time and capacity is a design target | Architecture, section 2 |
| Questions | [Defense questions](defense-qa.md) |

## Pending content register

| Slide | Missing content | Source issue | Status / Action when it merges |
|---|---|---|---|
| 14 | Result and evidence of the final validation of the executable plan | aroma-pacifico/aroma-pacifico-roadmap#33 (B13) | PENDING: teammates' work; keep placeholder until B13 merges |
| 16 | Every amount: normal month, harvest month, farm hardware, drone campaign, invocation cost | aroma-pacifico/aroma-pacifico-roadmap#36 (A23) | RESOLVED: incorporated from merged `docs/pilot-costs.md` (PR #44) |
| 17 | The design system and its application to the three apps | aroma-pacifico/aroma-pacifico-roadmap#37 (A24) | RESOLVED: incorporated from merged design system repository (PR #4) |
| 3, 10, 13 | Final diagram exports, if the diagrams repository changes them | aroma-pacifico-diagrams `complete/` | Monitoring; diagrams stable |
| 18 | Answers of the clarification session | PD-005 in the decision log | Open decisions for the defense; owned by the Federation |
