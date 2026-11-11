# Speaker Script

| Field | Value |
|---|---|
| Status | Agent draft, not rehearsed |
| Roadmap issue | aroma-pacifico/aroma-pacifico-roadmap#38 (A25) |
| Deck | [Final presentation](final-presentation.md) |
| Length | 20 minutes over 24 script slides: SR1 4:00, SR2 3:45, JR1 3:15, JR2 9:00 |
| Rehearsal | Not done. The team times a full run and replaces the targets below with the measured times. |

The script is written to be said aloud, in short sentences, roughly 130 words per minute. Speakers adapt the wording; the facts and the references are the fixed part. Each section names the documents the presenter cites out loud, so that the script points to the architecture document, the complete diagram, the observability design, the 100-hour plan, the module catalog, the CI output, the costs and the release notes. Every number is a case-statement figure, arithmetic on one, or a design target; say "design target" and never "measured". Lines marked `PENDING` are placeholders for unmerged deliverables (specifically B13 final validation).

## Cover and team slide (no own time)

While the jury settles, SR1 reads the title and moves to the team slide. Each presenter says their name and role, in presentation order: SR1, SR2, JR1 and JR2. This counts inside the time of slide 1.

## Part 1: SR1 (4:00)

**Slide 1 (0:35).** "Good morning. We present the 2026 update of the Aroma Pacífico coffee traceability pilot: 200 farms in Cauca, Huila and Tolima, three collection centers, 60 transporters and the delivery at Buenaventura. The delivery is plan-only: design, reusable Terraform, cost and this defense. Nothing is applied or deployed; the plan runs against the Floci emulator and CI estimates the cost with Infracost. We sustain the connectivity, the flight mode and why the infrastructure code fits in 100 hours, with the emphasis on governance, plan, code and cost."

**Slide 2 (0:50).** "The 2020 design assumed data coverage on most farms and a device publishing straight to the cloud; the collection center and the port had no network. Now every flow has an exit protocol, a local buffer of at most 24 hours and a defined behavior with no signal. Each center gets a segmented LAN and a 100 megabit WAN, the port gets no equipment, and we do not depend on a mobile generation that the operators switch off. Prices from 2020 are not a valid quote, so the costs are new. The detail is section 13 of the architecture document."

**Slide 3 (0:50).** "This is the complete diagram, in the diagrams repository under complete. AWS is the primary cloud, in one Region, us-east-1; Azure is prepared as an export target and not deployed, which is ADR-001. One organization holds a management account and five member accounts: security, network, production, test and development. At the edge are the farm nodes, the drone ground station, the apps and the center LANs. The badges D01 to D13 mark what the code builds; JR2 comes back to them in part 4."

**Slide 4 (0:35).** "Security is applied from the root. Six roles have separate identities with least privilege, and MFA is required for the center operator, the drone operator, the platform operator and the agronomist. The security module adds eight rotated KMS keys, a Cognito pool with TOTP MFA and seven role groups. Data is encrypted in transit and at rest and kept 5 years, and a lost drone or node loses its identity at once."

**Slide 5 (1:10).** "We also govern the platform and the change. From the organization root we apply seven service control policies: no leaving the organization, us-east-1 only, protect the trail, no long-term credentials, no member-account root user, mandatory cost tags, and production changes only through the pipeline. The tag policy fixes eight keys, and five of them split the cost. The budgets are 650 dollars in a normal month and 700 in harvest, with alerts at 80 and 100 percent, and the organization trail keeps five years. In the code, the 28 pc-iac rules are binding, and CI checks on every pull request the ones a machine can check: format, validation, lint, security scan, tests, a plan against Floci and Infracost. We work trunk-based with verified Conventional Commits, an agent from a different AI provider reviews, and nobody runs apply: the project ends at the plan. Every assumption has an ID: 185 assumptions, 107 pending decisions and four ADRs. SR2 continues with the connectivity."

## Part 2: SR2 (3:45)

**Slide 6 (1:00).** "The rule for every flow is identity, not address. Farms, phones and drones hold no cloud address; they authenticate with a certificate or a token, so the pattern grows from 200 to 1,000 farms by adding identities, not subnets. The farm node publishes MQTT over TLS with an X.509 certificate: crop readings every 4 hours, drying readings every hour while a lot is open. With a delivery route, the alert target is under 5 minutes; it is a design target, not a measurement. The centers use 10.41 to 10.43 and the cloud the supernet 10.80.0.0 slash 13, with no overlap."

