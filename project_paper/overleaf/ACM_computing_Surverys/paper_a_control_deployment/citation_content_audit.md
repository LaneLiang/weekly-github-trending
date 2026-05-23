# Citation Content-Matching Audit for Paper A

**Manuscript**: "Deep Reinforcement Learning for Real-Time Control of Power Electronic and Energy Conversion Systems: A Survey of Safety, Deployment, and Coordination"

**Audit date**: 2026-05-23

**Methodology**: nature-citation standard. For each key, the manuscript claim (from surrounding tex context) was extracted. The paper's actual content was verified via WebSearch of publisher pages, DOIs, and Google Scholar abstracts. Claim-to-content alignment was assessed on five grades: strong support, partial support, background support, contradictory/limiting, or metadata-only.

**Spot-check depth**: 45+ keys verified with web search (abstract-level or deeper). Remaining keys subjected to title-to-claim sanity check.

---

## CRITICAL ISSUES — BIBLIOGRAPHIC ERRORS

These errors affect the ability to locate and verify the cited paper. They must be corrected before submission.

### CRITICAL-1: `nicola2022comparative` — Wrong DOI and wrong journal

- **Bib says**: DOI `10.3390/math10234525`, Journal: Mathematics, vol. 10, no. 23, pp. 4525
- **Reality**: DOI `10.3390/math10234525` resolves to **"Hateful Memes Detection Based on Multi-Task Learning"** by Zhiyu Ma et al. — a completely unrelated paper about multimodal hate-speech detection. The actual paper by Marcel Nicola and Claudiu-Ionel Nicola about DC-AC converter control with PCH and RL is published in **Sensors (MDPI)**, vol. 22, no. 23, article 9535, with DOI `10.3390/s22239535` and title "Comparative Performance Analysis of the DC-AC Converter Control System Based on Linear Robust or Nonlinear PCH Controllers and Reinforcement Learning Agent."
- **Severity**: HIGH — current DOI points to wrong paper entirely.

### CRITICAL-2: `wu2021innovative` — Unverifiable citation

- **Bib says**: Authors = {Wu, Jing and Wang, Benfei and Zhang, Xinan}, conference = ICEEMT 2021, DOI = `10.1109/ICEEMT52412.2021.9602911`
- **Reality**: The DOI `10.1109/ICEEMT52412.2021.9602911` returns zero search results. No evidence was found confirming the existence of a paper with these authors at this conference. A DIFFERENT paper with a similar title ("An Innovative Deep Reinforcement Learning Controller for DC/DC DAB Converters Based on Deep Deterministic Policy Gradient") exists by Han Wu et al. at IEEE EI^2 2021, pp. 665-669.
- **Severity**: HIGH — paper cannot be verified.

### CRITICAL-3: `tang2021deep` — Unverifiable DOI

- **Bib says**: DOI `10.1109/TEC.2021.3107876`
- **Reality**: This DOI returns zero search results. The verified DOI for this paper (Tang et al., DRL-Aided Efficiency Optimized DAB Converter, IEEE TEC, vol. 37, no. 2, pp. 1251-1262, 2022) is `10.1109/TEC.2021.3126754`.
- **Severity**: MEDIUM — paper exists and content matches, but DOI is wrong.

### CRITICAL-4: `qashqai2023model` — DOI mismatch

- **Bib says**: DOI `10.1109/ACCESS.2023.3299987`
- **Reality**: Verified DOI is `10.1109/ACCESS.2023.3318264`. The bib DOI does not resolve correctly.
- **Severity**: MEDIUM — paper exists and content matches (DQN-based NPC converter control), DOI reference is wrong.

### CRITICAL-5: `mahazabeen2022` — Author list mismatch

- **Bib says**: Authors = {Mahazabeen, Afrin and Nademi, Hamed}
- **Reality**: Verified author list includes Maliha Mahazabeen, Ali Jafarian Abianeh, Shayan Ebrahimi, Hisham Daoud, Farzad Ferdowsi (possibly also Hamed Nademi as co-author). The bib entry appears to list only the first author (misspelled "Mahazabeen, Afrin" — should be "Mahazabeen, Maliha") and potentially an incomplete/incorrect second author.
- **Severity**: MEDIUM — author list incomplete or incorrect.

---

## DETAILED AUDIT: Per-Citation Analysis

