# Reviewer Response Quality Gate for the Three-CSUR Split

This file converts the TPEL rejection feedback into mandatory acceptance gates for the CSUR split. Every item remains **Open** until the new manuscript provides a concrete fix, a location, and evidence that the fix was verified against source papers or authoritative criteria.

## Global Rules

- No algorithm label enters a figure, table, or taxonomy without source-level verification.
- No timeline claim is allowed unless the underlying evidence distinguishes algorithm publication year, first PEC adoption year, and publication year of the cited PEC study.
- No future direction is allowed unless it specifies a bottleneck, candidate computing method, validation metric, and deployment scenario.
- No CSUR manuscript may rely on a purely application-domain contribution; the contribution must be a computing taxonomy, design space, benchmark, theory synthesis, or deployment framework.
- Conference and journal evidence must be separated before any readiness conclusion is drawn.

## Reviewer 1: 8 Items

| ID | Reviewer concern | Strict required resolution | Target artifact | Status |
|---|---|---|---|---|
| R1-1 | Introduction and contribution list do not distinguish analytical novelty from existing DRL reviews. | Each CSUR paper must state one non-overlapping analytical contribution: Paper A = deployment-oriented control taxonomy; Paper B = computational design automation taxonomy; Paper C = CPS/PHM decision-making framework. Include a comparison table against existing reviews. | Paper A outline and manuscript seed; later B/C drafts | Open |
| R1-2 | Trend figures are descriptive rather than insightful. | Replace descriptive trend narration with claims about algorithm preference, application maturity, and hardware validation, each backed by evidence-table fields. | Paper A evidence table; revised trend section | Open |
| R1-3 | Individual algorithm descriptions lack structured comparison. | Add comparison axes: action space, policy role, stability mechanism, sample efficiency, online latency, memory cost, verification maturity, and deployment setting. | Paper A taxonomy | Open |
| R1-4 | Too many conference papers; archival maturity is unclear. | Label every work as journal, conference, or other. Conclusions about robustness/practical readiness may use only journal or hardware-validated evidence unless explicitly marked as proof-of-concept. | Paper A evidence table | Open |
| R1-5 | Stability and safety are insufficiently rigorous. | Create a dedicated safety layer covering Lyapunov/safety filters, runtime shielding, constrained optimization, robustness testing, and failure-mode evidence. | Paper A taxonomy and manuscript seed | Open |
| R1-6 | Design, control, and maintenance are too broad in one article. | Split into three manuscripts and prevent overlap by assigning each paper a unique computing contribution and citation scope. | Three-paper roadmap and B/C briefs | Open |
| R1-7 | Future directions are high-level. | Rewrite future directions as actionable research programs with bottleneck, method, metric, and deployment scenario. | Paper A manuscript seed; B/C briefs | Open |
| R1-8 | Recent reviews on DRL for power electronics are missing. | Add a related-review map before drafting: review title, scope, missing gap, and how the new paper differs. | Paper A evidence expansion backlog | Open |

## Reviewer 2: 10 Items

| ID | Reviewer concern | Strict required resolution | Target artifact | Status |
|---|---|---|---|---|
| R2-1 | More state-of-the-art references are needed. | Add a 2024-2026 literature-expansion backlog for safe RL, converter control, HIL, embedded deployment, and multi-agent coordination. | Paper A evidence expansion backlog | Open |
| R2-2 | Lifecycle gap is not synthesized into a unified framework. | Do not use one lifecycle framework for all papers. Paper A must unify control through deployment maturity; Paper B through design-space search; Paper C through health-management decision loops. | Three-paper roadmap; each outline | Open |
| R2-3 | Reviewing RL applications over the years is strange and duplicative. | Quarantine the old timeline. Restore only if evidence supports a non-duplicative maturity narrative. | Paper A classification audit | Open |
| R2-4 | Need to show unique functions of each RL approach across problem areas. | For each algorithm family, explain what decision variable it controls, which converter property it handles, and where it fails. | Paper A taxonomy | Open |
| R2-5 | Control section is hard to follow and needs a summary diagram. | Replace converter-by-converter prose with a summary-first architecture: direct control, hybrid parameter tuning, modulation optimization, coordination, and safety/deployment overlays. | Paper A outline and manuscript seed | Open |
| R2-6 | Maintenance misses cyberattack/fault area and category overlap exists. | Paper C must introduce a corrected PHM taxonomy separating monitoring, diagnosis, prognostics, prescription, and cyber-resilience. | Paper C brief | Open |
| R2-7 | Safety/stability citations are not converter-specific enough. | Add source-level checks for every stability citation; mark non-converter evidence as transferable theory, not direct evidence. | Paper A evidence table | Open |
| R2-8 | Computational efficiency needs offline and online distinction. | Add separate fields for offline training cost, online inference latency, memory footprint, and on-chip adaptation feasibility. | Paper A evidence table and taxonomy | Open |
| R2-9 | RL does not offer universal solutions; theoretical PEC analysis remains important. | Add a "when not to use DRL" and "model-based theory remains necessary" subsection. | Paper A manuscript seed | Open |
| R2-10 | Discussion/future studies need deeper potential solutions. | Convert each future item into a concrete path drawing from control theory, safe RL, embedded systems, and CPS validation. | Paper A manuscript seed | Open |