**Slide 7 (1:00).** "With no signal nothing is lost. The node keeps an encrypted buffer of at most 24 hours; on reconnection it publishes a live reading first, then drains the buffer, and a late alert is marked as delayed. Farms outside coverage use the same node with a satellite bearer and no new radio base. The transporter app keeps an encrypted outbox, never drops a custody event and thins positions before it drops any. The drone mission is loaded before take-off; if the link falls the flight goes on, and the fumigation cannot close without the record. The full table is section 12 of the architecture document."

**Slide 8 (0:55).** "At the collection center one LAN pattern serves the three departments with two parameters: the center key and the second octet. Seven zones, each with its own SSID, and the visitor zone has no route to logistics or management. The WAN is 100 megabits, with two IPsec tunnels to the Transit Gateway and a cellular backup. With an assumed 50 percent of clients active at the peak, the center needs 68 megabits and we plan 90. At Buenaventura we deploy nothing: the platform records only the delivery event from the transporter app."

**Slide 9 (0:50).** "Every center has a perimeter firewall and the cloud has its own, with policy tables that list source, destination, port, action and validity. The data tier has no route to the internet and no center reaches it. We buy no NAT gateway and no firewall appliance: we reach AWS through endpoints, and the cost document puts that at 10,856 dollars a year saved, net. The same logic of a mission that waits for its link brings us to the drones. JR1 continues."

## Part 3: JR1 (3:15)

**Slide 10 (1:00).** "The flight mode is combined. The case statement has five mandatory services and none replaces another: area mode delimits the plot and estimates the harvest; precision mode confirms the alert, fumigates the focus and verifies the same plot. Only combined mode covers all five. The switch is a pair of persisted events, crop alert raised and then focus confirmed, and only a confirmed focus leads to a fumigation order. A contracted certified operator flies, and a Federation agronomist authorizes each fumigation with MFA. This is ADR-002."

**Slide 11 (0:50).** "This is the path from the alert to a closed case, in eight persisted steps, with four gates. The order cannot leave without the plot polygon and a closed flight record. The fumigation stays open until the verification object arrives. Authorization is human and no trigger can execute it. And if the link drops, the mission is already loaded and the record is published when it returns; the state does not change until the record is persisted."

**Slide 12 (0:40).** "Inference is event-driven: four functions, one per trigger. A drone capability orchestrator coordinates them, with an EventBridge bus and rules and one SQS queue per function; that is ADR-004, merged with status proposed. The inference-functions module implements the pattern with a queue, a dead-letter queue, a least-privilege role and a Lambda calling Amazon Nova Pro. Zero EC2 and zero provisioned concurrency; only screened images and alert-opening readings reach the model."

**Slide 13 (0:45).** "Two SLOs, both design targets. Crop alert delivery: 95 percent of alerts with a first receipt within 300 seconds, over 28 days. Sack lookup: 99.5 percent of requests without a server error or throttle. They are assumptions ASM-224 and ASM-225, because the case statement gives the 5-minute limit but no objective. We detect the five conditions the case names, and there are two dashboards, operational and cost. JR2 closes with the code, the plan and the costs."

## Part 4: JR2 (9:00)

**Slide 14 (1:00).** "Why does the infrastructure code fit in 100 hours? Because it covers what the case statement counts: modules, variables, remote state and an executable plan of one pattern environment, qa. We use Terraform because the 28 binding rules are written for it. State lives in an encrypted, versioned and natively locked bucket per environment, and secrets stay out of the repository and the state, with GitHub Actions OIDC and TF_VAR. The diagram shows the thirteen boxes, D01 to D13, one per task. What we left out is deliberate: the landing zone is designed but not coded, we do not instantiate 200 farms or three centers, and observability, costs, design system and this defense sit outside the 100 hours. That is ADR-003."

**Slide 15 (0:50).** "The plan numbers: thirteen tasks, B01 to B13, in 19 parts; 98 hours booked and 2 in reserve; no task over 10 hours; 49 percent of 200 hours of capacity, finishing at working hour 38 of 50, on day 8. Status today on the roadmap board: nine tasks done, among them CI with a plan against Floci and Infracost, and the collection center association. Three in progress: the firewall rules and the pattern module, whose modules are published and wait for their wiring, and CD, whose pipeline and runbook are merged. The final validation, B13, is PENDING: issue 33 in the roadmap. Do not describe a result."

**Slide 16 (0:50).** "The load is split by role, from section 6.5 of the plan. SR1 carries 27 hours, 21 of them in week 1; SR2 26; JR1 22; and JR2 23, most of it in week 2. Nobody goes over 25 hours a week or 5 a day. Six tasks split in two parts: part a is the module or the first delivery, part b the wiring into the stack or its extension. That is why thirteen tasks make 19 parts. Across the whole project, the planning workbook estimates 298 hours in 42 tasks, of which infrastructure code is 98, inside the 100-hour cap."

