# Batch 3: Entries S-Z -- Nature-Journal-Level Reference Audit

**Audit Date**: 2026-05-23
**Methodology**: nature-citation (source hierarchy: Crossref/DOI metadata -> Publisher pages -> Full text/abstract -> Secondary databases)
**Auditor**: Actor Agent, Batch 3 of 4

---

## Per-Entry Audit

### S Entries (7)

| Key | DOI OK? | Authors OK? | Algorithm Match? | Support Grade | Issues |
|-----|---------|-------------|-------------------|---------------|--------|
| `schulman2017proximal` | YES (arXiv:1707.06347, verified) | YES (Schulman, Wolski, Dhariwal, Radford, Klimov -- all confirmed) | N/A (foundational DRL algorithm paper) | **Strong** | None. Widely-cited PPO paper. Tex claim: "PPO is an on-policy method that builds on TRPO and constrains policy updates to a trust region" -- accurate. |
| `sutton2018reinforcement` | N/A (ISBN book, no DOI) | YES (Sutton and Barto, 2nd ed. MIT Press) | N/A (textbook) | **Strong** | None. The standard RL textbook. Tex claim: "For a comprehensive treatment of RL foundations" -- appropriate reference. |
| `sanchez2020tinyml` | YES (IEEE CAS Mag, verified) | YES (Sanchez-Iborra and Skarmeta, both confirmed) | N/A (survey) | **Background** | None. Tex claim: "The emerging TinyML paradigm provides a reference framework for deploying learned models on microcontroller-class devices" -- accurate. Background support for embedded deployment discussion. |
| `schenke2021deep` | YES (IEEE OJIES, verified) | YES (Schenke, Maximilian and Wallscheid, Oliver -- both confirmed) | MATCH (DQN-based direct torque control for PMSM) | **Strong** | None. Tex claim: "demonstrated a DQN-based direct torque controller for permanent magnet synchronous motors" -- accurate. Adjacent domain (motor drives). |
| `stapelberg2020survey` | YES (SACJ, verified) | **NO -- Author first name wrong.** Bib has "Stapelberg, Jacques" but actual author is "Belinda Stapelberg". "Jacques" is incorrect. | N/A (survey) | **Background** | **CRITICAL: Author name error**. Bib lists "Stapelberg, Jacques" -- correct first name is "Belinda". Malan's name is correct. Tex claim: "surveys of benchmarking frameworks" -- accurate description. |
| `silver2014deterministic` | YES (ICML 2014, verified via ACM DL 10.5555/3044805.3044850) | YES (Silver, Lever, Heess, Degris, Wierstra, Riedmiller -- all confirmed) | N/A (foundational DRL algorithm) | **Strong** | None. Foundational DPG paper. Tex claim: "DPG algorithm extends the deterministic policy gradient" -- accurate. |
| `schulman2015trust` | YES (arXiv:1502.05477 / ICML 2015, verified) | **NO -- Author order wrong.** Bib order: Schulman, Levine, Abbeel, Jordan, Moritz. Actual paper order: Schulman, Levine, Moritz, Jordan, Abbeel (ICML 2015 proceedings page). | N/A (foundational DRL algorithm) | **Strong** | **Author order error**: Abbeel and Moritz are swapped in the bib relative to the published paper. Jordan is also misplaced. Correct order from ICML 2015: Schulman, Levine, Moritz, Jordan, Abbeel. |

### T Entries (7)

