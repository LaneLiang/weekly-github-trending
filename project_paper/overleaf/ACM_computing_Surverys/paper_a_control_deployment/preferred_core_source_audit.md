# Preferred-Core Source-Level Audit for Paper A

This file audits the 19 preferred-core journal references before they are allowed to support Paper A's main claims. The purpose is to prevent the classification errors identified in the previous TPEL reviews.

## Status Labels

| Label | Meaning |
|---|---|
| Verified-source | Algorithm/control role/validation evidence confirmed from a DOI page, publisher page, institutional repository page, or source PDF. |
| Metadata-only | Venue and title are confirmed from local BibTeX, but algorithm or validation details require source/PDF verification. |
| Conditional-keep | May remain in the evidence base only for a narrow claim. |
| Reclassify | Should not be used under the old category or old claim. |

## Audited Rows

| Key | Venue tier | Algorithm/control evidence | System/control role | Validation evidence | Decision |
|---|---|---|---|---|---|
| `gheisarnejad2020iot` | Preferred-core: TPE | Verified-source: institutional page states DDPG actor-critic is used to tune ADRC coefficients online. | IoT-based DC-DC buck converter feeding CPLs; hybrid adaptive ADRC tuning. | Verified-source: real-time testbed with CoAP and Wi-Fi network; packet loss and interfering traffic evaluated. | Keep as high-value real-time implementation evidence. |
| `hajihosseini2020dc` | Preferred-core: TPE | Verified-source-limited: Aarhus Pure abstract states actor-critic DRL architecture incorporated into an ultra-local model controller; exact named algorithm is not visible from accessible source. | DC/DC converter / buck-boost converter context feeding CPLs; online learning adjusts feedback control gains. | Verified-source: dSPACE MicroLabBox outcomes on a real-time testbed are reported. | Keep as real-time actor-critic deployment evidence; do not count as DDPG/PPO/SAC/TD3/DQN. |
| `jiang2023stability` | Preferred-core: TPE | Verified-source metadata: title and DOI page identify DRL-assisted stability-oriented multiobjective control design. | Power converters; stability-oriented multiobjective control. | Metadata-only: validation details still require source/PDF inspection. | Keep as high-priority stability evidence, but verify experimental setup before strong claims. |
| `wang2023improved` | Preferred-core: TPE | Metadata-only: title says model-free active disturbance rejection deadbeat predictive current control, not explicitly DRL. | PMSM current control; may be comparator rather than DRL evidence. | Metadata-only. | Reclassify as comparator/adjacent unless source confirms RL relevance. |
| `ye2024deep` | Preferred-core: TPE | Verified-source: institutional repository abstract states DDPG-based RL controller. | SIMO DC-DC converter; multivariable voltage control and cross-regulation mitigation. | Verified-source: simulations and experiments are reported. | Keep as recent TPE experimental DRL control evidence. |
| `zeng2022autonomous` | Preferred-core: TPE | Verified-source metadata: IEEE Xplore title identifies multiagent DRL-based method. | ISOP-DAB converter in DC microgrid; input voltage sharing and triple-phase-shift modulation. | Metadata-only: validation details require PDF/source inspection. | Keep for multi-agent DAB coordination after validation check. |
| `zeng2022multiagent` | Preferred-core: TPE | Verified-source metadata: IEEE Xplore title identifies multiagent DRL-aided control. | ISOP DAB converter; output current sharing. | Metadata-only: validation details require PDF/source inspection. | Keep for multi-agent DAB current-sharing evidence after validation check. |
| `gheisarnejad2020novel` | Preferred-core: TIE | Verified-source metadata: DOI-indexed page confirms nonlinear DRL controller for DC-DC buck converters. | DC-DC buck converter nonlinear control. | Metadata-only: validation details require source/PDF inspection. | Keep as core nonlinear DRL converter-control evidence. |
| `meng2022novel` | Preferred-core: TIE | Verified-source: KTH/SwePub abstract states DRL-based backstepping control with DRL compensation; keywords identify twin-delayed deep deterministic policy gradient. | DAB converter with CPLs; hybrid nonlinear/backstepping compensation. | Verified-source: KTH/SwePub abstract states experiments verify effectiveness. | Keep; classify as hybrid nonlinear control with DRL compensation, likely TD3 pending PDF. |
| `qie2022new` | Preferred-core: TIE | Metadata-only: title says robust integral reinforcement learning. | Interleaved DC/DC boost converter control. | Metadata-only. | Keep pending source validation. |
| `tang2020reinforcement` | Preferred-core: TIE | Metadata-only: title says reinforcement-learning-based efficiency optimization. | DAB DC-DC converter; triple-phase-shift modulation efficiency optimization. | Metadata-only. | Keep pending source validation. |
| `tang2022deep` | Preferred-core: TIE | Metadata-only: title says DRL-aided variable-frequency triple-phase-shift control. | DAB converter modulation/control. | Metadata-only. | Keep pending source validation. |
| `wei2015reinforcement` | Preferred-core: TIE | Metadata-only: title says reinforcement-learning-based MPPT. | Wind energy conversion system MPPT. | Metadata-only. | Keep only as historical RL/MPPT evidence; do not use as DRL maturity evidence. |
| `zeng2023deep` | Preferred-core: TIE | Metadata-only: title says DRL-enabled distributed uniform control. | DC solid-state transformer in DC microgrid; distributed control. | Metadata-only. | Keep pending source validation. |
| `cui2023adaptive` | Preferred-core: TCAS-I | Metadata-only: title says generalized predictive control via DRL. | DC/DC converter; hybrid predictive-control horizon tuning. | Metadata-only. | Keep pending source validation. |
| `9521987` | Preferred-core: TCAS-II | Metadata and DOI available in local BibTeX; keywords include deep reinforcement learning and large-signal stability. | DC-DC buck converter feeding CPLs; voltage regulation. | Metadata-only: validation details require source/PDF inspection. | Keep pending source validation. |
| `fathollahi2023robust` | Preferred-core: TCAS-II | Secondary-confirmed: Power Electronics News summary identifies SAC parameter tuning, but accessible Aarhus/DOI metadata does not expose method-section detail. | Full-bridge converters feeding CPLs; stabilization. | Secondary-confirmed only: simulation and HIL/real-time examinations are reported by secondary source. | Conditional-keep; do not use in algorithm-count figures until PDF or official abstract confirms SAC and validation. |
| `gheisarnejad2022reducing` | Preferred-core: TCAS-II | Verified-source: Aarhus abstract states PPO actor-critic tunes MFSMC coefficients. | DC MG with parallel boost converters feeding CPLs; hybrid MFSMC parameter tuning. | Verified-source: OPAL-RT HIL simulations. | Keep as PPO-assisted robust-control and HIL evidence. |
| `khooban2022smartenance` | Preferred-core: TCAS-II | Verified-source: Aarhus abstract states DDPG actor-critic tunes coefficients embedded in non-integer MPC. | DC/DC converters with CPLs in full-electric ferry ship; hybrid MPC parameter design. | Verified-source: experimental results with comparative analysis are reported; exact platform still needs PDF. | Reclassify into Paper A hybrid MPC/DRL control, not Paper C maintenance. |

