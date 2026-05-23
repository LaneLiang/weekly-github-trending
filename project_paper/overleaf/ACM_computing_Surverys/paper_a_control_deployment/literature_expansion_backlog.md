# Paper A Literature Expansion Backlog

This backlog records candidate additions found during the first web-assisted expansion pass. Items are **not accepted evidence** until verified through the publisher page, DOI, or source PDF.

## Candidate Additions Matching Preferred Venues

| Candidate | Venue fit | Why it matters for Paper A | Current verification status |
|---|---|---|---|
| Wan and Xu, "Stability-Guided Reinforcement Learning Control for Power Converters: A Lyapunov Approach" | TIE, preferred-core | Directly addresses R1-5/R2-7/R4-4 on rigorous safety and stability. Search result reports TIE 72(7):7553-7562, 2025, DOI `10.1109/TIE.2024.3522491`. | Candidate only; verify via IEEE Xplore/DOI/source PDF |
| Zeng et al., "Multi-Objective Controller Design for Grid-Following Converters With Easy Transfer Reinforcement Learning" | TPE, preferred-core | Useful for transfer learning, online implementation, reduced training burden, and controller scalability. Search result reports TPE 40(5):6566-6577, 2025, DOI `10.1109/TPEL.2025.3525500`. | Candidate only; verify via IEEE Xplore/DOI/source PDF |
| Schenke, Haucke-Korber, and Wallscheid, safe RL torque-control paper | TPE, preferred-core | Strong fit for safe online training, edge-computing training pipeline, FPGA hard real-time inference, and real-world experiments. University page reports TPE publication and DOI `10.1109/TPEL.2023.3303651`. | Candidate only; verify exact title/authors/pages from IEEE Xplore |
| Liu et al., "Event-Driven Based Reinforcement Learning Predictive Controller Design for Three-Phase NPC Converters Using Online Approximators" | TPE, preferred-core | Strong fit for online approximators, switching-frequency reduction, robustness to uncertainties, and predictive-control integration. University repository reports TPE 40(4):4914-4926, 2025, DOI `10.1109/TPEL.2024.3510731`. | Candidate only; verify via IEEE Xplore/DOI/source PDF |

## Related-Review Candidates

These may be needed for the related-review comparison table even if they are not preferred-core evidence for technical claims.

| Candidate | Venue | Use |
|---|---|---|
| Chen et al., "A Review on the Applications of Reinforcement Learning Control for Power Electronic Converters" | IEEE Transactions on Industry Applications, 2024 | Required comparator review for R1-8; use to clarify Paper A's deployment-centered novelty |
| Ye et al., "An overview of reinforcement learning for power electronic converters: Topology derivation, parameter design, and control implementation" | Renewable and Sustainable Energy Reviews, 2026 | Comparator review spanning all lifecycle stages; use to separate Paper A from broader lifecycle surveys |
| "Review of online learning for control and diagnostics of power converters and drives" | Renewable and Sustainable Energy Reviews, 2023 | Comparator for online learning scope; use only in related work, not as primary control evidence |

## Search Rules for the Next Pass

- Search first in TPE, TIE, TCAS-I, TCAS-II, APEC, ECCE, ISSCC, and JSSC.
- Add 2024-2026 papers only if they improve one of these gaps: safety/stability, sim-to-real, hardware/real-time implementation, computational burden, or multi-agent coordination.
- Do not add papers merely to increase citation count.
- Every added source must receive a row in `evidence_table.md` and a venue decision in `current_reference_screening.md`.