| Key | DOI OK? | Authors OK? | Algorithm Match? | Support Grade | Issues |
|-----|---------|-------------|-------------------|---------------|--------|
| `tang2020reinforcement` | YES (IEEE TIE, verified) | YES (Tang, Hu, Xiao, Chen, Huang, Chen, Blaabjerg -- all confirmed) | MATCH (Q-learning for TPS modulation efficiency optimization) | **Strong** | None. Tex claim: "tabular Q-learning for modulation-mode selection in DAB converters" -- accurate. |
| `tang2021deep` | YES (IEEE TEC, verified, early access 2021, print 2022) | YES (Tang, Hu, Zhang, Cao, Hou, Li, Chen, Blaabjerg -- all confirmed) | MATCH (DDPG for DAB TPS efficiency optimization) | **Strong** | Minor: Bib key uses 2021 (early-access year), print in vol.37 (2022). Bib note explains this. Acceptable. |
| `tang2022deep` | YES (IEEE TIE, verified, online 2022, print 2023) | YES (Tang, Hu, Cao, Hou, Li, Li, Chen, Blaabjerg -- all confirmed) | MATCH (TD3 for variable-frequency TPS control) | **Strong** | None. |
| `tang2021artificial` | YES (IEEE TPEL, verified) | YES (Tang, Hu, Cao, Hou, Li, Chen, Blaabjerg -- all confirmed) | MATCH (DDPG for minimum reactive power control using harmonic analysis) | **Strong** | None. Cited in tex at line 258 as part of DAB series. |
| `traue2020toward` | YES (IEEE TNNLS, verified, online 2020, print 2022) | YES (Traue, Book, Kirchgaessner, Wallscheid -- all confirmed) | MATCH (Gym-electric-motor RL environment toolbox) | **Partial** | Adjacent domain (motor drives, not DC-DC converters). Tex acknowledges this as "adjacent domain" and uses it as an example of RL environment standardization. Appropriate as background/analogy support. |
| `tobin2017domain` | YES (IEEE IROS 2017, verified) | YES (Tobin, Fong, Ray, Schneider, Zaremba, Abbeel -- all confirmed) | N/A (sim-to-real, not PE-specific) | **Strong** | None. Tex claim: "Domain randomization was originally developed in the robotics community for visual transfer" -- accurate. |
| `tan2018sim` | YES (RSS 2018, verified) | YES (Tan, Zhang, Coumans, Iscen, Bai, Hafner, Bohez, Vanhoucke -- all confirmed) | N/A (sim-to-real, not PE-specific) | **Strong** | None. Tex claim: "extended with system identification to build more accurate simulators for sim-to-real transfer of agile locomotion" -- accurate. |

### V Entries (2)

| Key | DOI OK? | Authors OK? | Algorithm Match? | Support Grade | Issues |
|-----|---------|-------------|-------------------|---------------|--------|
| `van2016deep` | YES (AAAI 2016, verified) | YES (van Hasselt, Guez, Silver -- all confirmed) | N/A (foundational DRL algorithm) | **Strong** | None. Double DQN paper. Tex claim: "Double DQN" extension listed -- accurate. |
| `vazquez2022artificial` | YES (IEEE TIE, verified) | **NO -- MAJOR author list errors.** Bib lists: Vazquez, Marino, Zafra, Penalosa, Andres, Franquelo (6 authors). Actual authors (7): Sergio Vazquez, **Daniel L. Marino** (not David), Eduardo Zafra, **M.D. Valdes Pena** (not Manuel Valdes Penalosa), **Juan J. Rodriguez-Andina** (missing), Leopoldo G. Franquelo, **Milos Manic** (missing). "Andres, Raul" in bib is a fabricated author -- does not appear in the actual paper. | N/A (supervised ANN, not RL-based -- bib classifies this correctly as non-RL) | **Partial** | **CRITICAL -- MULTIPLE AUTHOR ERRORS**: (1) "Marino, David" should be "Marino, Daniel L."; (2) "Penalosa, Manuel Valdes" is garbled, should be "Valdes Pena, M.D." or "Pena, Maria Dolores Valdes"; (3) "Andres, Raul" is FABRICATED -- no such author exists on this paper; (4) MISSING authors: Juan J. Rodriguez-Andina and Milos Manic. **This bib entry appears to have been compiled from corrupted metadata and contains at least one fabricated author name.** Tex accurately notes this is a "supervised ANN" approach (non-RL) for FCS-MPC weighting factor tuning. |

### W Entries (6)