## Immediate Findings

1. The old control section over-included papers whose titles do not clearly indicate DRL or RL. These must not support algorithm-distribution claims.
2. The strongest immediately usable Paper A evidence is concentrated around real-time implementation, DDPG-based buck/SIMO control, stability-oriented DRL, and multi-agent DAB/SST control.
3. Several preferred-core papers are still only metadata-confirmed. They remain in the candidate evidence base, but they cannot yet support strong ACM/CSUR synthesis claims.
4. The red/yellow batch classification table is now recorded in `classification_table_red_yellow_batch1.md` and `.csv`. `hajihosseini2020dc` is verified enough for real-time actor-critic deployment evidence but not named algorithm-family counts. `fathollahi2023robust` remains conditional and must not enter SAC counts until source/PDF evidence is obtained.

## Sources Used in This Audit

- Institutional publication page for `gheisarnejad2020iot`, which reports DDPG actor-critic tuning of ADRC coefficients and real-time IoT testbed validation.
- UWA institutional repository page for `ye2024deep`, which reports DDPG-based RL control for SIMO DC-DC converters with simulations and experiments.
- IEEE Xplore pages or DOI-indexed pages for `zeng2022autonomous`, `zeng2022multiagent`, `jiang2023stability`, and `gheisarnejad2020novel`.
- Local `References.bib` metadata for rows labelled metadata-only.