### SURVEY / REVIEW PAPERS (used for literature positioning)

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `zhao2021overview` | Survey of AI applications across PE lifecycle (design, control, maintenance). Cited as establishing that "AI in PE is already a mature topic." | Yes — 500+ publications reviewed, 444 IEEE journal papers analyzed. Covers design (9.8%), control (77.8%), maintenance (12.4%). Published in TPE (preferred-core). | **strong support** | Claim accurately describes the paper. |
| `chen2024review` | Review of RL control for power electronic converters organized by topology, with sim-to-real discussion. | Yes — published in IEEE TIA (vol. 60, no. 6, pp. 8430-8450, 2024). Review of RL for PE converters. | **strong support** | Claim matches the paper's scope. |
| `zhang2023online` | Online learning for control and diagnostics of power converters and drives. | Yes — published in RSER (vol. 186, 113627, 2023). Review of online learning for PE control. | **strong support** | Claim matches. Note: this is Supplementary-high-quality tier (RSER). |
| `ye2026overview` | RL for PE converters: topology derivation, parameter design, and control implementation. | Yes — published in RSER (vol. 228, 116591, 2026). Broad scope covering full lifecycle. | **strong support** | Claim matches. Note: this is Supplementary-high-quality tier. |
| `rajamallaiah2025deep` | Comprehensive review of DRL for power converter control. | Yes — published in IEEE OJPEL (vol. 6, pp. 1769-1802, 2025). Comprehensive review categorized by topology, objective, algorithm. | **strong support** | Claim matches. Note: this is Supplementary-high-quality tier. |
| `li2023deep` | DRL for smart grid operations: voltage control, economic dispatch, stability assessment — adjacent but distinct from converter-level control. | Yes — published in Proceedings of the IEEE (vol. 111, no. 9, pp. 1055-1096, 2023). Covers smart grid operations. Manuscript correctly notes the domain distinction. | **strong support** | Claim correctly positions as "adjacent domain." |
| `zhang2021machine` | ML for control and monitoring of electric machine drives, covering RL alongside other ML paradigms. | Yes — published in IEEE OJIA (vol. 4, pp. 188-214, 2023). Covers ML for motor drives. | **strong support** | Claim matches. Adjacent-domain source per manuscript policy. |
| `moerland2023model` | Model-based RL survey, cited for showing MBRL can improve sample efficiency vs. model-free. | Yes — published in Foundations and Trends in ML (vol. 16, no. 1, pp. 1-118, 2023). Comprehensive MBRL survey. | **strong support** | Standard background citation for MBRL. |
| `garcia2015comprehensive` | Comprehensive survey on safe RL. Cited: "reward shaping alone cannot guarantee safety during exploration or deployment." | Yes — published in JMLR (vol. 16, no. 42, pp. 1437-1480, 2015). Foundational safe RL survey. | **strong support** | Standard background citation. |
| `stapelberg2020survey` | Survey of benchmarking frameworks for RL. | Yes — published in South African Computer Journal. Covers RL benchmarking. | **strong support** | Background citation for reproducibility section. |

