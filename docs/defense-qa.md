# Defense Questions and Short Answers

| Field | Value |
|---|---|
| Roadmap issue | aroma-pacifico/aroma-pacifico-roadmap#38 (A25) |
| Companion files | [Deck overview](final-presentation.md), [Guion de la sustentación](guion-sustentacion.md) |
| Deck annex | Slides after the closing QR show every diagram whole and in detail; the guion maps each annex ID to its slides |

Each answer is meant to be said in about 30 seconds and names the document that holds the detail. The answers repeat what the merged documents of the architecture, infrastructure, modules and design-system repositories record and add no requirement. The owner is the presenter of that topic in the deck, who answers first; the others add. Where a diagram helps, the answer names the annex slide to jump to.

## Architecture and operation

| # | Likely question | Short answer | Owner | Detail |
|---|---|---|---|---|
| 1 | Why AWS as the primary cloud, and what does "prepared second cloud" mean? | Functions, storage and managed inference live together in one Region, `us-east-1`, so we can name where objects leave Colombia, and the team's 28 IaC rules are written for AWS. Azure is prepared for portability and exit, not failover: neutral interfaces, open-format data and a declared export target, with nothing deployed. | SR1 | [ADR-001](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-001-primary-and-second-cloud.md) |
| 2 | What happens to a farm with no signal for more than 24 hours? | The node buffers at most 24 hours, encrypted; older readings are evicted, counted and reported as a gap, and a node silent for more than 24 hours raises a detection. Farms out of coverage use the same node with a satellite bearer. On reconnection the node publishes a live reading first and then drains the buffer, so a late alert is marked as late. | JR1 | [Architecture, section 12](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#12-store-and-forward-and-no-signal-behavior) |
| 3 | The alert must arrive in under 5 minutes. How do you know it does? | It is a design target with a defined indicator, not a measurement: first receipt by push or SMS within 300 seconds of the reading, 95 percent over 28 days (ASM-224). The latency budget spends 210 seconds across seven hops and keeps 90 seconds of margin. | SR2 | [Observability](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/observability.md); annex, no-signal sequence |
| 4 | Why the combined flight mode and not only precision agriculture? | Only combined mode covers the five mandatory services: delimiting and estimating need area flights, and confirming, fumigating and verifying need precision flights. The switch is `crop_alert_raised` then `focus_confirmed`. | SR2 | [ADR-002](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-002-drone-flight-mode-and-governance.md) |
| 5 | Who flies, who authorizes, and what stops an unauthorized spray? | A contracted certified operator flies; a Federation agronomist authorizes each order as a human identity with MFA, and no trigger can authorize. The order state machine only reaches `authorized` with that MFA and only dispatches with a valid pilot permit and an active kit. | SR2 | ADR-002; annex, drone state machines |
| 6 | How does a lost drone or a decommissioned node stop publishing? | The identity is revoked: the device certificate is retired, tokens are invalidated and the API refuses any token issued before the revocation, so the effect does not wait for expiry. | JR1 | [Security and identity, section 10](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/security-and-identity.md) |
| 7 | What does the buyer see, and what do they not see? | Origin, processing dates, status and drying variables, through a separate projection keyed by a random sack code. No farmer identity document and no full trace. | SR2 | [Sack and trip](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/sack-and-trip.md) |
| 8 | How does the pilot scale from 200 to 1,000 farms? | Farms and phones hold no cloud address, so growth adds identities, not subnets; the addressing plan and the ingestion point do not change. | JR1 | [Addressing plan](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/addressing-plan.md) |
| 9 | What are the recovery targets for sack events? | The case statement fixes an RPO of 15 minutes for sack events and an RTO of 4 hours for the public lookup. The design meets them inside one Region across Availability Zones, with five-year retention. | SR2 | [Sack and trip](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/sack-and-trip.md) |
| 10 | What leaves Colombia? | There is no AWS Region in Colombia. Every object and record is stored and processed in `us-east-1`; only screened crop images and alert-opening readings go to the model, and an object that contains a person is not sent. | SR2 | [Inference functions, section 8.2](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/inference-functions.md) |

## Governance

| # | Likely question | Short answer | Owner | Detail |
|---|---|---|---|---|
| 11 | How is the platform governed from day one? | From the organization root: seven service control policies (among them `us-east-1` only, no long-term credentials and production changes only through the pipeline), a tag policy of eight keys of which five split the cost, budgets of USD 650 in a normal month and USD 700 in harvest with alerts at 80 and 100 percent, and an organization trail kept five years. | SR1 | [Landing zone, sections 3 to 7](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/landing-zone.md) |
| 12 | Who can change production? | Only the pipeline. A service control policy limits production changes to it; production applies only the reviewed plan whose fingerprint a second person on the approver list approved, and the job refuses harvest-week daytime except for an incident. | SR1 | [Automation and pipelines](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/automation-and-pipelines.md) |
| 13 | What if a production change is needed in harvest week? | No production change between 05:00 and 18:00 in harvest week, except an incident. The release note records the window, the impact, the approval, the notice to the Federation and how to roll back. | SR1 | Automation and pipelines, sections 3 to 5 and 10; release notes |
| 14 | How do you avoid secrets in the repository and in the state? | Device keys are generated on the device; CI uses GitHub Actions OIDC with no static keys; environments ship `.tfvars.example` with external injection; sensitive values never reach the state in plain text, per ADR-003. The qa end-to-end plan also scans the history and the plan for secrets. | JR2 | [ADR-003](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/adr/adr-003-iac-tool-remote-state-and-pattern-module.md) |

## Infrastructure as code

| # | Likely question | Short answer | Owner | Detail |
|---|---|---|---|---|
| 15 | Why Terraform, and where does the state live? | The team's 28 binding rules are written for Terraform. State lives in an encrypted, versioned bucket per environment with native locking; ADR-003 records the layout and what stays out of the code on purpose. | JR2 | ADR-003 |
| 16 | How does the code map to the diagram? | Thirteen boxes, D01 to D13, one per roadmap task B01 to B13. Eight public modules implement them, each published by tag from v0.1.0 to v0.5.0 and consumed by tag (pc-iac-015), with 131 plan-mode tests in 8 suites. | JR2 | `aroma-pacifico-terraform-modules`; annex, IaC traceability |
| 17 | How are stacks and environments organized? | Four stacks in dependency order: state, network, security and workloads. dev, qa and pdn use the same modules and tags and differ only in their variables file, backend and CIDR. | JR2 | `aroma-pacifico-infrastructure`: `stacks/`, `environments/` |
| 18 | Did you run a plan? Where is the evidence? | Yes, a plan and never an apply. The qa plan runs end to end against the Floci emulator, the four stacks in order, which the faculty advisor accepted as the plan target (pc-iac-028). | JR2 | `aroma-pacifico-infrastructure`, `docs/b13-final-validation.md` |
| 19 | How does CI enforce the rules, and what does Infracost show? | An infrastructure pull request runs 13 checks: a secret scan, per-stack format, validate, lint, security scan and tests, the Floci plan, Infracost and the convention checks; a modules pull request runs 29. Infracost publishes cost before, after and the delta next to the plan. We quote no Infracost figure, because it changes with each pull request; the cost baseline is the cost document. | JR2 | pc-iac-027; `infrastructure-ci.yml`, `infracost.yml` |
| 20 | How do you tear an environment down or roll back? | A rollback is a revert by pull request and a new promotion, so the reviewed plan shows the inverse change. Tearing down runs the stacks in reverse order and the approver reads the destructions first. Tables with data carry `prevent_destroy`, so a plan that would replace them fails, and the state is recoverable from the versioned bucket. | JR2 | `aroma-pacifico-infrastructure`, `docs/cd-pipeline.md`, sections 3 and 7 |

## The 100-hour plan

| # | Likely question | Short answer | Owner | Detail |
|---|---|---|---|---|
| 21 | Why does the infrastructure code fit in 100 hours? | Its scope is what the case statement counts: modules, variables, remote state and an executable plan of one pattern environment. 98 hours in 19 parts, none above 10 hours, with 2 hours of reserve. | JR2 | [100-hour plan](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/iac-plan-100h.md) |
| 22 | How is the work split between the four of you? | SR1 27 hours, SR2 26, JR1 22 and JR2 23. Six tasks are split into module and wiring; nobody exceeds 25 hours a week or 5 a day. | JR2 | 100-hour plan, sections 4.1 and 6.5 |
| 23 | What is the critical path, and what if a task slips? | Two 38-hour chains that share B01, B06a, B03 and B04b; one continues through B09b, B07b and B12, the other through B08 and B05, and both close in B13. The plan ends at hour 38 of 50, on day 8, so a slip has 12 hours of buffer, and the team uses 49 percent of its 200-hour capacity. | JR2 | 100-hour plan, sections 6.2 to 6.5 |
| 24 | What is deliberately not coded? | The landing zone, the 200 farms, the three centers and the functions beyond the pattern environment are designed and diagrammed but not coded, because the case statement counts one pattern environment. ADR-003 lists them. | JR2 | ADR-003; 100-hour plan, section 2 |

## Costs

| # | Likely question | Short answer | Owner | Detail |
|---|---|---|---|---|
| 25 | How much does the pilot cost? | USD 2,707.27 in a normal month and USD 10,638.75 in a harvest month, with USD 82,550 of initial investment. The cloud is the smaller part: USD 558.94 and USD 573.75, under the USD 650 and USD 700 budgets. | SR1 | [Pilot costs, section 1](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/pilot-costs.md) |
| 26 | Why does harvest cost four times more? | The drone campaign, not the cloud: it goes from USD 583.33 to USD 8,500 in the harvest month. AWS rises only USD 14.81, from SMS and inference. | SR1 | Pilot costs, sections 3.2 and 7.1 |
| 27 | What does one farm cost? | USD 370 of hardware once and USD 4.60 a month of connectivity. | SR1 | Pilot costs, section 5 |
| 28 | Where are the savings? | Six decisions: endpoints instead of Network Firewall and NAT, CloudFront instead of a load balancer, the model only when an alert opens, dual hardware with satellite only without signal, contracted drones and on-demand DynamoDB. Together USD 47,532.88 a year and USD 230,000 of avoided investment. | SR1 | Pilot costs, sections 2 and 9; [Architecture, section 15](https://github.com/aroma-pacifico/aroma-pacifico-architecture/blob/main/docs/architecture.md#15-decisions-that-lower-or-avoid-cost) |
| 29 | How do you keep the cost under control after go-live? | Budgets with alerts at 80 and 100 percent, cost tags enforced by the tag policy, and Infracost on every pull request and on the production approval, so every change shows its cost before anyone approves it. | SR1 | Landing zone; pc-iac-027 |

## Rules for answering

Answer the question asked, then name the document. Never present a design target as a measurement, and never state a price or an approval that is not in a merged document. If the question needs a diagram, jump to its annex slide (the table in the guion lists them) and return to the closing slide afterwards.