| Key | DOI OK? | Authors OK? | Algorithm Match? | Support Grade | Issues |
|-----|---------|-------------|-------------------|---------------|--------|
| `wei2015reinforcement` | YES (IEEE TIE, verified) | YES (Wei, Zhang, Qiao, Qu -- all confirmed) | MATCH (Q-learning for MPPT of wind energy systems) | **Background** | Adjacent domain (wind energy MPPT, not DC-DC converter control). Tex claim: "early tabular Q-learning for wind MPPT" -- accurate. Background support for value-based method history. |
| `weber2023steady` | YES (IEEE Access, verified) | YES (Weber, Schenke, Wallscheid -- all confirmed) | MATCH (IASA method for steady-state error compensation in RL-based power electronic control) | **Strong** | None. Tex claim: "steady-state error compensation for RL-based control of power electronic systems" -- accurate description of the IASA method. |
| `wu2021innovative` | YES (IEEE EI2 2021, verified via IEEE Xplore 9713634) | YES (Wu, Tian, Jia, Meng, Shi, Zhao, Yan -- all confirmed) | MATCH (DDPG for DAB DC bus voltage stabilization) | **Strong** | None. Conference paper. Bib note documents previous ghost DOI replacement -- the current DOI is verified correct. |
| `wang2016sample` | YES (arXiv:1611.01224 / ICLR 2017, verified) | YES (Wang, Bapst, Heess, Mnih, Munos, Kavukcuoglu, de Freitas -- all confirmed) | N/A (foundational DRL -- ACER) | **Background** | None. Tex claim: "sample-efficient actor-critic methods such as ACER, which combine experience replay with off-policy corrections" -- accurate. Background support for efficiency discussion. |
| `wan2024safety` | YES (IEEE TIE, verified) | YES (Wan, Xu, Dragicevic -- all confirmed) | MATCH (SAC with MPC-based safety policy for VSC control) | **Strong** | None. Tex claim: "safety-enhanced self-learning framework that enables safe online RL on a physical two-level voltage source converter" -- accurate. |
| `wu2025deep` | YES (IEEE/CAA JAS, verified) | YES (Wu, Zhang, Fan, Shi, Guan -- all confirmed) | MATCH (DDPG with Lyapunov-constrained deep dynamics model for grid-forming converters) | **Strong** | Adjacent domain (grid-forming converters). Tex claim: "Lyapunov-constrained DDPG framework for deep synchronization control of grid-forming converters" -- accurate. |

### Y Entries (4)

| Key | DOI OK? | Authors OK? | Algorithm Match? | Support Grade | Issues |
|-----|---------|-------------|-------------------|---------------|--------|
| `ye2024deep` | YES (IEEE TPEL, verified) | YES (Ye, Guo, Wang, Zhang -- all confirmed) | MATCH (DDPG for SIMO DC-DC converter) | **Strong** | None. Tex claim: "DDPG-based controller for a single-inductor multiple-output (SIMO) DC-DC converter" -- accurate. |
| `ye2026overview` | YES (RSER, verified, DOI prefix 2025, volume 228 = 2026) | YES (Ye, Xuan, Guo, Liu, Wang, Zhang, Iu -- all confirmed) | N/A (survey) | **Strong** | Bib key uses 2026 (journal vol. year), DOI has 2025 prefix (early access). This is acceptable and consistent with journal conventions. |
| `yu2022surprising` | YES (arXiv:2103.01955 / NeurIPS 2022, verified) | YES (Yu, Velu, Vinitsky, Gao, Wang, Bayen, Wu -- all confirmed) | N/A (foundational MARL -- MAPPO benchmark study) | **Strong** | None. Tex claim: "MAPPO extends PPO to the multi-agent setting" -- accurate. |
| `ye2025soft` | YES (IEEE JESTIE, verified via UWA repository) | YES (Ye, Zhao, Guo, Zhu, Guo, Liu, Wang, Zhang, Iu -- all confirmed, 9 authors) | MATCH (SAC for SIDO DC-DC converter) | **Strong** | None. Tex claim: "extended this approach to a single-inductor dual-output (SIDO) converter using an SAC-based controller" -- accurate. |

### Z Entries (14)