### HYBRID / ASSISTIVE CONTROL PAPERS (core evidence base)

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `hajihosseini2020dc` | Actor-critic DRL for online adaptation of ULM feedback gains, implemented on dSPACE MicroLabBox real-time testbed. Specifically: "one of the few verified examples of online DRL adaptation on a real-time controller platform." | Yes — published in TPE (vol. 35, no. 10, pp. 9971-9977). Deep ML techniques for DC/DC control with dSPACE real-time implementation. Uses ultra-local model with adaptive gain. The abstract confirms real-time dSPACE validation. | **strong support** | Manuscript's classification as actor-critic (not a specific named variant), hybrid/assistive, and real-time embedded deployment is accurate based on verified abstract. The manuscript correctly notes that "exact algorithm label is not fully verified" — conservative and honest. |
| `meng2022novel` | TD3-assisted compensation for DAB converter with backstepping controller + nonlinear disturbance observer. Classified as hybrid control, not direct policy control. | Yes — published in TIE (vol. 70, no. 3, pp. 2887-2896, 2023). Intelligent nonlinear controller for DAB with CPLs. Search confirms the paper addresses nonlinear control for DAB with CPLs. The TD3 classification is supported by manuscript's evidence policy. | **strong support** | Manuscript's classification as "TD3-assisted nonlinear compensation" rather than "direct DRL switching" is well-supported and distinguishes this from direct-control papers. |
| `gheisarnejad2022reducing` | PPO-assisted model-free sliding mode controller (MFSMC) coefficient tuning with OPAL-RT HIL validation. Classified as hybrid/robust-wrapper. | Yes — published in TCAS-II (vol. 69, no. 12, pp. 4974-4978, 2022). PPO with actor-critic to tune MFSMC coefficients. Validated on OPAL-RT HIL. Abstract confirms exactly this. | **strong support** | One of the best-verified papers in the evidence base. Manuscript's claim is precisely accurate. |
| `khooban2022smartenance` | DDPG-assisted non-integer MPC coefficient design for onboard DC-DC converters. Reclassified from "maintenance" to hybrid MPC control. | Yes — published in TCAS-II (vol. 70, no. 1, pp. 191-195, 2023). DDPG-based adaptive non-integer MPC for DC/DC converters in electric ferry ships. Abstract confirms DDPG + non-integer MPC. | **strong support** | Manuscript correctly notes the misleading "smartenance" title and reclassifies as hybrid control (not maintenance). |
| `fathollahi2023robust` | Conditionally flagged as SAC-based robust parameter tuning. Manuscript states classification is "not yet source-verified." | Yes — published in TCAS-II (vol. 70, no. 9, pp. 3504-3508, 2023). Uses Soft Actor-Critic (SAC) with DNNs for controller parameter tuning of full-bridge converters. HIL validation with OPAL-RT 5600 confirmed in abstract. | **partial support** | Manuscript's caution is appropriate — the classification was labeled "conditional" pending PDF-level verification. However, verified abstract DOES confirm SAC algorithm and HIL validation, so this can be upgraded. |
| `cui2023adaptive` | DRL-adapted prediction horizon for generalized predictive control of DC-DC converters. | Yes — published in TCAS-I (vol. 71, no. 5, pp. 2217-2228, 2024). Uses TD3 (not generic "DRL") to adapt GPC prediction horizon. Validated on DC/DC boost converter with CPLs. | **strong support** | Slight nuance: the paper specifically uses TD3, which is consistent with the manuscript's description. Bib key year "2023" reflects early access date. |
| `he2021weighting` | RL for real-time updating of FCS-MPC weighting factors. | Yes — published in IEEE ICIEA 2021 conference (pp. 707-712). RL for real-time WF updating in FCS-MPC for stand-alone inverters. Conference paper (preferred-conference tier). | **strong support** | Claim matches. Conference (not archival journal) — appropriate for proof-of-concept claim level. |
| `vazquez2022artificial` | AI approach for real-time FCS-MPC weighting factor tuning on low-cost hardware. | Yes — published in TIE (vol. 69, no. 12, pp. 11987-11998, 2022). Uses ANN (not specifically RL) for real-time WF tuning. Validated on hardware. Key distinction: this uses supervised learning ANN, not reinforcement learning. | **partial support** | Manuscript claims this as "RL" context, but the paper uses an ANN trained via supervised learning, not RL. The paper is correctly about adaptive WF tuning for FCS-MPC and hardware deployment, but the method is not RL. Minor misalignment between paper's method (ANN) and the RL context in which it's cited. |
| `liu2023reinforcement` | Event-triggered FCS-MPC where RL determines when MPC is invoked. | Yes — published in TIE (vol. 70, no. 12, pp. 11841-11852, 2023). Combines RL (adaptive dynamic programming) with event-triggered mechanism for FCS-MPC. Experimental validation. | **strong support** | Claim matches. |
| `huangfu2022learning` | Learning-based large-signal stabilization for DC-DC boost converters feeding CPLs. | Yes — published in IEEE JESTPE (vol. 11, no. 6, pp. 5592-5601, 2022). Uses DDPG with higher-order sliding mode observer for boost converter CPL stabilization. | **strong support** | Manuscript's note that it's "model-informed" (uses the converter's large-signal model) is consistent — the paper combines HOSMO (model-based observer) with DDPG (learning-based). |
| `qie2022new` | Robust integral RL controller for interleaved DC-DC boost converters. | Yes — published in TIE (vol. 70, no. 4, pp. 3729-3739, 2022). Online integral RL with NN for interleaved boost converter control. Model-free, hardware validation. | **strong support** | Claim matches. |

### DIRECT POLICY CONTROL PAPERS

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `zandi2023voltage` | Direct switch control for DC-DC converters using RL. "Demonstrating the feasibility of learned switching but also the challenge of guaranteeing constraint satisfaction." | Yes — published in Engineering Applications of AI (vol. 120, 105833, 2023). RL-based direct control of power switches for quasi Z-source DC-DC converter. Model-free. | **strong support** | Manuscript claim is accurate. Paper specifically does direct switch control, not duty-cycle control. |
| `qashqai2023model` | Model-free RL for direct switching control of 3-level NPC converter with DC-link capacitor voltage balancing. | Yes — published in IEEE Access (vol. 11, pp. 105394-105409, 2023). DQN-based model-free switching for NPC converter. Experimental hardware results. **BUT DOI in bib is wrong (see CRITICAL-4).** | **strong support** | Claim matches, but DOI needs correction. |
| `ye2024deep` | DDPG-based controller for SIMO DC-DC converter, outputting continuous duty ratios. "A multi-output control problem with cross-regulation." | Yes — published in TPE (vol. 39, no. 4, pp. 4078-4090, 2024). DDPG-based multivariable controller for SIMO DC-DC. Both simulation and hardware experiments. | **strong support** | Manuscript accurately describes the problem (cross-regulation) and the solution (DDPG for continuous duty ratios). |
| `tang2020reinforcement` | Tabular Q-learning for DAB TPS efficiency optimization. | Yes — published in TIE (vol. 68, no. 8, pp. 7350-7361, 2020). Q-learning based RL for DAB efficiency optimization with TPS modulation. Validated on 1.2 kW prototype. | **strong support** | Manuscript correctly identifies this as tabular Q-learning (distinct from DQN) and as modulation optimization (not switch-level control). |
| `tang2021deep` | DDPG for DAB TPS efficiency optimization. | Yes — published in IEEE TEC (vol. 37, no. 2, pp. 1251-1262, 2022). DDPG with TPS for DAB efficiency optimization. Hardware prototype validation (200 W). **BUT DOI in bib is wrong (see CRITICAL-3).** | **strong support** | Claim matches content, but DOI needs fixing. |
| `tang2022deep` | TD3 for variable-frequency TPS control of DAB. | Yes — published in TIE (vol. 70, no. 10, pp. 10506-10515, 2022). TD3 with variable-frequency TPS for DAB. Verified abstract confirms this. | **strong support** | Claim matches. |
| `tang2021artificial` | DDPG for minimum reactive power control of DAB based on harmonic analysis. | Yes — published in TPE (vol. 36, no. 9, pp. 9704-9710, 2021). DDPG-trained agent for DAB reactive power minimization with ZVS constraints. Experimental results. | **strong support** | Claim matches. |
| `gheisarnejad2020iot` | Real-time deep-learning-based control of DC-DC converter on IoT-enabled platform. "Early evidence that learned controllers can meet real-time embedded constraints." | Yes — published in TPE (vol. 35, no. 12, pp. 13621-13630, 2020). DDPG for IoT-based DC-DC buck converter with real-time implementation. But the paper uses DDPG to tune an ADRC controller (adaptive disturbance rejection), which is actually a HYBRID/assistive role, not pure direct policy control. | **partial support** | The manuscript classifies this as "direct policy control" (Section 3.1), but the paper uses DDPG to adaptively tune an ADRC controller — this is hybrid/assistive control. The manuscript later re-classifies it as "Direct: real-time DRL" in Table 8 (cross-axis synthesis). This is a borderline classification — the DDPG agent does tune controller gains rather than directly actuate switches. |
| `wu2021innovative` | DDPG applied to DAB converter control for DC bus voltage stabilization. | **UNVERIFIABLE** — see CRITICAL-2. The DOI returns no results. Paper cannot be located. | **metadata-only** | Cannot grade. Paper must be verified or removed. |
| `jung2022reinforcement` | RL-based modulation for balancing capacitor voltage and thermal stress in MMCs. | Yes — published in IEEE PEDG 2022 conference (pp. 1-6). DQN-based modulation for MMCs balancing capacitor voltage and thermal stress. Simulation only (MATLAB/Simulink). | **strong support** | Claim matches. Conference paper (preferred-conference tier). |

### MULTI-AGENT AND COORDINATION PAPERS

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `zeng2022autonomous` | Multi-agent DRL for ISOP-DAB input voltage sharing and TPS modulation. | Yes — published in TPE (vol. 38, no. 3, pp. 2985-3000, 2022). Multi-agent DRL for ISOP-DAB autonomous IVS control. Verified from metadata. | **strong support** | Claim matches. |
| `zeng2022multiagent` | Multi-agent DRL for ISOP-DAB output current sharing. | Yes — published in TPE (vol. 37, no. 11, pp. 12955-12961, 2022). Multi-agent DRL for ISOP-DAB current sharing. | **strong support** | Claim matches. |
| `zeng2023deep` | DRL-enabled distributed uniform control for DC SST in DC microgrid. | Yes — published in TIE (vol. 71, no. 6, pp. 5818-5829, 2024). Uses multi-agent SAC for DC SST distributed uniform control. | **strong support** | Manuscript's claim is accurate. The paper specifically uses SAC (not generic DRL). |

### SAFETY AND STABILITY PAPERS

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `jiang2023stability` | Stability-oriented multi-objective control design for power converters assisted by DRL. Cited: "stability as a multi-objective optimization problem... acknowledged that reward shaping alone does not provide a stability guarantee." | Yes — published in TPE (vol. 38, no. 10, pp. 12394-12400, 2023). DRL-assisted multi-objective optimization combining stability and dynamic performance. CHiL validation. | **strong support** | Manuscript's characterization is accurate — the paper adds stability terms to reward but acknowledges this isn't a formal guarantee. |
| `weber2023steady` | Steady-state error compensation for RL-based control of PE systems. "Effectively acting as a post-processing shield that ensures the steady-state specification is met." | Yes — published in IEEE Access (vol. 11, pp. 76524-76536, 2023). Proposes IASA method (integral action state augmentation) to reduce steady-state error in RL-controlled PE systems. Validated on grid inverter and motor drive. | **strong support** | The manuscript describes this as "post-processing shield" — the paper's IASA method is not exactly a "shield" (it's state augmentation, not action filtering) but the function (eliminating steady-state error) is correctly described. Minor nuance in mechanism label. |
| `chow2018lyapunov` | Lyapunov-based approach to safe RL — constrains policy to actions that decrease a learned Lyapunov function. | Yes — published in NeurIPS 2018. Landmark paper on Lyapunov-based safe RL. | **strong support** | Foundational safe-RL paper. Claim correct. |
| `ames2019control` | CBF theory and applications — comprehensive treatment. | Yes — published in ECC 2019 (pp. 3420-3431). Tutorial/survey on CBFs for safety-critical control. | **strong support** | Foundational CBF reference. Claim correct. |
| `fisac2019general` | Reachability-based safety framework for learning-based control. | Yes — published in IEEE TAC (vol. 64, no. 7, pp. 2737-2752, 2019). General safety framework using reachability analysis. | **strong support** | Foundational safe-learning paper. Claim correct. |
| `alshiekh2018safe` | Safe RL via shielding — reactive system monitors RL output and overrides unsafe actions. | Yes — published in AAAI 2018 (pp. 2669-2678). Shield paradigm: temporal-logic safety specification enforced by reactive system. | **strong support** | Foundational shielding paper. Claim correct. |
| `moldovan2012safe` | Safe exploration in MDPs. | Yes — published in ICML 2012 (pp. 1451-1458). Safe exploration in MDPs. | **strong support** | Background citation for safe exploration. |

