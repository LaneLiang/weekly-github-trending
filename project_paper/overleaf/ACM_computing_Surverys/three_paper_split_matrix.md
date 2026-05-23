# Three-CSUR Split Matrix

## Decision

Proceed with three CSUR-oriented manuscripts that share the original topic of deep reinforcement learning for power electronic converters, but do not share the same survey contribution.

| Paper | Working title | Computing contribution | Reused seed material | Submission readiness |
|---|---|---|---|---|
| A | Deep Reinforcement Learning for Real-Time Control of Power and Energy Conversion Systems: A Survey of Safety, Deployment, and Coordination | Deployment-centered taxonomy for learning-based real-time control, organized by control role, safety mechanism, sim-to-real maturity, embedded implementation, and coordination architecture. | `055_control2.tex`, `023_background.tex`, selected `024_timeline.tex`, selected `06_future.tex` | Primary CSUR target |
| B | Learning-Based Design Automation for Power Electronic Converters: A Survey of Graph Search, Reinforcement Learning, and Constraint-Aware Optimization | Computational design automation taxonomy for topology search, graph generation, constraint-aware optimization, and multi-objective design-space exploration. | `032_design_new.tex`, selected `023_background.tex`, selected design figures/tables | Second-stage CSUR reserve |
| C | Sequential Decision-Making for Predictive Maintenance in Converter-Dense Cyber-Physical Energy Systems: A Survey | CPS/PHM decision-making framework for monitoring, diagnosis, prognostics, prescriptive maintenance, cyber-resilience, and uncertainty-aware scheduling. | `05_maintenance.tex`, selected `06_future.tex` | Long rebuild before CSUR |

## Non-Overlap Contract

- Paper A studies online operation and deployment of learned control policies.
- Paper B studies offline and design-time computational search over converter structures, parameters, and objectives.
- Paper C studies health-state inference and maintenance decisions over converter-dense cyber-physical systems.
- Shared DRL background must be short and customized for each paper.
- Figures, taxonomies, contribution lists, and future directions must be distinct.

## Recommended Order

1. Finish Paper A evidence table and classification audit.
2. Draft Paper A CSUR outline and manuscript seed.
3. Expand Paper A literature and only then rewrite in LaTeX.
4. Start Paper B after Paper A taxonomy is stable.
5. Start Paper C after adding CPS/PHM and cyber-resilience literature.

