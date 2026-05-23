# Paper A Related-Review Comparison Map

This map addresses reviewer gate R1-8: Paper A must cite recent review papers and explain why the new CSUR manuscript is not another descriptive aggregation of DRL applications in power electronic converters.

## Comparison Table

| Review | Source status | Main scope | Useful for Paper A | Limitation relative to Paper A |
|---|---|---|---|---|
| Zhao, Blaabjerg, and Wang, "An Overview of Artificial Intelligence Applications for Power Electronics," IEEE TPEL, 2021 | Preferred-core review | Broad AI applications in power electronics, including design, control, and condition monitoring | Establishes that AI in power electronics is already a mature review topic and that control is a major application area | Not focused on DRL, real-time deployment, source-level algorithm verification, or CSUR-style computing taxonomy |
| Chen et al., "A Review on the Applications of Reinforcement Learning Control for Power Electronic Converters," IEEE TIA, 2024 | Adjacent high-quality review | RL control strategies by converter topology, sim-to-real methods, design considerations, and future prospects | Required comparator for RL control in PECs and sim-to-real discussion | Still organized primarily around converter/topology applications; does not enforce a verified evidence protocol for algorithm labels and deployment-readiness statistics |
| Zhang et al., "Review of online learning for control and diagnostics of power converters and drives," RSER, 2023 | Supplementary high-quality review | Online learning for condition monitoring, fault detection, stability assessment, and control | Useful for online learning, diagnostics/control boundary, and experimental implementation perspective | Broader online-learning scope; not specific to DRL real-time converter control and not centered on safety/deployment/coordination taxonomy |
| Ye et al., "An overview of reinforcement learning for power electronic converters," RSER, 2026 | Supplementary high-quality review | RL across topology derivation, parameter design, and control implementation | Important comparator for the three-paper split because it covers lifecycle stages similar to the rejected TPEL review | Too broad for Paper A; motivates separating control/deployment from Paper B design automation and Paper C health-management decision-making |
| Rajamallaiah et al., "Deep Reinforcement Learning for Power Converter Control," IEEE OJPEL, 2025 | Supplementary high-quality review | DRL control applications categorized by converter topology, objective, algorithm, and implementation framework | Closest direct comparator for DRL converter-control applications and challenges | Paper A must differ by using evidence-gated classification, deployment maturity, safety mechanisms, computational stages, and coordination architecture as the main synthesis axes |

## Paper A Differentiation Claim

Paper A's novelty is not that it is the newest list of DRL-for-converter-control papers. Its contribution is a computing-oriented synthesis of how learned policies enter real-time converter-control loops, how safety and stability are enforced, how simulation results become deployable controllers, how offline and online computation differ, and how coordination scales across converter-dense cyber-physical energy systems.

## Evidence Rule

Related reviews can be cited to position the manuscript and identify gaps. They cannot be used to classify primary papers unless the primary source is separately verified in the Paper A evidence table.

## Web-Verified Source Notes

- Zhao et al. 2021 details verified through CiNii/Crossref metadata: IEEE TPEL 36(4), 4633-4658, DOI `10.1109/TPEL.2020.3024914`.
- Chen et al. 2024 details verified through EurekaMag metadata: IEEE TIA 60(6), 8430-8450, DOI `10.1109/TIA.2024.3435170`.
- Zhang et al. 2023 details verified through ScienceDirect and DTU/KTH metadata: RSER 186, Article 113627, DOI `10.1016/j.rser.2023.113627`.
- Ye et al. 2026 details verified through ScienceDirect metadata: RSER 228, Article 116591, DOI `10.1016/j.rser.2025.116591`.
- Rajamallaiah et al. 2025 details verified through DOAJ metadata: IEEE OJPEL 6, 1769-1802, DOI `10.1109/OJPEL.2025.3619673`.