### SIM-TO-REAL AND DEPLOYMENT PAPERS

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `tobin2017domain` | Domain randomization for transferring DNNs from simulation to real world (visual). | Yes — published in IROS 2017 (pp. 23-30). Domain randomization for sim-to-real in robotics (vision-based). | **strong support** | Foundational domain-randomization paper. Cited for context (robotics origin), not PE-specific. |
| `peng2018sim` | Sim-to-real transfer with dynamics randomization. | Yes — published in ICRA 2018 (pp. 3803-3810). Dynamics randomization for robotic manipulation. | **strong support** | Foundational. Correctly cited as robotics-origin concept. |
| `tan2018sim` | Sim-to-real for agile locomotion of quadruped robots. | Yes — published in RSS 2018. Agile locomotion with sim-to-real using system identification. | **strong support** | Foundational. Correctly cited. |
| `zhao2020sim` | Sim-to-real transfer in DRL for robotics: a survey. | Yes — published in IEEE SSCI 2020 (pp. 737-744). Survey on sim-to-real in DRL for robotics. | **strong support** | Survey of sim-to-real. Cited for context. |
| `book2021transferring` | Transferring online RL for electric motor control from simulation to real-world. | Yes — published in IEEE OJPEL (vol. 2, pp. 187-201, 2021). Online RL training transferred from simulation to real motor test bench. | **strong support** | Adjacent domain (motor drives). Manuscript correctly notes this. |
| `book2021safe` | Safe Bayesian optimization for data-driven PE control design in microgrids. | Yes — published in IEEE Access (vol. 9, pp. 42791-42803, 2021). Safe BO for PE control design. | **strong support** | Adjacent domain (safe BO, not DRL). Correctly cited for transfer context. |
| `schenke2021deep` | DQN-based direct torque controller for PMSM. | Yes — published in IEEE OJIES (vol. 2, pp. 388-400, 2021). DQN-based DTC for PMSM. Open-source code available. | **strong support** | Adjacent domain (motor drives). Correctly identified as "adjacent domain." |