## Reviewer 3: 4 Items

| ID | Reviewer concern | Strict required resolution | Target artifact | Status |
|---|---|---|---|---|
| R3-1 | Position DRL within other AI-based methods. | Add a decision matrix comparing DRL with supervised learning, imitation learning, MPC-assisted learning, Bayesian optimization, evolutionary search, and classical adaptive control. | Paper A taxonomy; Paper B brief | Open |
| R3-2 | Clarify academic vs industrial adoption and field barriers. | Add deployment-readiness levels: simulation only, HIL, real-time controller, embedded prototype, field/industrial evidence. | Paper A evidence table | Open |
| R3-3 | Section III conclusions lack references in text. | Every synthesis claim must cite evidence-table rows or a verified group of rows. | Paper A manuscript seed | Open |
| R3-4 | Paper is text-heavy and needs concept figures. | Plan figures for control-role taxonomy, deployment-readiness ladder, safety stack, and offline/online computation pipeline. | Paper A outline | Open |

## Reviewer 4: 4 Items

| ID | Reviewer concern | Strict required resolution | Target artifact | Status |
|---|---|---|---|---|
| R4-1 | Many algorithm classifications are wrong. | Audit all labels for DQN, DDQN, DDPG, TD3, SAC, PPO, MADDPG, MAPPO, MASAC, and A3C against source papers. Old Fig. 5 and Table II/IX labels are invalid until rechecked. | Paper A classification audit and evidence table | Open |
| R4-2 | Timeline stages are not convincing. | Remove early/intermediate/mainstream stage claims unless redefined as "algorithm origin" versus "PEC adoption" with verified dates. | Paper A classification audit | Open |
| R4-3 | Many cited papers are conference or low quality. | Weight evidence by venue maturity and validation maturity. Proof-of-concept papers may identify emerging ideas but may not support strong performance claims. | Paper A evidence table | Open |
| R4-4 | Future directions are vague and technically questionable. | Remove unsupported solution buzzwords. Explain each method in the correct context, why it applies, and how it would be evaluated. | Paper A manuscript seed | Open |

## Immediate Consequences for Paper A

Paper A must be rebuilt from the evidence table rather than from the old control section. The old control text can supply candidate references and examples, but it cannot supply verified classifications. The old timeline and algorithm distribution figures are quarantined until the audit proves they are correct.

## Paper A Draft Progress Log

### 2026-05-23 Method and Synthesis Scaffold

The ACM draft now contains concrete first-pass fixes for several reviewer gates. These fixes remain draft-level until the full evidence table is completed and every cited source is PDF/source verified.

| Gate | Draft-level fix added | Location |
|---|---|---|
| R1-1 | Paper A now states a distinct analytical contribution: a deployment-centered control taxonomy for DRL in real-time converter control. | `paper_a_control_deployment/acm_draft/paper_a_control_deployment.tex`, title, abstract, taxonomy section |
| R1-3 / R2-4 | Algorithm discussion is reframed through control interface, action space, safety mechanism, deployment maturity, computation stage, and coordination scope before any algorithm counts. | Table `deployment-taxonomy` |
| R1-4 / R4-3 | Source tiers separate preferred-core journals, preferred conferences, supplementary high-quality evidence, adjacent context, and exclude-by-default sources. | Section `Review Method and Evidence Policy`; Table `review-protocol` |
| R1-5 / R2-7 | Safety and stability are promoted from vague limitations to taxonomy dimensions and a dedicated section. | Sections `Deployment-Centered Taxonomy` and `Safety, Stability, and Certification` |
| R1-7 / R2-10 / R4-4 | Future directions are rewritten as bottleneck, candidate computing method, validation metric, and deployment scenario. | Table `research-agenda` |
| R2-3 / R4-2 | Timeline claims are not allowed unless evidence distinguishes publication dates from actual PEC adoption/deployment maturity. | Table `evidence-use-rules` |
| R2-8 / R3-4 | Computational efficiency is separated into offline training, online inference, memory footprint, adaptation cost, and hardware target. | Sections `Computational Efficiency`; Tables `deployment-taxonomy`, `evidence-use-rules`, `reproducibility-checklist` |
| R3-2 | Deployment maturity is explicitly coded as simulation, real-time digital simulation, HIL, embedded prototype, or field-relevant evidence. | Tables `deployment-taxonomy`, `review-protocol`, `evidence-use-rules` |
| R4-1 | The five highest-risk red/yellow papers now have conservative source-resolution rules, with conditional papers excluded from algorithm statistics. | Table `red-yellow-resolution` |

Remaining high-priority unresolved gates before a full CSUR draft:

1. Add a related-review comparison map to address R1-8.
2. Expand 2024-2026 source search and verify recent safe RL, HIL, embedded deployment, and multi-agent control literature for R2-1.
3. Add a DRL-versus-other-AI decision matrix for R3-1.
4. Complete PDF/source verification for all preferred-core journal rows, not only the first five red/yellow papers.
5. Build concept figures from the current tables after the taxonomy stabilizes.
