# Final Presentation: Slide Deck

| Field | Value |
|---|---|
| Status | Agent draft, rehearsal pending |
| Roadmap issue | aroma-pacifico/aroma-pacifico-roadmap#38 (A25) |
| Length | 20 minutes, 24 script slides, four presenters by role; the deck has 31 pages with the cover, the team slide, four part dividers and the questions slide |
| Companion files | [Speaker script](speaker-script.md), [Defense questions and short answers](defense-qa.md) |
| Slide file | [`deck/aroma-pacifico-sustentacion.pptx`](../deck/aroma-pacifico-sustentacion.pptx) (Spanish, with speaker notes) and its [PDF export](../deck/aroma-pacifico-sustentacion.pdf); see the [README](../README.md#the-slide-file) |
| Source of requirements | `docs/case/case-statement.pdf` |

This deck is the slide content only. Each slide lists its on-screen text, its source in the architecture repository and its time. The slide specifications incorporate the visual design system of A24 (brand assets, typography, outdoor contrast rules, and palette) and the pilot cost model of A23. Every figure on a slide is either a figure of the case statement, arithmetic on those figures, or a design target recorded in the decision log. None is a measurement. Content that depends on a task that has not merged is marked `PENDING` and names its source issue (specifically B13 final validation); the register at the end of this file lists open dependencies.

## Time plan

| Part | Presenter | Slides | Minutes | Cumulative | Topic |
|---|---|---|---|---|---|
| 1 | SR1 | 1 to 5 | 4:00 | 4:00 | What changes since 2020, the architecture, the security base and the governance of the platform and of change |
| 2 | SR2 | 6 to 9 | 3:45 | 7:45 | Connectivity: farm, transporter, drone link, collection center and port, with and without signal |
| 3 | JR1 | 10 to 13 | 3:15 | 11:00 | Flight mode, pest-to-fumigation flow, inference and observability |
| 4 | JR2 | 14 to 24 | 9:00 | 20:00 | Why the infrastructure code fits 100 hours, the plan by role and its status, modules, stacks and CI, controlled change, costs, design system and close |

The case statement asks the team to sustain three things: the connectivity (part 2), the flight mode (part 3) and why the infrastructure code fits 100 hours (part 4). The lead asked for the most weight on costs, governance, the 100-hour plan and the infrastructure code (comment of 2026-11-11 on the A25 issue), so part 4 has 9 minutes, governance has its own slide in part 1, and parts 1 to 3 are shorter than in the first draft.

## Before slide 1: cover and team (no own time)

The cover carries the title, the date and the four presenters with their names, deck role and job role. The team slide follows it: a header strip ("Universidad Icesi", "Sustentación técnica" and the page number), four portrait cards of equal size with a 3:4 crop, the name in two lines (first names, then surnames) in the brand primary color and the role below, in presentation order. Each presenter says their name and role; the time counts inside slide 1. The part dividers then show the presenter's name and role with the part time. Names and photos live only in the deck (`deck/content.yaml` and `deck/assets/team/`).

## Part 1: Framing and base (SR1, 4:00)

### Slide 1: The pilot and the defense (0:35)

| On the slide | Source |
|---|---|
| Aroma Pacífico: 2026 update of the coffee traceability pilot, Cauca, Huila and Tolima | Case statement, "Contexto" |
| 200 farms, 3 collection centers, 60 transporters, delivery at the port of Buenaventura | Case statement, "Cifras del piloto" |
| Plan-only delivery: design, modular Terraform, no apply, no deployment | [Architecture, section 1](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#1-executive-summary) |
| Agenda: four parts by role, three things we sustain (connectivity, flight mode, IaC in 100 hours) | [Architecture, section 16](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#16-defense-guide) |

### Slide 2: What changes since 2020 (0:50)

| 2020 assumption | 2026 design | Source |
|---|---|---|
| Data coverage on most farms; device publishes straight to the ingestion point | Every flow has an exit protocol, a local buffer of at most 24 hours and a defined behavior without signal | [Architecture, section 12](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#12-store-and-forward-and-no-signal-behavior) |
| Collection center and port without LAN or WAN | Segmented LAN per center with a 100 Mbps WAN; no Federation equipment at the port | [Architecture, section 5](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#5-point-3-network-and-connectivity) |
| A mobile network generation that may be switched off | No dependency on a switched-off generation; LTE-based bearer, satellite IP bearer for farms out of coverage | [Connectivity](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/connectivity.md) |
| 2020 prices and services | Not a valid quote; cost document is new | A23 (see slides 20 to 22) |

Closing line of the slide: the 2020 record of what is kept and what is retired is [section 13 of the architecture document](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#13-the-2020-pilot-what-is-kept-changed-and-retired).

### Slide 3: The architecture at a glance (0:50)

Full-slide image: the complete diagram, `aroma-pacifico-diagrams/complete/architecture.png` ([SVG](https://github.com/aroma-pacifico/aroma-pacifico-diagrams/blob/main/complete/architecture.svg) for the print version). A second image, `aroma-pacifico-diagrams/complete/architecture-iac.png`, is used on slide 14.

| Callout on the image | Text |
|---|---|
| Cloud | AWS primary, one Region (`us-east-1`), Azure prepared only as an undeployed export target (ADR-001) |
| Accounts | One organization, five member accounts: security, network, production, test, development |
| Edge | Two solar nodes per farm, drone ground station, transporter and farmer apps, a LAN per center |
| Boxes | D01 to D13 mark what the infrastructure code builds |

### Slide 4: Governance and security base (0:35)

| Topic | On the slide | Source |
|---|---|---|
| Governance | Service control policies, tag policy, budgets and organization trail applied from the root; five transversal tags carry the cost split | [Landing zone](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/landing-zone.md) |
| Identities | Separate identities and least privilege for six roles; MFA for collection-center operator, drone operator, platform operator and the agronomist | [Security and identity](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/security-and-identity.md) |
| Security module | Merged `modules/security` (box D06, B06): eight rotated customer-managed keys (CMKs), staff Cognito pool with TOTP MFA, field pool passwordless, seven role groups | `aroma-pacifico-terraform-modules` PR #12 |
| Data & Revocation | TLS in transit, CMKs at rest, 5-year retention; immediate revocation IAM role for lost drones or decommissioned nodes | [Security and identity, section 10](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/security-and-identity.md#10-revocation-flow-for-a-compromised-farm-node-or-drone); PR #12 |

### Slide 5: Governance of the platform and of change (1:10)

| Topic | On the slide | Source |
|---|---|---|
| Landing zone (A08) | Seven SCPs from the organization root: no leaving the organization, `us-east-1` only, protect the trail, no long-term credentials, no member-account root, mandatory cost tags, production only through the pipeline; tag policy with eight keys, five of them cost allocation tags; budgets USD 650 normal and USD 700 harvest with alerts at 80 and 100 percent; organization trail with 5-year retention | [Landing zone, sections 3, 5, 6 and 7](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/landing-zone.md) |
| Rules in CI | 28 binding pc-iac rules; CI checks the machine-checkable ones on every pull request (fmt, validate, tflint, Trivy, tests, Floci plan, Infracost) | `aroma-pacifico-ai-agents` `standards/iac-rules/` |
| Review gates | Trunk-based development, Conventional Commits verified per pull request, a reviewer agent from a different AI provider, no apply outside the approved CD path | `AGENTS.md`; `.github/workflows/pr-conventions.yml` |
| Decisions | Decision log with 185 ASM and 107 PD entries (292); ADR-001 cloud, ADR-002 flight mode, ADR-003 IaC, ADR-004 drone orchestrator | [Decision log](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/decision-log.md), [ADRs](https://github.com/aroma-pacifico/aroma-pacifico-architecture/tree/main/docs/adr) |

## Part 2: Connectivity (SR2, 3:45)

### Slide 6: One rule for every flow (1:00)

Statement on the slide: identity, not address. Farms, phones and drones hold no cloud address; they authenticate by certificate or token, so growing from 200 to 1,000 farms adds identities, not subnets.

| Fact | Value | Source |
|---|---|---|
| Telemetry protocol | MQTT over TLS, X.509 device certificate, QoS 1, to the regional IoT endpoint | Architecture, section 12 |
| Crop reading cadence | Every 4 hours, 6 readings a day; drying every hour while a lot is open | Case statement |
| Alert latency | Under 5 minutes with a delivery route (design target, first receipt on push or SMS) | Case statement; ASM-224 |
| Addressing | Centers 10.41, 10.42, 10.43; AWS supernet 10.80.0.0/13, one /16 per environment (`dev` 80, `qa` 81, `pdn` 82) | [Addressing plan](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/addressing-plan.md) |

### Slide 7: Without signal (1:00)

| Actor | Buffer | Behavior without signal | Released when |
|---|---|---|---|
| Farm node | Encrypted ring buffer, at most 24 hours | Keeps reading; on reconnection publishes a live reading first, then drains oldest first; alert raised at drain, marked delayed | Each reading is acknowledged |
| Farm out of coverage | Same node | Same MQTT over a satellite IP bearer; no new radio base, no weekly visit | Next contact |
| Transporter app | Encrypted outbox, at least 7 days of positions | Position every 5 minutes; custody events never evicted; positions thinned to one per 15 minutes before any drop | API confirms persistence |
| Drone | Mission preloaded at the municipal seat or the center | Flight proceeds; record stays in the buffer; no fumigation closure without the record | Persistence receipt for each object |

Source: [architecture, section 12](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#12-store-and-forward-and-no-signal-behavior). The numeric values beyond the case statement are assumptions ASM-073 to ASM-079.

### Slide 8: Collection center and port (0:55)

| Item | Design | Source |
|---|---|---|
| LAN | One pattern, three centers; seven zones with the reserved /24 blocks, one SSID per client zone; visitors have no route to logistics or management | [Collection-center network](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/collection-center-network.md) |
| WAN | 100 Mbps symmetric; two IPsec tunnels to a Transit Gateway with a cellular backup | Architecture, section 1 |
| Capacity | At an assumed 50 percent active clients at the peak: 68 Mbps down and 17 up needed, against 90 planned (ASM-084, ASM-085) | Architecture, section 5 |
| Port | No Federation equipment; the platform records only the delivery event, sent by the transporter app | [Connectivity, section 10](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/connectivity.md#10-port-of-buenaventura) |

### Slide 9: Firewall and what we did not buy (0:50)

| On the slide | Source |
|---|---|
| Perimeter firewall per center and a cloud firewall; policy tables with source, destination, port, action and permanent or temporary | [Firewall policy](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/firewall-policy.md) |
| No NAT gateway and no network firewall appliance in the cloud; AWS services reached through endpoints | Architecture, section 15 |
| Data tier has no route to the internet and is never reachable from a center | Architecture, section 5 |
| Transition line to part 3: the same link logic decides how a drone mission survives a dropped link | Slide 10 |

## Part 3: Flight mode and workloads (JR1, 3:15)

### Slide 10: Combined flight mode (1:00)

| Mode | Services | Why |
|---|---|---|
| Area | Delimit the plot, estimate the harvest | Steady state of every farm; one flight per harvest for the estimate |
| Precision | Confirm the alert, fumigate the focus, verify the same plot | Entered only through a crop alert |
| Switch | `crop_alert_raised` then `focus_confirmed` | Only a confirmed focus can lead to a fumigation order |

Statement on the slide: only the combined mode covers the five mandatory services, none of which can be replaced by another. A contracted certified operator flies; a Federation agronomist authorizes each fumigation as a human identity with MFA. Source: [ADR-002](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-002-drone-flight-mode-and-governance.md).

### Slide 11: From alert to closed case (0:50)

Image: the pest-to-fumigation sequence and state machine from `aroma-pacifico-diagrams` (drone fumigation sequence, merged in the diagrams repository). Text under the image:

| Gate | Rule |
|---|---|
| Order cannot leave | No plot polygon, or no closed flight record |
| Fumigation stays open | Until the verification object arrives and is persisted |
| Authorization | Human identity only; no trigger executes it |
| Link drops over the plot | Mission already loaded; record published on restore |

Source: [drone service](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/drone-service.md).

### Slide 12: Event-driven inference (0:40)

| On the slide | Source |
|---|---|
| Four functions, one per trigger: telemetry batch, focus confirmation, verification, harvest estimate | [Inference functions](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/inference-functions.md) |
| Codified inference pattern: merged `modules/inference-functions` (box D10, B10) with SQS queue, dead-letter queue, least-privilege IAM role, and Lambda invoking Amazon Nova Pro via Bedrock | `aroma-pacifico-terraform-modules` PR #14 |
| Standardized result contract: functions persist timestamp (`result_at`), confidence, and source object (`source`); zero persistent compute (no EC2, ECS, or provisioned concurrency) | Same; case statement, Part E |
| Data leaving Colombia: stored and processed in `us-east-1`; only screened crop images and alert-opening readings reach the model | Architecture, section 1 |
| Drone capability orchestrator (event-driven): the custom bus and its rules route each mission event to its capability, per-function queues buffer it with retries and a dead-letter queue, and the mission state machine in DynamoDB is the source of truth; no central workflow engine in the pilot | [ADR-004](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-004-drone-capability-orchestration.md), merged with status Proposed; the orchestrator is labelled in `complete/architecture.svg` and `flows/inference-functions.svg` (G05) |

### Slide 13: Observability and the two SLOs (0:45)

| SLO | SLI | Objective (design target) | Source |
|---|---|---|---|
| Crop alert delivery | Share of alert openings whose first receipt arrives within 300 seconds of the reading | 95 percent over a rolling 28 days | ASM-224 |
| Sack lookup availability | Share of lookup requests answered without a 5XX or 429 | 99.5 percent over a rolling 28 days | ASM-225 |

Below the table, one line for the five detections of the case statement (silent nodes over 24 hours, undelivered alerts, flights without a persisted record, fumigations without closure, failed invocations that did not change state) and one line for the two dashboards, operational and cost. Source: [observability](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/observability.md). Nothing is deployed: these are definitions, and their tests are future work.

## Part 4: Infrastructure as code, change, cost and close (JR2, 9:00)

### Slide 14: Why the code fits 100 hours (1:00)

Image: `architecture-iac.png`, the diagram with boxes D01 to D13.

| What the code covers | What it deliberately leaves out |
|---|---|
| Terraform, one tool whose 28 binding rules already exist | The landing zone (designed, not coded) |
| One pattern environment planned (`qa`), one stack per domain | The 200 farms and the three centers |
| Eight reference modules, tagged up to `v0.4.0`: network, state backend, base security (B06, PR #12), farm (B08), telemetry ingestion, inference functions (B10, PR #14), firewall rules and collection-center association (B05, PR #21); 142 plan-mode test runs in 17 test files | The other three inference functions, the sack lookup module, application code |
| Remote state: one encrypted, versioned, natively locked S3 bucket per environment | CodeDeploy deployments and manual cluster infrastructure |
| Environment isolation and secrets (B03/PR #6): `environments/{dev,qa,pdn}/*.tfvars.example`, external injection via GitHub OIDC and `TF_VAR_*`, no plaintext secrets in repository or state (ADR-003) | Observability, release notes, costs, design system and this defense (separate deliverables outside the 100 hours) |

Sources: [ADR-003](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-003-iac-tool-remote-state-and-pattern-module.md), [100-hour plan, section 2](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/iac-plan-100h.md#2-scope-what-counts-in-the-100-hours), `aroma-pacifico-infrastructure` PR #6, and `aroma-pacifico-terraform-modules` PRs #12, #14 and #21 (tag `v0.4.0`).

### Slide 15: The 100-hour plan in numbers (0:50)

| Check | Value | Source |
|---|---|---|
| Tasks | 13 issues, B01 to B13, split into 19 parts, each with owner, order, dependency and diagram box | Plan, section 4.1 |
| Total | 98 hours booked; 2 hours reserve | Plan, section 9 |
| Largest task | 10 hours (limit is 10) | Plan, section 9 |
| Capacity | 4 people at 5 hours a day for 10 working days is 200 hours; 49 percent booked | Plan, section 6.1 |
| Finish | Working hour 38 of 50, Day 8 of 10 | Plan, section 9 |
| Top risks | Plan evidence without an AWS account: the faculty advisor accepted the Floci emulator as the plan target (pc-iac-028), and PD-019 stays open until B13; feature behavior not yet re-checked live (PD-200) | Plan, section 8 |
| Done on the roadmap board (9) | B01 to B06, B08, B10 and B11: repositories, remote state, variables, network, collection-center association, security, farm, inference and CI with a plan against the Floci emulator and Infracost | Roadmap board on 2026-11-11; `aroma-pacifico-infrastructure` PRs #4, #9 to #12 |
| In progress on the roadmap board (3) | B07 and B09: modules published (`firewall-rules` `v0.3.0`, `telemetry-ingestion` `v0.4.0`), stack wiring (part b) open; B12: CD pipeline and runbook merged, issue still open | Roadmap board; `aroma-pacifico-infrastructure` PRs #14 and #19 |
| Result of the final validation (B13) | PENDING: source aroma-pacifico/aroma-pacifico-roadmap#33 | not merged |

### Slide 16: Workload by role and week (0:50)

| Role | Parts | Week 1 | Week 2 | Total |
|---|---|---|---|---|
| SR1 | B03, B06a, B06b, B10, B13a | 21 h | 6 h | 27 h |
| SR2 | B07a, B07b, B09a, B09b, B12 | 16 h | 10 h | 26 h |
| JR1 | B01, B04a, B04b, B11a, B11b | 18 h | 4 h | 22 h |
| JR2 | B02, B05, B08, B13b | 10 h | 13 h | 23 h |
| Team | 19 parts | 65 h | 33 h | 98 h |

Side cards: six tasks split into a and b (B04, B06, B07, B09, B11, B13; a is the module or first delivery, b the stack wiring or extension); nobody above 25 hours a week or 5 a day; the planning workbook `Planeacion_Esfuerzo_AromaPacifico.xlsx` estimates 298 hours in 42 tasks for the whole project, 98 of them infrastructure code, inside the 100-hour cap. Sources: [100-hour plan, sections 4.1 and 6.5](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/iac-plan-100h.md); workbook, Resumen sheet.

### Slide 17: Module catalog (1:10)

| Module | First tag | Box | What it creates |
|---|---|---|---|
| `network` | `v0.1.0` | D04 | VPC, eight tier subnets, route tables, network ACLs, endpoints, rejected-traffic flow log |
| `security` | `v0.1.0` | D06 | Rotated KMS keys, Cognito pools and groups, service and revocation IAM roles |
| `inference-functions` | `v0.1.0` | D10 | SQS queue with dead-letter queue, event source mapping, Lambda, least-privilege role, logs |
| `farm` | `v0.2.0` | D08 | IoT thing, certificate from a CSR and its policy attachment, `FarmId` tag |
| `state-backend` | `v0.3.0` | D02 | Versioned, KMS-encrypted S3 bucket with public access blocked |
| `firewall-rules` | `v0.3.0` | D07 | Security groups, prefix lists, endpoint policies, WAF web ACL |
| `collection-center-association` | `v0.4.0` | D05 | Customer gateway, VPN, Transit Gateway attachment and accepter, center prefix list |
| `telemetry-ingestion` | `v0.4.0` | D09 | IoT policy and topic rule, DynamoDB table, error queue, ingestion logs |

Callout: public repository, name prefix, no provider or backend blocks, no accounts; 17 test files and 142 plan-mode test runs. No `v0.5.0` tag exists. Source: `aroma-pacifico-terraform-modules` tags and module READMEs; pc-iac-015.

### Slide 18: Stacks and the CI pipeline (1:10)

| Stack | Tagged modules it consumes |
|---|---|
| `state-backend` | `state-backend` `v0.3.0` |
| `network` | `network` `v0.3.0`, `collection-center-association` `v0.4.0` |
| `security` | None wired yet |
| `workload` | None wired yet |

Right half: verbatim CI output from `main` at `1adf80a` (2026-11-11): Floci plan `state-backend` qa 8 to add; `network` qa 163 to add; `network` pdn 167 to add; `security` and `workload` qa no changes; `terraform test` 16 passed in `network` and 3 in `state-backend`. Callout: an infrastructure pull request runs 13 checks (secret scan; per stack fmt, init, validate, tflint, Trivy and `terraform test`; the Floci plan; Infracost; three convention checks); a modules pull request runs 29. Source: `aroma-pacifico-infrastructure` `stacks/`, `.github/workflows/`, runs on `main` and the checks of PR #19.

### Slide 19: Controlled change and release notes (0:40)

| On the slide | Source |
|---|---|
| Pull request gates, saved `qa` plan, `pdn` applies only the reviewed saved plan after a named human approval | [Automation and pipelines](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/automation-and-pipelines.md) |
| No production change between 05:00 and 18:00 in harvest week, except an incident | Case statement, "Automatización y cambio" |
| Two release note templates, application and infrastructure, each with one completed example; both state what changes, the window, impact, approval, notice to the Federation and rollback | [Release notes](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/release-notes/README.md) |
| The examples are fictional and claim no approval or notice | Same |

### Slide 20: Cost (0:40)

| Cost Domain | On the slide (exact figures from cost document) | Architectural Source |
|---|---|---|
| Normal Month OPEX | $2,707.27 USD total pilot spend: farm connectivity $920.00, center links $645.00, drone campaign average $583.33, AWS cloud workloads $558.94 (within $650.00 budget ceiling) | [Pilot costs, sections 1 and 7](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/pilot-costs.md#1-executive-summary-and-scope); ASM-230, ASM-250 |
| Harvest Month OPEX | $10,638.75 USD total pilot spend: farm connectivity $920.00, center links $645.00, drone harvest campaign $8,500.00, AWS cloud workloads $573.75 (within $700.00 budget ceiling) | Same, sections 1, 5, 7 |
| One Farm's Hardware CAPEX | $370.00 USD per farm: Crop node $175.00, Drying node $180.00, mounting kit $15.00. Total 200 farms CAPEX: $74,000.00 USD. Monthly recurring connectivity: $920.00 USD across 400 nodes | Same, section 3; ASM-231 |
| Commercial Drone Campaign | $8,500.00 USD per harvest campaign; 7 annual campaigns (4 harvest, 3 off-harvest, 1,105 total flights) = $45,250.00 USD annual operator contract | Same, section 5; ADR-002, ASM-238 |
| Harvest Invocations | 108,270 invocations, 420 model calls, $5.21 USD compute and model spend ($0.00477/1k telemetry evals, $5.164/1k confirmations/verifications, $21.65/1k estimations) | Same, section 6; ASM-169, ASM-237 |
| Key Savings Decisions | 1. VPC endpoints vs Network Firewall and NAT saves $10,856.40/yr net OPEX (ASM-127)<br>2. CloudFront serverless front door vs ALB saves $490.56/yr net OPEX (ASM-155)<br>3. Episode-only Bedrock inference vs all readings saves $632.68/yr net OPEX (ASM-167)<br>*(Total 6 decisions avoid $47,532.88/yr OPEX and $230,000.00 CAPEX)* | Same, section 9; ASM-251, [Architecture, section 15](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#15-decisions-that-lower-or-avoid-cost) |

### Slide 21: Cost breakdown (1:00)

| Domain (USD) | Investment | Normal month | Harvest month |
|---|---|---|---|
| Hardware of 200 farms | 74,000.00 | 920.00 | 920.00 |
| 3 collection centers | 8,550.00 | 645.00 | 645.00 |
| Drone campaign | 0.00 | 583.33 | 8,500.00 |
| AWS cloud | 0.00 | 558.94 | 573.75 |
| Pilot total | 82,550.00 | 2,707.27 | 10,638.75 |

Second table, AWS by service (normal / harvest): Route 53 Resolver 182.70; Transit Gateway 110.50; VPN to the 3 centers 109.50; observability 60.72; interface endpoints 58.90; S3 and KMS 15.80; WAF, DynamoDB, CloudFront and IoT 15.57; SMS 4.95 / 14.85; event compute and AI 0.30 / 5.21; total 558.94 / 573.75. Harvest raises the cloud by USD 14.81. Callout: per farm USD 370 of hardware once and USD 4.60 a month of connectivity; the cost document gives no cost per sack. Source: [pilot costs, sections 1, 3.2 and 7.1](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/pilot-costs.md); ASM-230 to ASM-237.

### Slide 22: Cost decisions, method and Infracost (0:50)

| Decision | Avoided per year (USD) | Avoided investment (USD) |
|---|---|---|
| Endpoints instead of Network Firewall and NAT | 10,856.40 | 0.00 |
| CloudFront and Lambda instead of an ALB | 490.56 | 0.00 |
| Model only when an alert opens | 632.68 | 0.00 |
| Dual-mode hardware, satellite only without signal | 34,560.00 | 50,000.00 |
| Contracted drones, no own fleet | 0.00 | 180,000.00 |
| On-demand DynamoDB | 993.24 | 0.00 |
| Total | 47,532.88 | 230,000.00 |

Side cards: method (published `us-east-1` rates and November 2026 catalogs, 1 USD = 4,100 COP, every assumption with an ID and kept apart from the calculation); to re-check (AWS prices under PD-200, equipment and flight quotes under PD-230); Infracost on every pull request (CLI v2 compares base and head per stack and module and publishes before, after and delta next to the plan, per pc-iac-027). The deck quotes no Infracost figure: the estimates live in each run summary. Sources: [pilot costs, sections 1, 2 and 9](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/pilot-costs.md); ASM-251; `infracost.yml` in `aroma-pacifico-infrastructure` and `aroma-pacifico-terraform-modules`.

### Slide 23: Design system (0:20)

| Design Element | Specification & Implementation | Source & Standards |
|---|---|---|
| Brand Assets | Pure SVG vector marks: logo, isotype (coffee bean over Pacific waves), single-ink (`#1A1714`), and negative white versions; 25% clear space, 48 px / 24 px minimum reproduction limits | `aroma-pacifico-design-system` [`brand/`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/tree/main/brand); case statement point 7 |
| Semantic Palettes | 4 Sack status badges: En preparación (`#FBF1DC`/`#5C3D00`), En viaje (`#E3EEFB`/`#0B3A6E`), Aceptado (`#E2F3E6`/`#0F4D22`), Rechazado (`#FBE4E2`/`#7A1610`)<br>5 Crop alert severities: Critical (`#FBE4E2`/`#7A1610`), Caution (`#FBF1DC`/`#5C3D00`), Notice (`#E3EEFB`/`#0B3A6E`), Resolved (`#E2F3E6`/`#0F4D22`), No-Data (`#ECE6DE`/`#1A1714`) | Same, [`tokens/tokens.json`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/tokens/tokens.json); PD-154, ASM-096 |
| Outdoor Usability Rules | OUTDOOR-1 to OUTDOOR-8: minimum 7.0:1 (WCAG Level AAA) relative luminance contrast (48 checked token pairs, 0 failures), 48x48/56x56 px touch targets, high-reflectance light backgrounds (`#FFFFFF`, `#F6F2EC`), redundant icon+text encoding, and `[data-contrast="outdoor"]` 21:1 mode | Same, [`components/`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/tree/main/components), [`tokens/contrast-report.md`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/tokens/contrast-report.md) |
| Typography & Base UI | Roboto / Noto Sans system stack; 8-unit spatial system; 15 outline SVG icons (24x24 px, 2 px stroke); buttons, fields, alerts, sack cards, badges | Same, [`components/components.css`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/components/components.css) |
| Applied Across Three Apps | Master design sheet applied to Coffee Grower offline-first PWA, Transporter logistics tracking, and Public Sack Lookup with 4 data groups (origin, dates, status, drying stats) and zero personal data | Same, [`docs/design-system.md`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/docs/design-system.md), [`examples/design-sheet.html`](https://github.com/aroma-pacifico/aroma-pacifico-design-system/blob/main/examples/design-sheet.html); ASM-096 |

### Slide 24: Close and what stays open (0:30)

| On the slide | Source |
|---|---|
| Three things sustained: connectivity, flight mode, IaC in 100 hours | Slides 6 to 10 and 14 to 18 |
| Open decisions owned by the Federation (clarification session answers, thresholds, drone operator contract RFP validation) | [Architecture, section 17](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#17-open-decisions-for-the-defense) |
| Open in the team: B07, B09 and B12 in progress, final validation B13 pending | Roadmap board |
| Nothing was applied or deployed; every latency, recovery time and capacity is a design target | Architecture, section 2 |
| Questions | [Defense questions](defense-qa.md) |

## Pending content register

| Slide | Missing content | Source issue | Status / Action when it merges |
|---|---|---|---|
| 15 | Result and evidence of the final validation of the executable plan | aroma-pacifico/aroma-pacifico-roadmap#33 (B13) | PENDING: issue open and in Backlog on the board on 2026-11-11; the deck shows it as pending and states no result |
| 15 | CI pipeline with an executable plan | aroma-pacifico/aroma-pacifico-roadmap#31 (B11) | RESOLVED: gates, Floci plan job and Infracost estimate merged in `aroma-pacifico-infrastructure` PRs #9 to #12; Done on the board |
| 15 | CD pipeline with production approval | aroma-pacifico/aroma-pacifico-roadmap#32 (B12) | OPEN: pipeline (PR #14) and runbook (PR #19) merged, but the issue is In progress on the board; the deck counts it under "En curso: 3" |
| 15 | Pattern firewall rules and the pattern module of ADR-003 | aroma-pacifico/aroma-pacifico-roadmap#27 (B07), aroma-pacifico/aroma-pacifico-roadmap#29 (B09) | OPEN: both In progress on the board, modules published and stack wiring pending; the deck counts them under "En curso: 3" |
| 14, 15, 18 | Association between the environment and a collection center | aroma-pacifico/aroma-pacifico-roadmap#25 (B05) | RESOLVED: module merged in `aroma-pacifico-terraform-modules` PR #21 (tag `v0.4.0`) and stack wiring in `aroma-pacifico-infrastructure` PR #4; Done on the board |
| 12 | Event-driven drone capability orchestrator (ADR-004) | `aroma-pacifico-architecture` PR #50, `aroma-pacifico-diagrams` PR #23 | RESOLVED: both merged (G05 Done); ADR-004 has status Proposed and the deck says "ADR-004, propuesto"; slide 12 and slide 3 crops re-rendered with the labelled orchestrator |
| 20 to 22 | Every amount: normal month, harvest month, farm hardware, drone campaign, invocation cost, breakdown by domain and service, cost decisions | aroma-pacifico/aroma-pacifico-roadmap#36 (A23) | RESOLVED: incorporated from merged `docs/pilot-costs.md` (PRs #44 and #46, reconciled totals) |
| 22 | Infracost before, after and delta figures | `aroma-pacifico-infrastructure` and `aroma-pacifico-terraform-modules` cost workflows | OPEN by design: the figures live in each CI run summary and change per pull request; the deck states the mechanism and quotes no figure |
| 23 | The design system and its application to the three apps | aroma-pacifico/aroma-pacifico-roadmap#37 (A24) | RESOLVED: incorporated from merged design system repository (PR #4) |
| 3, 6 to 9, 11, 12, 14, 19 | Final diagram exports, if the diagrams repository changes them | aroma-pacifico-diagrams | RESOLVED for this deck: crops rendered from the merged SVG exports; rerun `deck/build_deck.py --refresh-assets` if they change |
| 24 | Answers of the clarification session | PD-005 in the decision log | Open decisions for the defense; owned by the Federation |