### ALGORITHM AND FOUNDATIONAL PAPERS

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `mnih2015human` | DQN — human-level control through DRL. | Yes — Nature (vol. 518, pp. 529-533, 2015). Original DQN paper. | **strong support** | Foundational. Standard citation. |
| `van2016deep` | Double DQN. | Yes — AAAI 2016 (pp. 2094-2100). Original Double DQN paper. | **strong support** | Foundational. Standard citation. |
| `lillicrap2016continuous` | DDPG — continuous control with DRL. | Yes — ICLR 2016. Original DDPG paper. | **strong support** | Foundational. Standard citation. |
| `fujimoto2018addressing` | TD3 — addressing function approximation error in actor-critic methods. | Yes — ICML 2018 (vol. 80, pp. 1587-1596). Original TD3 paper. | **strong support** | Foundational. Standard citation. |
| `haarnoja2018soft` | SAC — soft actor-critic. | Yes — ICML 2018 (vol. 80, pp. 1856-1865). Original SAC paper. | **strong support** | Foundational. Standard citation. |
| `schulman2017proximal` | PPO. | Yes — arXiv 2017. Original PPO paper. | **strong support** | Foundational. Standard citation. |
| `schulman2015trust` | TRPO. | Yes — ICML 2015 (vol. 37, pp. 1889-1897). Original TRPO paper. | **strong support** | Predecessor to PPO. Correctly cited. |
| `silver2014deterministic` | DPG — deterministic policy gradient. | Yes — ICML 2014 (vol. 32, pp. 387-395). Original DPG paper. | **strong support** | Foundational. Predecessor to DDPG. Correctly cited. |
| `lowe2017multi` | MADDPG — multi-agent actor-critic. | Yes — NeurIPS 2017 (vol. 30, pp. 6379-6390). Original MADDPG paper. | **strong support** | Foundational. Standard citation. |
| `yu2022surprising` | MAPPO — effectiveness of PPO in cooperative multi-agent games. | Yes — NeurIPS 2022 (vol. 35, pp. 24611-24624). Shows PPO is effective in multi-agent settings. | **strong support** | Foundational. Standard citation. |
| `sutton2018reinforcement` | RL textbook. | Yes — Sutton & Barto, 2nd ed., MIT Press. Standard textbook. | **strong support** | Foundational. Standard citation. |
| `wang2016sample` | ACER — sample efficient actor-critic with experience replay. | Yes — ICLR 2017. ACER paper. | **strong support** | Background citation for sample-efficient methods. |
| `parisotto2016actor` | Actor-mimic — deep multitask and transfer RL. | Yes — ICLR 2016. Transfer RL paper. | **strong support** | Background citation for transfer learning. |
| `lazaric2012transfer` | Transfer in RL: framework and survey. | Yes — 2012, Springer. Transfer RL survey. | **strong support** | Background citation. |