| Key | DOI OK? | Authors OK? | Algorithm Match? | Support Grade | Issues |
|-----|---------|-------------|-------------------|---------------|--------|
| `zhao2021overview` | YES (IEEE TPEL, verified) | YES (Zhao, Blaabjerg, Wang -- all confirmed) | N/A (survey/overview) | **Strong** | None. Tex claim: "Zhao, Blaabjerg, and Wang surveyed artificial intelligence applications across the full power-electronics lifecycle" -- accurate. |
| `zhang2023online` | YES (RSER, verified) | YES (Zhang, Izquierdo Gomez, Xu, Dragicevic -- all confirmed) | N/A (survey) | **Strong** | None. Tex claim: "covered online learning for control and diagnostics of power converters and drives from a broader machine-learning perspective" -- accurate. |
| `zandi2023voltage` | YES (Eng. App. of AI, verified) | YES (Zandi and Poshtan -- both confirmed) | MATCH (RL for direct switch control of DC-DC converters) | **Strong** | None. Tex claim: "explored direct switch control for DC-DC converters using RL" -- accurate. |
| `zeng2022autonomous` | **CONFLICT** -- Bib DOI 10.1109/TPEL.2022.3212345 may be valid (IEEE doc 9935265), but alternate source claims DOI 10.1109/TPEL.2022.3218900. Unable to resolve conflict definitively without direct IEEE access. | YES (Zeng, Pou, Sun, Mukherjee, Xu, Gupta, Dong -- all confirmed) | MATCH (MA-TD3 for ISOP-DAB IVS and TPS modulation) | **Strong** | **DOI conflict across sources**: Bib uses 10.1109/TPEL.2022.3212345; xjtlu.edu.cn reports 10.1109/TPEL.2022.3218900 for the same paper. The bib DOI was confirmed by one search finding the IEEE Xplore page (document 9935265), but a second search returned a different DOI. Recommend direct IEEE Xplore resolution. Bib note says "DOI verified via IEEE Xplore staging document 9793712" but that document ID differs from the paper's page (9935265) -- this needs reconciliation. |
| `zeng2022multiagent` | YES (IEEE TPEL, verified) | YES (Zeng, Pou, Sun, Maswood, Dong, Mukherjee, Gupta -- all confirmed) | MATCH (MADRL for ISOP-DAB output current sharing) | **Strong** | None. Bib note documents DOI verification. Letters paper (5 pages). |
| `zeng2023deep` | YES (IEEE TIE, corrected DOI verified) | YES (Zeng, Pou, Sun, Li, Liang, Xia, Mukherjee, Gupta -- all confirmed) | MATCH (MADRL with SAC for DC SST distributed control) | **Strong** | Bib note documents previous DOI correction (from 10.1109/TIE.2023.3279277 to 10.1109/TIE.2023.3294584). Current DOI confirmed correct. |
| `zhao2020sim` | YES (IEEE SSCI 2020, verified) | YES (Zhao, Queralta, Westerlund -- all confirmed) | N/A (survey) | **Strong** | None. Tex claim: "The gap between simulation and hardware is well-known in robotics and autonomous driving" -- accurate reference. |
| `zhang2021multi` | YES (Springer, verified) | YES (Zhang, Yang, Basar -- all confirmed) | N/A (handbook chapter / survey) | **Strong** | None. Tex claim: "For a broader treatment of MARL theories and algorithms, the reader is referred to Zhang et al." -- appropriate. |
| `zhang2021machine` | YES (IEEE OJIA, verified, arXiv 2021, journal 2023) | YES (Zhang, Wallscheid, Porrmann -- all confirmed) | N/A (survey) | **Strong** | Bib key uses 2021 (arXiv year), journal published 2023. Bib note documents this. Acceptable for citation stability. |
| `zhang2023data` | YES (IEEE TSTE, verified) | YES (Zhang, Guo, Magnusson, Pilawa-Podgurski, Xu -- all confirmed) | MATCH (Safe-guaranteed MADDPG for inverter decentralized control) | **Partial** | Adjacent domain (distribution systems, not DC-DC converters). Tex acknowledges this as "adjacent domain: distribution systems" and uses it as an example of safety-constrained multi-agent coordination. Appropriate as conceptual support. |
| `zhou2023drl` | YES (IEEE JESTPE, verified) | YES (Zhou, Zhang, Cui, Lin, Dong -- all confirmed) | MATCH (SAC-based parameter self-configuration for nonsmooth control in DC microgrids) | **Strong** | Bib key uses 2023 (online year), print in vol.12 (2024). Bib note documents this. Acceptable. |
| `zeng2025physics` | YES (IEEE TTE, verified) | YES (Zeng, Xiao, Liu, Liang, Rodriguez, Zou, Zhang, Pou -- all confirmed) | MATCH (Physics-informed deep transfer RL for ISOP-DAB in electric aircraft) | **Strong** | None. Tex claim: "physics-informed deep transfer RL method that transfers knowledge from a simulation-trained ISOP-DAB system to a physical experimental system" -- accurate. |
| `zeng2025multi` | YES (IEEE TPEL, verified) | YES (Zeng, Jiang, Konstantinou, Pou, Zou, Zhang -- all confirmed) | MATCH (Easy Transfer RL for multi-objective grid-following converter control) | **Strong** | None. Tex claim: "achieved a 96.4% training reduction when transferring multi-objective grid-following controllers across converters" -- accurate. |
| `zandi2023voltage_quasi` | YES (Control Engineering Practice, verified) | YES (Zandi and Poshtan -- both confirmed) | MATCH (RL-based direct switch control for quasi-Z-source converter under CPL) | **Strong** | None. Tex claim: "extended this RL-based direct switching approach to quasi-Z-source converters under constant power load conditions" -- accurate. |

---

## Batch Statistics

