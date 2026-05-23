# Paper A Evidence Table

This is the source inventory for Paper A. Rows are extracted from the current control section citations. **Algorithm labels remain unverified unless the status says verified from the source paper.** This avoids repeating the reviewer-identified classification failures.

## Fields to Complete Before Drafting Claims

- `Algorithm verified`: exact method used in the source paper.
- `Control role`: direct policy control, parameter tuning, modulation optimization, energy management, coordination, or other.
- `System`: converter or energy-conversion system type.
- `Validation maturity`: simulation, HIL, real-time controller, embedded prototype, field/industrial evidence.
- `Evidence weight`: journal/hardware-validated, journal/simulation-only, conference proof-of-concept, adjacent-domain transfer.
- `Verified basis`: source page, abstract sentence, table, experiment section, or code/dataset.

## Current Control-Reference Inventory

| Key | Year | Source type | Title | Preliminary role from old draft | Verification status |
|---|---:|---|---|---|---|
| `10030117` | 2022 | Conference | Voltage Regulation of DC-DC Buck Converters Feeding CPLs via Automatic Curriculum Learning | Buck/CPL voltage control | Open: verify algorithm and validation |
| `10141314` | 2023 | Conference | A TD3 Algorithm Based Reinforcement Learning Controller for DC-DC Switching Converters | Bidirectional switching converter control | Open: verify TD3 and validation |
| `10245391` | 2023 | Conference | Intelligent DRL Control for DC-DC Buck Converter Feeding a Constant Power Load | Buck/CPL voltage control | Open |
| `10246775` | 2023 | Conference | Implementation of Real Time Normalized Advantage Function Control for a Buck Converter | Real-time NAF buck control | Open: verify real-time platform |
| `10264605` | 2023 | Conference | State Spaces and Reward Functions in RL-Based Control of a DC/DC Buck Converter | Reward/state design | Open |
| `9521987` | 2022 | Journal | Voltage Regulation of DC-DC Buck Converters Feeding CPLs via DRL | Buck/CPL voltage control | Open |
| `9660319` | 2021 | Conference | RL-Based Online-Training AI Controller for DC-DC Switching Converters | Online-training converter controller | Open |
| `9752938` | 2022 | Conference | Performance Enhancement of Buck Converter Using Reinforcement Learning Control | Buck control | Open |
| `alfred2021model` | 2021 | Conference | Model-Free RL-Based Control Methodology for Power Electronic Converters | Model-free converter control | Open |
| `anugula2021deep` | 2021 | Conference | DRL-Based Adaptive Controller of DC Electric Drive | Motor drive control | Open |
| `arianborna2023mppt` | 2023 | Conference | MPPT Control of a PMSG Connected to the Wind Turbine Based on Deep Q-Network | MPPT/wind conversion | Open |
| `bo2022controller` | 2022 | Conference | Controller Parameterization for Grid-Connected Power Converters through RL | Controller tuning | Open |
| `book2021transferring` | 2021 | Journal | Transferring Online RL for Electric Motor Control from Simulation to Real-World Experiments | Sim-to-real motor control | Open: candidate deployment evidence |
| `chen2024asynchronous` | 2024 | Journal | Asynchronous DRL with Gradient Sharing for SOC Balancing of Multiple Batteries | Adjacent multi-agent/battery coordination | Open: mark as adjacent if not PEC control |
| `chen2024control` | 2024 | Conference | Control of a Wave Energy Converter Using Model-Free DRL | Wave energy converter control | Open |
| `chou2019maximum` | 2019 | Journal | Maximum Power Point Tracking of Photovoltaic System Based on RL | MPPT | Open |
| `cui2023adaptive` | 2023 | Journal | Adaptive Horizon Seeking for Generalized Predictive Control via DRL with Application to DC/DC Converters | Hybrid predictive control tuning | Open |
| `dong2022generalized` | 2022 | Conference | Generalized Predictive Controller with Self-Tuning Horizon for DC/DC Converters Using Multi-Objective DRL | Hybrid predictive control tuning | Open |
| `dragoun2019adaptive` | 2019 | Conference | Adaptive Control of LCL Filter with Time-Varying Parameters Using RL | Grid filter adaptive control | Open |
| `fathollahi2023robust` | 2023 | Journal | Robust AI Controller for Stabilization of Full-Bridge Converters Feeding CPLs | Robust stabilization | Conditional: secondary source says SAC/HIL, but not counted until source/PDF confirms |
| `gheisarnejad2020iot` | 2020 | Journal | IoT-Based DC/DC Deep Learning Power Converter Control: Real-Time Implementation | Real-time DC/DC control | Open: candidate real-time evidence |
| `gheisarnejad2020novel` | 2020 | Journal | Nonlinear DRL Controller for DC-DC Buck Converters | Buck control | Open |
| `gheisarnejad2022reducing` | 2022 | Journal | Reducing Impact of Constant Power Loads on DC Energy Systems by AI | CPL mitigation | Verified-source: PPO actor-critic tunes MFSMC coefficients; OPAL-RT HIL simulations |
| `hajihosseini2020dc` | 2020 | Journal | DC/DC Power Converter Control-Based Deep Machine Learning Techniques: Real-Time Implementation | Real-time DC/DC control | Verified-source-limited: actor-critic DRL/ULM gain adaptation; dSPACE MicroLabBox real-time testbed; no named DDPG/PPO/SAC/TD3/DQN count |
| `he2021weighting` | 2021 | Conference | Real-Time Updating of FCS-MPC Weighting Factors via RL | MPC parameter tuning | Open |
| `hu2021novel` | 2021 | Conference | PID Controller Based on DRL for DC/DC Buck Converters | Hybrid PID tuning/control | Open |
| `huangfu2022learning` | 2022 | Journal | Learning-Based Optimal Large-Signal Stabilization for DC/DC Boost Converters Feeding CPLs via DRL | Stability-oriented control | Open: candidate safety/stability evidence |
| `jiang2021application` | 2021 | Conference | Neural Network Controller and Policy Gradient RL on MMC: Proof of Concept | MMC proof-of-concept | Open |
| `jiang2023stability` | 2023 | Journal | Stability-Oriented Multiobjective Control Design for Power Converters Assisted by DRL | Stability-oriented control design | Open: high-priority verify |
| `jung2022reinforcement` | 2022 | Conference | RL-Based Modulation for Balancing Capacitor Voltage and Thermal Stress in MMCs | MMC modulation/stress balancing | Open |
| `khooban2022smartenance` | 2022 | Journal | Smartenance DC-DC On-Board Power Converters | Hybrid maintenance/control | Verified-source: DDPG actor-critic designs non-integer MPC coefficients; experimental comparative results; reclassify to Paper A hybrid MPC control |
| `kosuru2022deep` | 2022 | Proceedings/Actuators | DRL for Stability Enhancement of Variable Wind Speed DFIG System | Wind converter stability | Open |
| `lee2023pwm` | 2023 | Conference | PWM-PFM Hybrid Modulation for DAB Converter Based on RL | DAB modulation | Open |
| `li2023large` | 2023 | Journal | Large-Scale Multi-Agent DRL for Cooperative Output Voltage Control of PEMFCs | Multi-agent voltage coordination | Open: adjacent energy-conversion system |
| `liang2022multiagent` | 2022 | Journal | Multiagent RL for Wind Farm Frequency Control | Adjacent multi-agent coordination | Open: mark as adjacent unless converter-focused |
| `lu2021speed` | 2021 | Conference | Speed Tracking of BLDC Motor Based on DRL and PID | Motor drive hybrid control | Open |
| `mahazabeen2022performance` | 2022 | Conference | RL-Aided DAB-Based EV Charger Control | DAB/EV charger control | Open |
| `mao2022research` | 2022 | Conference | Adaptive PI Controller Based on DRL for DC-DC Boost Converter | Hybrid PI tuning | Open |
| `meng2022novel` | 2022 | Journal | Intelligent Nonlinear Controller for DAB Converter with CPLs | DAB nonlinear control | Verified-source: TD3 keyword; DRL compensation with disturbance observer/backstepping; experiments reported |
| `nicola2022comparative` | 2022 | Journal | DC-AC Converter Control Based on Robust/PCH Controllers and RL Agent | DC-AC comparative control | Open |
| `nicola2022improved` | 2022 | Conference | Improved DC-AC Converter Control Based on PCH Controller and RL Agent | DC-AC hybrid control | Open |
| `nicola2023improved` | 2023 | Conference | Improved DC-DC Converter for Fuel Cell/Battery Hybrid System Based on ACO and RL-TD3 | Hybrid energy converter control | Open |
| `pinthurat2023simultaneous` | 2023 | Journal | Simultaneous Voltage Regulation and Unbalance Compensation in Distribution Systems | Adjacent distribution control | Open |
| `prag2021data` | 2021 | Journal | Data-Driven Model Predictive Control of DC-to-DC Buck-Boost Converter | Data-driven MPC comparator | Open: not necessarily RL |
| `qashqai2023model` | 2023 | Journal | Model-Free Switching and Control for Three-Level NPC Converter Using DRL | NPC switching/control | Open |
| `qie2022new` | 2022 | Journal | Robust Integral RL-Based Control for Interleaved DC/DC Boost Converter | Robust integral RL | Open |
| `qie2023new` | 2023 | Conference | RL-Based Voltage Control for Three-Phase AC/DC Converter | AC/DC voltage control | Open |
| `ranjbaran2023reinforcement` | 2023 | Conference | RL-Based Energy Management of Hybrid Energy Storage Systems in EVs | Energy management | Open |
| `schenke2021deep` | 2021 | Journal | Deep Q-Learning Direct Torque Controller for PMSMs | Motor control | Open |
| `tang2020reinforcement` | 2020 | Journal | RL-Based Efficiency Optimization for DAB Converter with Triple-Phase-Shift Modulation | DAB efficiency/modulation | Open |
| `tang2021deep` | 2021 | Journal | DRL-Aided Efficiency-Optimized DAB Converter for Distributed Generation | DAB efficiency/modulation | Open |
| `tang2021rl` | 2021 | Journal | RL-ANN Minimum-Current-Stress Scheme for DAB Converter with TPS Control | DAB stress optimization | Open |
| `tang2022deep` | 2022 | Journal | DRL-Aided Variable-Frequency TPS Control for DAB Converter | DAB modulation | Open |
| `teng2020reinforcement` | 2020 | Conference | RL-Based Data-Driven Voltage Regulator for Wireless EV Chargers | Wireless charger voltage control | Open |
| `traue2020toward` | 2020 | Journal | RL Environment Toolbox for Intelligent Electric Motor Control | Benchmark/toolbox | Open |
| `wan2021reinforcement` | 2021 | Conference | RL-Based Weighting Factor Design of MPC for Power Electronic Converters | MPC parameter tuning | Open |
| `wang2023improved` | 2023 | Journal | Model-Free Active Disturbance Rejection Deadbeat Predictive Current Control of PMSM | Motor-control comparator/adjacent | Open |
| `weber2023steady` | 2023 | Journal | Steady-State Error Compensation for RL-Based Control of Power Electronic Systems | RL error compensation | Open |
| `wei2015reinforcement` | 2015 | Journal | RL-Based Intelligent MPPT for Wind Energy Conversion Systems | MPPT/wind conversion | Open |
| `wu2021innovative` | 2021 | Conference | DRL Controller for DC/DC DAB Converters Based on DDPG | DAB phase/control | Open: verify DDPG |
| `yan2022multiagent` | 2022 | Journal | Multiagent Quantum DRL for Distributed Frequency Control of Islanded Microgrids | Multi-agent coordination | Open: adjacent microgrid |
| `yang2020deep` | 2020 | Journal | DRL-Based Energy Management Strategy for Supercapacitor Energy Storage in Urban Rail Transit | Energy management | Open |
| `ye2024deep` | 2024 | Journal | DDPG-Based RL Controller for Single-Inductor Multiple-Output DC-DC Converter | SIMO DC-DC control | Open: high-priority recent journal |
| `yin2021quantum` | 2021 | Journal | Quantum DRL for Rotor-Side Converter Control of DFIG-Based Wind Turbines | Wind converter control | Open |
| `zandi2023voltage` | 2023 | Journal | Voltage Control of DC-DC Converters through Direct Switch Control Using RL | Direct switch control | Open |
| `zeng2021deep` | 2021 | Conference | DRL-Based Input Voltage Sharing for ISOP DAB Converter in DC Microgrids | ISOP-DAB sharing | Open |
| `zeng2022autonomous` | 2022 | Journal | Autonomous Input Voltage Sharing and TPS Modulation for ISOP-DAB Converter: Multiagent DRL | Multi-agent ISOP-DAB control | Open |
| `zeng2022multiagent` | 2022 | Journal | Multiagent DRL-Aided Output Current Sharing for ISOP-DAB Converter | Multi-agent ISOP-DAB control | Open |
| `zeng2023deep` | 2023 | Journal | DRL-Enabled Distributed Uniform Control for DC Solid-State Transformer in DC Microgrid | Distributed SST control | Open |
| `zhou2023ai` | 2023 | Journal | AI-Based Power Reserve Control for PV Generation in Microgrid Frequency Regulation | PV/microgrid frequency support | Open |
| `zou2022optimization` | 2022 | Journal | Optimization of Electricity Generation of a Wave Energy Converter Using DRL | Wave energy optimization | Open |