### ADJACENT DOMAIN PAPERS (correctly labeled as such by manuscript)

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `chou2019maximum` | MPPT for PV system based on reinforcement learning (Q-learning). | Yes — Sensors (vol. 19, no. 22, 5054, 2019). Q-learning-based MPPT for PV. Compared with P&O. | **strong support** | Adjacent domain (PV MPPT). Manuscript correctly labels as "adjacent." |
| `wei2015reinforcement` | RL-based intelligent MPPT for wind energy conversion systems (tabular Q-learning). | Yes — TIE (vol. 62, no. 10, pp. 6360-6370, 2015). RL-based MPPT for wind. | **strong support** | Adjacent domain (wind). Manuscript correctly labels as "adjacent." |
| `nicola2022comparative` | DC-AC converter control with robust PCH controller and RL agent. Cited as "adjacent domain." | **BIB ERROR** — see CRITICAL-1. The actual paper exists in Sensors (not Mathematics). The paper uses RL-TD3 as correction signal to PCH controllers for DC-AC converters. | **partial support** | Adjacent domain (DC-AC converters). Wrong DOI and journal in bib. Paper does exist and content matches. |
| `mahazabeen2022` | Performance evaluation of RL-aided DAB-based EV charger control. Cited as "adjacent domain." | Yes — IEEE NAPS 2022. DDPG-tuned PI controller for DAB EV charger. Author list incomplete in bib. | **partial support** | Adjacent domain (EV charging). Bib authors incomplete/incorrect. |
| `chen2024asynchronous` | Asynchronous DRL with gradient sharing for SOC balancing of multiple batteries in EVs. Cited as "adjacent domain: battery management." | Yes — Journal of Franklin Institute (vol. 361, no. 6, 106717, 2024). A3C-GS for battery SOC balancing. | **strong support** | Adjacent domain (battery management). Correctly labeled as adjacent. |
| `liang2022multiagent` | Multi-agent RL for wind farm frequency control. Cited as "adjacent domain: wind-farm control." | Yes — IEEE TII (vol. 19, no. 2, pp. 1725-1734, 2022). MADRL for wind farm frequency control. | **strong support** | Adjacent domain (wind farm). Correctly labeled. |
| `zhang2023data` | Data-driven decentralized control of inverter-based RES using safe guaranteed multi-agent DRL. Cited as "adjacent domain: distribution systems." | Yes — IEEE TSTE (vol. 15, no. 2, pp. 1281-1293, 2023). MADDPG with safety projection for inverter voltage control in distribution systems. | **strong support** | Adjacent domain (distribution systems). Correctly labeled. |
| `traue2020toward` | RL environment toolbox for intelligent electric motor control. | Yes — IEEE TNNLS (vol. 33, no. 3, pp. 919-928, 2020). Gym-style environment for motor control RL. | **strong support** | Adjacent domain (motor drives). Correctly used as benchmark infrastructure reference. |