| Metric | Count |
|--------|-------|
| **Total entries** | 40 |
| **DOI verified** | 38 / 40 (95.0%) |
| **DOI conflict/uncertain** | 1 (zeng2022autonomous) |
| **DOI not applicable (ISBN/book)** | 1 (sutton2018reinforcement) |
| **Authors verified correct** | 37 / 40 (92.5%) |
| **Authors with issues** | 3 (stapelberg2020survey, schulman2015trust, vazquez2022artificial) |
| **Algorithm match confirmed** | 21 / 21 PE application papers (100%) |
| **Algorithm N/A (foundational/theory/survey)** | 19 |
| **Strong support** | 32 / 40 (80.0%) |
| **Partial support** | 4 / 40 (10.0%) |
| **Background support** | 4 / 40 (10.0%) |
| **Contradictory** | 0 / 40 (0%) |
| **Metadata-only candidate** | 0 / 40 (0%) |

---

## Critical Issues Found

### Issue 1 (CRITICAL): `vazquez2022artificial` -- Multiple Author Errors Including Fabricated Name

The bib entry for `vazquez2022artificial` contains **severe author list errors**:

**Bib author list (6 authors):**
```
Vazquez, Sergio and Marino, David and Zafra, Eduardo and
Penalosa, Manuel Valdes and Andres, Raul and Franquelo, Leopoldo G.
```

**Actual author list (7 authors, confirmed via DBLP, IEEE, multiple sources):**
1. Sergio Vazquez
2. Daniel L. Marino
3. Eduardo Zafra
4. M.D. Valdes Pena (Maria Dolores Valdes Pena)
5. Juan J. Rodriguez-Andina
6. Leopoldo G. Franquelo
7. Milos Manic

**Specific errors:**
- (a) "Marino, David" -> should be "Marino, Daniel L." (wrong first name)
- (b) "Penalosa, Manuel Valdes" -> garbled name; should be "Valdes Pena, M.D." or "Pena, Maria Dolores Valdes"
- (c) "Andres, Raul" -> **FABRICATED AUTHOR**; no such person appears on this paper. Likely a corruption of "Rodriguez-Andina, Juan J."
- (d) MISSING: Juan J. Rodriguez-Andina (actual author)
- (e) MISSING: Milos Manic (actual author)

**Recommendation**: Replace the entire author field with the verified author list from DBLP or IEEE Xplore.

### Issue 2 (CRITICAL): `stapelberg2020survey` -- Wrong First Name

Bib has `Stapelberg, Jacques` but the correct author is `Stapelberg, Belinda`. "Jacques" is incorrect. Verified via SACJ journal page, Semantic Scholar, and arXiv preprint.

### Issue 3: `schulman2015trust` -- Author Order Error

Bib author order: Schulman, Levine, **Abbeel**, **Jordan**, **Moritz**
Actual ICML 2015 paper order: Schulman, Levine, **Moritz**, **Jordan**, **Abbeel**

Three authors are out of order (Abbeel, Jordan, Moritz).

### Issue 4: `zeng2022autonomous` -- DOI Conflict

Bib DOI: `10.1109/TPEL.2022.3212345`
Alternate source (xjtlu.edu.cn): `10.1109/TPEL.2022.3218900`

Both resolve to the same paper title. The bib DOI was confirmed by one search finding the IEEE Xplore page (document 9935265), but a second search returned a conflicting DOI. Additionally, the bib note says "DOI verified via IEEE Xplore staging document 9793712" but the IEEE page is document 9935265 -- this internal note discrepancy needs reconciliation. **Recommendation**: Verify directly on IEEE Xplore with institutional access.

---

## Minor Issues / Observations

1. **Adjacent-domain entries properly flagged**: `traue2020toward`, `wei2015reinforcement`, `zhang2023data`, `wu2025deep` are correctly classified as adjacent-domain references. The tex text appropriately acknowledges their domain boundaries.

2. **Year vs. key discrepancies are documented**: `tang2021deep` (key 2021, print 2022), `zhang2021machine` (key 2021 arXiv, journal 2023), `zhou2023drl` (key 2023, print 2024), `ye2026overview` (key 2026, DOI 2025 prefix) -- all have explanatory notes. These are acceptable per citation conventions.

3. **All PE application papers have correct algorithm labels**: DDPG, TD3, SAC, Q-learning, MADDPG, MATD3, and MAPPO labels all match the actual papers.

4. **No ghost DOIs found** in S-Z batch. All DOIs resolve to the correct papers (with the zeng2022autonomous conflict noted above).

---

## Summary of Batch 3

Batch 3 covers 40 entries (keys S through Z). Overall quality is high, with 80% strong support grade and no contradictory or metadata-only entries. However, **three entries have author errors** that must be corrected before journal submission, with `vazquez2022artificial` being the most severe (fabricated author name + missing real authors). One DOI conflict needs resolution for `zeng2022autonomous`.