**Slide 17 (1:10).** "This is the catalog of the public modules repository. Eight modules, each with its diagram box and the version in which it was first published by git tag: network, security and inference in v0.1.0; farm in v0.2.0; state backend and firewall rules in v0.3.0; collection center association and telemetry ingestion in v0.4.0. Each module takes a name prefix, declares no provider or backend and holds no accounts or client data, because the repository is public. They carry 17 test files with 142 plan-mode runs, and each has an example that CI plans against Floci. The stacks consume them by tag, so a version bump is a reviewed change."

**Slide 18 (1:10).** "The infrastructure repository has four stacks: state-backend, network, security and workload. state-backend consumes the state module v0.3.0, and network consumes network v0.3.0 and collection center association v0.4.0. Security and workload have no modules wired yet, which is why their plan says no changes. On the right is the real CI output on main, commit 1adf80a: the qa plan against Floci proposes 8 resources in state-backend and 163 in network, and 167 in pdn, with nothing to change or destroy. The tests pass: 16 in network and 3 in state-backend. Every infrastructure pull request passes 13 checks: a secret scan; per stack, format, validate, tflint, Trivy and terraform test; the plan against Floci; Infracost; and three convention checks. In the modules repository it is 29, with 16 validations and 8 example plans."

**Slide 19 (0:40).** "Change is controlled. Every pull request passes gates and the qa plan is saved. Production applies only that plan, after a named human approval, and never between 05:00 and 18:00 in harvest week unless there is an incident; in this project everything stops at the plan. The release notes have two templates, application and infrastructure, each with a fictional example."

**Slide 20 (0:40).** "Now the costs, from the pilot cost document. A normal month costs 2,707 dollars and 27 cents, and a harvest month 10,638 dollars and 75 cents. The AWS cloud is only a part: 558.94 and 573.75, under the 650 and 700 ceilings. One farm's hardware costs 370 dollars and a drone campaign 8,500 dollars per harvest month. In harvest, 108,270 invocations and 420 model calls cost 5 dollars and 21 cents. Let us see where it comes from."

**Slide 21 (1:00).** "On the left, cost by domain. The initial investment is 82,550 dollars: 74,000 of hardware for 200 farms and 8,550 for the three centers. Each month the field costs 920 dollars and the centers 645, all year round; what drives the harvest month is the drone campaign, which goes from 583 to 8,500 dollars. On the right, the cloud by service: the private network weighs most, with the DNS resolver, the Transit Gateway and the VPNs. Harvest raises the cloud by only 14 dollars and 81 cents, from SMS and inference. Per farm it is 370 dollars of hardware and 4.60 a month of connectivity. The document does not compute a cost per sack."

**Slide 22 (0:50).** "The method: published us-east-1 rates and November 2026 catalogs, at 4,100 pesos per dollar, with every assumption numbered and kept apart from the calculation, and to be re-checked under PD-200 and PD-230. Six decisions lower the cost: endpoints instead of Network Firewall and NAT, CloudFront instead of a load balancer, the model only when an alert opens, dual-mode hardware with satellite only where there is no signal, contracted drones and on-demand DynamoDB. Together they avoid 47,532 dollars a year and 230,000 of investment. And every change is costed before it merges: Infracost compares base and head of each stack and publishes before, after and delta next to the plan, with no cloud credentials. The Infracost figures live in each run summary; we do not quote them as a measurement."

**Slide 23 (0:20).** "The design system covers the three apps with their own brand, 7 to 1 contrast across the 48 color pairs with no failure, and 48 and 56 pixel touch targets for field sunlight. The public lookup shows four groups of data and no personal data."

**Slide 24 (0:30).** "To close: connectivity is solved flow by flow, with a buffer and a behavior for no signal. The flight mode is combined, with a human authorization. The code fits because its scope is one environment and one pattern. Some decisions are still open and belong to the Federation: the answers of the clarification session, the thresholds and the drone operator contract. In the team, B07, B09 and B12 are in progress and the final validation, B13, is pending. Every latency, recovery time and capacity we gave is a design target. Thank you. We take your questions."

## Rehearsal log

| Run | Date | Total time | Part times (SR1, SR2, JR1, JR2) | Adjustments |
|---|---|---|---|---|
| 1 | not done | not done | not done | not done |

The team fills this table after each rehearsal. The acceptance criterion about a full 20-minute run stays open until it has at least one row with a measured time.