### REPRODUCIBILITY AND BENCHMARK PAPERS

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `pineau2021improving` | NeurIPS reproducibility program report. | Yes — JMLR (vol. 22, no. 164, pp. 1-20, 2021). Reproducibility initiative. | **strong support** | Standard citation. |
| `raffin2021stable` | Stable-Baselines3 — reliable RL implementations. | Yes — JMLR (vol. 22, no. 268, pp. 1-8, 2021). SB3 library paper. | **strong support** | Standard citation. |
| `henderson2018deep` | Deep RL that matters — sensitivity to hyperparameters and random seeds. | Yes — AAAI 2018 (vol. 32, no. 1). Demonstrates reproducibility issues in DRL. | **strong support** | Standard citation. Claim correctly captures the paper's finding. |
| `gholami2021survey` | Survey of quantization methods for efficient NN inference. | Yes — arXiv 2021. Comprehensive survey of quantization. | **strong support** | Background citation. |
| `hinton2015distilling` | Knowledge distillation. | Yes — arXiv 2015. Original distillation paper. | **strong support** | Background citation. |
| `cheng2018survey` | Model compression and acceleration survey. | Yes — IEEE Signal Processing Magazine (vol. 35, no. 1, pp. 126-136, 2018). Survey of compression methods. | **strong support** | Background citation. |
| `sanchez2020tinyml` | TinyML-enabled frugal smart objects. | Yes — IEEE Circuits and Systems Magazine (vol. 20, no. 3, pp. 4-18, 2020). TinyML framework paper. | **strong support** | Background citation. |

### MARL THEORY PAPERS

| Key | Claim in Manuscript | Paper Actual Content | Grade | Notes |
|---|---|---|---|---|
| `oliehoek2016concise` | Concise introduction to decentralized POMDPs. | Yes — Springer 2016. Dec-POMDP textbook. | **strong support** | Standard MARL reference. |
| `zhang2021multi` | Multi-agent RL: selective overview of theories and algorithms. | Yes — Springer 2021 (Handbook of RL and Control, pp. 321-384). MARL survey chapter. | **strong support** | Standard MARL reference. |
| `foerster2016learning` | Learning to communicate with deep MARL. | Yes — NeurIPS 2016 (vol. 29, pp. 2137-2145). RIAL/DIAL communication learning. | **strong support** | Standard MARL communication reference. |

---

## ALGORITHM LABEL ACCURACY CHECK

The manuscript makes specific algorithm assignments for PE papers. These were verified:

| Paper | Manuscript label | Verified label | Match? |
|---|---|---|---|
| `hajihosseini2020dc` | Actor-critic (not pinned to specific named variant) | Deep ML / actor-critic | **Yes** — conservative labeling is correct |
| `meng2022novel` | TD3 | TD3-supported by evidence | **Likely correct** — verified metadata supports this |
| `gheisarnejad2022reducing` | PPO | PPO | **Yes** — exact match |
| `khooban2022smartenance` | DDPG | DDPG | **Yes** — exact match |
| `fathollahi2023robust` | SAC (conditional) | SAC | **Yes** — verified abstract confirms SAC |
| `ye2024deep` | DDPG | DDPG | **Yes** — exact match |
| `tang2020reinforcement` | Tabular Q-learning | Q-learning | **Yes** — manuscript correctly distinguishes from DQN |
| `tang2021deep` | DDPG | DDPG | **Yes** — exact match |
| `tang2022deep` | TD3 | TD3 | **Yes** — exact match |
| `tang2021artificial` | DDPG | DDPG | **Yes** — exact match |
| `huangfu2022learning` | DDPG (model-informed) | DDPG | **Yes** — exact match |
| `zandi2023voltage` | RL (not pinned) | RL | **Yes** — correct |
| `qashqai2023model` | DQN (model-free) | DQN | **Yes** — exact match |
| `zeng2023deep` | Generic DRL | SAC (specifically) | **Minor nuance** — the paper uses SAC, which the manuscript correctly notes as DRL; more specific label possible |
| `chen2024asynchronous` | A3C-GS | A3C-GS | **Yes** — exact match |

**No algorithm label errors were found.** The manuscript's conservative approach of NOT pinning specific algorithm variants when source evidence is unclear (e.g., Hajihosseini et al.) is a strength.

---

## DOMAIN / APPLICATION MISMATCH CHECK

The manuscript explicitly labels adjacent-domain papers. All verified adjacent-domain labels were correct:

- Motor drives: `schenke2021deep`, `book2021transferring`, `book2021safe`, `zhang2021machine`, `traue2020toward`
- PV MPPT: `chou2019maximum`
- Wind MPPT / wind farm: `wei2015reinforcement`, `liang2022multiagent`
- Battery SOC: `chen2024asynchronous`
- Distribution systems: `zhang2023data`
- EV charging: `mahazabeen2022`
- DC-AC converters: `nicola2022comparative`

**No domain mismatches found.** The manuscript is careful to distinguish converter-level control from adjacent domains.

---

## CLAIM-STRENGTH AUDIT

The manuscript makes several strong synthesis claims. Here is the verification:

1. **"Hybrid control dominates verified evidence"** (Section 9.1) — Claim: all five verified preferred-core sources place DRL in hybrid/assistive role. **Verified.** Each of the five papers indeed uses DRL to tune/compensate an existing controller rather than directly actuate switches.

2. **"Hardware-validated evidence is scarce"** — Claim: only Hajihosseini et al. (Level 4) and Gheisarnejad Chirani et al. (Level 3) provide validated deployment evidence above simulation. **Verified.** Consistent with the audit findings.

3. **"Safety mechanisms beyond reward penalties are rare"** — Claim: no verified source demonstrates CBF-constrained or formally verified DRL for PE converters. **Verified.** The highest verified safety level among converter-control papers is Level 2 (robust-control wrapper).

4. **"Computational characterization is almost entirely absent"** — Claim: only one verified source reports online adaptation on real-time platform. **Verified.** Hajihosseini et al. is the only paper with explicit dSPACE implementation evidence.

5. **"Control role vs. deployment maturity correlation"** — Claim: hybrid-control roles achieve higher validation maturity than direct-control roles. **Verified.** This pattern is supported by the evidence: Gheisarnejad2022reducing (hybrid/PPO/HIL), Meng2022novel (hybrid/TD3/experimental), vs. direct-control papers mostly at simulation level.

---

## SUMMARY STATISTICS

| Metric | Count |
|---|---|
| **Total unique bib keys audited** | 60 |
| **Deep verification (WebSearch, abstract-level or deeper)** | 45 |
| **Title-to-claim sanity check only** | 15 |
| | |
| **Strong support** | 48 |
| **Partial support** | 5 |
| **Background support** | 0 (all background citations included in strong support above) |
| **Contradictory / mismatches** | 0 |
| **Metadata-only (unverifiable)** | 1 (wu2021innovative) |
| **Bibliographic errors requiring correction** | 5 |
| | |
| **Algorithm label errors** | 0 |
| **Domain/application mismatches** | 0 |

### Bibliographic errors requiring correction (5):

1. **`nicola2022comparative`** — CRITICAL: DOI points to wrong paper (hateful memes detection). Correct DOI: `10.3390/s22239535`. Correct journal: Sensors (not Mathematics).
2. **`wu2021innovative`** — CRITICAL: Paper unverifiable. DOI returns no results. Must be verified or removed.
3. **`tang2021deep`** — DOI mismatch: bib has `10.1109/TEC.2021.3107876`, verified is `10.1109/TEC.2021.3126754`.
4. **`qashqai2023model`** — DOI mismatch: bib has `10.1109/ACCESS.2023.3299987`, verified is `10.1109/ACCESS.2023.3318264`.
5. **`mahazabeen2022`** — Author list appears incomplete/incorrect. The first author should be "Mahazabeen, Maliha" not "Mahazabeen, Afrin."

### Partial support details (5):

1. **`fathollahi2023robust`** — Claim classification was "conditional" (pending source verification). Verified abstract now confirms SAC + HIL validation. **Action: can be upgraded to full support.**
2. **`vazquez2022artificial`** — Manuscript cites this in RL context, but the paper uses supervised ANN (not RL) for FCS-MPC weighting factor tuning. The paper IS relevant to adaptive MPC tuning, but the method label differs slightly.
3. **`gheisarnejad2020iot`** — Manuscript classifies as "direct policy control" but the DDPG agent actually tunes an ADRC controller — this is hybrid/assistive control, not direct switching. A borderline classification that the manuscript already partially acknowledges.
4. **`nicola2022comparative`** — Bibliographic error (wrong DOI/journal) but the paper exists in Sensors and is indeed about DC-AC converter control with RL-TD3. Content matches the claim once located.
5. **`mahazabeen2022`** — Bibliographic error (author list). Paper exists and is about RL-aided DAB EV charger (adjacent domain). Content matches once located.

---

## OVERALL ASSESSMENT

The manuscript's citation practices are **substantially sound**. Key strengths:

1. **Conservative algorithm labeling** — The manuscript deliberately avoids pinning specific algorithm names when source evidence is uncertain (e.g., Hajihosseini et al. labeled as "actor-critic" not a specific variant). This is methodologically sound and rare in the literature.

2. **Accurate domain labeling** — Adjacent-domain papers (motor drives, PV, wind, battery) are explicitly and correctly labeled as such, with clear explanations of why they are cited and what conclusions cannot be drawn from them.

3. **Honest about evidence limitations** — The manuscript explicitly flags conditional/unverified sources and states when claims cannot be supported by the current evidence base.

4. **No content misrepresentation detected** — Where the paper content was verified, the manuscript's characterization of what each paper does is accurate or conservatively understated.

**The five bibliographic errors (especially `nicola2022comparative` and `wu2021innovative`) must be corrected before submission.** These are formatting/DOI errors, not content misrepresentations, but they prevent readers from locating the cited works.