## New-2026-05-23: Literature Expansion (2023--2026 Papers)

| Key | Year | Source type | Title | Preliminary role | Verification status |
|---|---:|---|---|---|---|
| `cui2023implementation` | 2023 | Journal (TIE) | Implementation of Transferring RL for DC-DC Buck Converter Control via Duty Ratio Mapping | Sim-to-real transfer, buck converter | New-2026-05-23: verified via dblp/IEEE Xplore metadata |
| `lee2024reinforcement` | 2024 | Journal (IEEE Access) | RL-Based Control of DC-DC Buck Converter Considering Controller Time Delay | Time-delay aware DRL, buck converter, DSP deployment | New-2026-05-23: verified via dblp/IEEE metadata |
| `rajamallaiah2024deep` | 2024 | Journal (IEEE Access) | DRL Based Control Strategy for Voltage Regulation of DC-DC Buck Converter Feeding CPLs in DC Microgrid | Buck+CPL voltage regulation, DRL | New-2026-05-23: verified via dblp |
| `feng2025six` | 2025 | Journal (JESTPE) | Six Control DoF Modulation Scheme for DAB DC-DC Converters with DRL | DDPG DAB 6-DoF modulation, experimental prototype | New-2026-05-23: verified via multiple academic databases |
| `qashqai2025implementation` | 2025 | Journal (IEEE Access) | Implementation of DRL for Model-Free Switching and Control of 23-Level HPUC Converter | DQN direct switching, multilevel converter | New-2026-05-23: verified via ETS institutional repository |
| `ye2025soft` | 2025 | Journal (JESTIE) | SAC Algorithm Based RL Controller for Single-Inductor Dual-Output DC-DC Converter | SAC SIDO DC-DC converter control | New-2026-05-23: verified via UWA repository |
| `wan2024safety` | 2024 | Journal (TIE) | Safety-Enhanced Self-Learning for Optimal Power Converter Control | Safe online RL, VSC, physical hardware validation | New-2026-05-23: verified via DTU Orbit/IEEE metadata |
| `liu2024predictive` | 2024 | Journal (TIE) | Predictive Control of VSI: An Online RL Solution | Online RL FCS-MPC, Lyapunov stability, VSI | New-2026-05-23: verified via multiple academic databases |
| `liu2024event` | 2025 | Journal (TPE) | Event-Driven Based RL Predictive Controller for Three-Phase NPC Converters Using Online Approximators | Event-driven RL-MPC, NPC converter, online NN | New-2026-05-23: verified via IEEE metadata |
| `zhou2023drl` | 2024 | Journal (JESTPE) | DRL-Based Parameter Self-Configuration Mechanism of Nonsmooth Control for DC Microgrids Feeding CPLs | SAC parameter self-configuration, CPL microgrid | New-2026-05-23: verified via IEEE Xplore metadata |
| `liu2024learning` | 2024 | Journal (TPE) | Learning-Based Resilient FCS-MPC for Power Converters Under Actuator FDI Attacks | RL resilient MPC, cybersecurity | New-2026-05-23: verified via IEEE metadata |
| `zeng2025physics` | 2025 | Journal (TTE) | Physics-Informed Deep Transfer RL for ISOP-DAB APM in Electrical Aircraft | Transfer RL, ISOP-DAB, multi-agent coordination | New-2026-05-23: verified via CityU HK repository |
| `zeng2025multi` | 2025 | Journal (TPE) | Multi-Objective Controller Design for Grid-Following Converters With Easy Transfer RL | Transfer RL, grid-following, multi-objective | New-2026-05-23: verified via NTU Singapore repository |
| `abdulkader2024adaptive` | 2024 | Journal (IEEE Access) | Adaptive Voltage Control of Single-Inductor 3x Multilevel Converters Using Multi-Agent Approximate Q-Learning | Multi-agent Q-learning, DC microgrid | New-2026-05-23: verified via IEEE metadata |
| `dong2024data` | 2024 | Journal (TCAS-I) | Data-Driven Distributed H-infinity Current Sharing Consensus Optimal Control of DC Microgrids via RL | Distributed RL, current sharing, H-infinity | New-2026-05-23: verified via X-MOL metadata |
| `gallardo2024reinforcement` | 2024 | Journal (TIE) | RL-Based False Data Injection Attacks Detector for MMCs | RL FDI detector, MMC cybersecurity, HIL | New-2026-05-23: verified via IEEE/DTU metadata |
| `ahmadian2024empowering` | 2024 | Journal (IEEE Access) | Empowering Dynamic Active and Reactive Power Control: DRL Controller for 3-Phase Grid-Connected EVs | TD3 EV charger, V2G, adjacent domain | New-2026-05-23: verified via IEEE metadata |
| `wu2025deep` | 2025 | Journal (IEEE/CAA JAS) | Deep Synchronization Control of Grid-Forming Converters: A RL Approach | DDPG grid-forming, Lyapunov-constrained, adjacent | New-2026-05-23: verified via IEEE metadata |
| `balouji2025deep` | 2025 | Journal (TIA) | DRL Enabled Inverters: Strengthening RES Integration in Grids With Electric Arc Furnaces | DDPG grid-supporting inverter, adjacent domain | New-2026-05-23: verified via IEEE/Semantic Scholar |
| `gao2023artificial` | 2023 | Journal (OJIA) | AI Techniques for Enhancing Performance of Controllers in Power Converter-Based Systems---Overview | AI controller overview, supplementary | New-2026-05-23: verified via Semantic Scholar |
| `ding2024deep` | 2024 | Journal (Energies) | Deep and RL in VSG: A Comprehensive Review | DRL for VSG survey, supplementary | New-2026-05-23: verified via MDPI |
| `oshnoei2024grid` | 2024 | Conference (IPEMC-ECCE Asia) | Grid Impedance Shaping for GFM Inverters: A SAC-DRL Algorithm | SAC grid-forming, dSPACE experimental, adjacent | New-2026-05-23: verified via Aalborg Univ. repository |
| `zandi2023voltage_quasi` | 2023 | Journal (Control Eng. Practice) | Voltage Control of a Quasi Z-Source Converter Under CPL Using RL | RL direct switch control, quasi-Z-source, supplementary | New-2026-05-23: verified via multiple databases |

## Year Distribution After Expansion

Estimated new year distribution (including all bib entries):
- 2014--2020 (foundational + early application papers): ~35 entries (~35%)
- 2021--2022 (transition period): ~20 entries (~20%)
- 2023--2026 (recent papers, including new additions): ~45 entries (~45%)

With the 23 new 2023--2026 entries added, the proportion of recent papers rises significantly. When counting only PE application papers (excluding foundational algorithms, theory papers, and surveys), the 2023--2026 ratio improves from ~29% (11/38) to ~55% (34/62). Further additions from the evidence table's candidate pool (many of which are 2023 conference papers) would push this above 60%.

Until row-level verification is complete, Paper A may only claim that these are **candidate sources** from the previous control section. It must not claim exact algorithm distribution, adoption timeline, or comparative performance.
