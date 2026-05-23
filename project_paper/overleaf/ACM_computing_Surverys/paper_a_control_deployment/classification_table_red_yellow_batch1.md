# Paper A Red/Yellow Batch 1 Classification Table

This table records the current source-verification status for the five papers most likely to cause fatal algorithm-classification errors. The classification rule is strict: a paper may enter algorithm-count figures only when the algorithm label, control role, and validation type are supported by a publisher page, institutional repository page, or source PDF. Secondary reporting can support a provisional note, but not authoritative statistics.

## Evidence Scale

| Evidence level | Meaning | Figure/table use |
|---|---|---|
| `Verified-source` | Method/control role/validation are confirmed by institutional/publisher metadata with abstract or source PDF. | May enter evidence tables and algorithm statistics if the algorithm label is explicit. |
| `Verified-source-limited` | Core method and validation are source-confirmed, but exact subalgorithm is not named. | May enter taxonomy/deployment tables; not algorithm-family counts beyond the verified level. |
| `Secondary-confirmed` | Details are available from a credible secondary technical report, while institutional/publisher page lacks abstract detail. | May be discussed as provisional; not counted in algorithm statistics. |
| `Unverified` | Title/venue/DOI only, or method/experiment unclear. | Do not classify; do not count. |

## Classification Table

| Key | Venue | Network evidence used | Algorithm label | Control role | System / target | Validation evidence | Paper A taxonomy placement | Count in algorithm figures? | Decision |
|---|---|---|---|---|---|---|---|---|---|
| `hajihosseini2020dc` | IEEE Transactions on Power Electronics (TPE), 2020 | Aarhus Pure abstract; Deakin metadata; DOI/Crossref | DRL with actor-critic architecture; exact named algorithm not specified in accessible source | DRL-adaptive tuning of ultra-local model (ULM) feedback controller gains through online NN learning | DC-DC converter / buck-boost converter context feeding constant power loads (CPLs) in DC microgrids | dSPACE MicroLabBox outcomes on a real-time testbed | Real-time deployment; hybrid adaptive control; stability-oriented CPL mitigation | **No** for DDPG/PPO/SAC/TD3/DQN counts; **yes** for actor-critic DRL deployment table | Keep as verified real-time deployment evidence; classify only as actor-critic DRL-assisted ULM gain adaptation. |
| `meng2022novel` | IEEE Transactions on Industrial Electronics (TIE), 2023 | KTH DiVA abstract and keywords; DOI/Crossref | Twin-delayed deep deterministic policy gradient (TD3) by keyword | DRL-based compensation around nonlinear disturbance observer and backstepping controller | Dual active bridge (DAB) converter feeding CPLs | Experiments verify effectiveness | Hybrid nonlinear control; DRL compensation; large-signal stability | **Yes**, as TD3, but only under hybrid compensation, not direct policy control | Keep; classify as TD3-assisted backstepping/nonlinear control. |
| `fathollahi2023robust` | IEEE Transactions on Circuits and Systems II: Express Briefs (TCAS-II), 2023 | Aarhus Pure bibliographic record; Power Electronics News secondary technical summary; DOI/Crossref | Secondary source says soft actor-critic (SAC); official accessible page lacks abstract confirmation | Secondary source says SAC tunes controller parameters in nonlinear controller law | DC/DC full-bridge converter feeding CPLs, telecom-power context | Secondary source says simulation and HIL/real-time examinations; official accessible page only confirms venue/DOI | Provisional robust nonlinear control / DRL parameter tuning | **No** until PDF or official abstract confirms SAC and validation | Conditional keep; do not use in algorithm-count figures yet. |
| `gheisarnejad2022reducing` | IEEE Transactions on Circuits and Systems II: Express Briefs (TCAS-II), 2022 | Aarhus Pure abstract and keywords; DOI/Crossref | Proximal policy optimization (PPO), actor-critic neural networks | PPO designs/tunes key coefficients of model-free sliding mode controller (MFSMC) | DC microgrid with parallel boost converters feeding CPLs | OPAL-RT hardware-in-the-loop (HIL) simulations | Hybrid robust-control parameter tuning; HIL validation; CPL stability | **Yes**, as PPO-assisted MFSMC parameter tuning | Keep as verified PPO/HIL evidence; not direct switching policy control. |
| `khooban2022smartenance` | IEEE Transactions on Circuits and Systems II: Express Briefs (TCAS-II), 2023 | Aarhus Pure abstract and keywords; DOI/Crossref | Deep deterministic policy gradient (DDPG), actor-critic neural networks | DDPG designs coefficients embedded in non-integer MPC | DC/DC converters with CPLs in full-electric ferry ship / onboard DC system | Experimental results with comparative analysis reported; exact hardware platform still needs PDF | Hybrid MPC parameter design; onboard DC converter stabilization | **Yes**, as DDPG-assisted non-integer MPC parameter design, with validation platform marked partial | Reclassify from maintenance to Paper A control/deployment taxonomy. |

## Batch Decision

| Outcome | Papers |
|---|---|
| Safe for taxonomy and deployment synthesis | `hajihosseini2020dc`, `meng2022novel`, `gheisarnejad2022reducing`, `khooban2022smartenance` |
| Safe for algorithm-count figures | `meng2022novel` as TD3; `gheisarnejad2022reducing` as PPO; `khooban2022smartenance` as DDPG |
| Safe only for broad actor-critic deployment, not named algorithm counts | `hajihosseini2020dc` |
| Not safe for algorithm-count figures yet | `fathollahi2023robust` |

## Source Links

- Hajihosseini et al. 2020: DOI `https://doi.org/10.1109/TPEL.2020.2977765`; Aarhus Pure and Deakin metadata were used for source-visible abstract/metadata.
- Meng et al. 2023: DOI `https://doi.org/10.1109/TIE.2022.3170608`; KTH DiVA page `https://kth.diva-portal.org/smash/record.jsf?pid=diva2:1721955`.
- Fathollahidehkordi et al. 2023: DOI `https://doi.org/10.1109/TCSII.2023.3270751`; Aarhus Pure bibliographic metadata and Power Electronics News secondary summary were used, but method/experiment remain not source-confirmed.
- Gheisarnejad Chirani et al. 2022: DOI `https://doi.org/10.1109/TCSII.2022.3194271`; Aarhus Pure abstract was used for PPO/MFSMC/HIL classification.
- Khooban 2023: DOI `https://doi.org/10.1109/TCSII.2022.3206230`; Aarhus Pure page `https://pure.au.dk/portal/en/publications/smartenance-dc-dc-on-board-power-converters`.
