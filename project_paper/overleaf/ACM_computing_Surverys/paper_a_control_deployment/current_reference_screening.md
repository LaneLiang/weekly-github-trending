# Current Paper A Reference Screening

This file screens the 71 unique references extracted from the old control section against the user's preferred venue categories.

## Summary

| Category | Count | Action |
|---|---:|---|
| Preferred-core journal | 19 | Keep if source-level algorithm/validation details verify |
| Preferred-conference | 2 | Keep only as proof-of-concept/emerging evidence |
| Supplementary-high-quality | 3 | Keep only with explicit justification |
| Adjacent-context | 11 | Usually move to background/comparison or remove |
| Exclude-by-default | 36 | Remove from main Paper A evidence unless uniquely justified |

## Preferred-Core Journal Evidence

These papers match the user's preferred journal list and should form the backbone of Paper A after source-level verification.

| Key | Venue | Preliminary action |
|---|---|---|
| `gheisarnejad2020iot` | IEEE Transactions on Power Electronics | Keep: real-time implementation candidate |
| `hajihosseini2020dc` | IEEE Transactions on Power Electronics | Keep: real-time implementation candidate |
| `jiang2023stability` | IEEE Transactions on Power Electronics | Keep: high-priority stability evidence |
| `wang2023improved` | IEEE Transactions on Power Electronics | Keep if directly relevant to converter/motor-control comparison |
| `ye2024deep` | IEEE Transactions on Power Electronics | Keep: recent TPE control evidence |
| `zeng2022autonomous` | IEEE Transactions on Power Electronics | Keep: multi-agent ISOP-DAB evidence |
| `zeng2022multiagent` | IEEE Transactions on Power Electronics | Keep: multi-agent ISOP-DAB evidence |
| `gheisarnejad2020novel` | IEEE Transactions on Industrial Electronics | Keep: nonlinear DRL converter controller |
| `meng2022novel` | IEEE Transactions on Industrial Electronics | Keep: DAB intelligent nonlinear controller |
| `qie2022new` | IEEE Transactions on Industrial Electronics | Keep: robust integral RL control |
| `tang2020reinforcement` | IEEE Transactions on Industrial Electronics | Keep: DAB efficiency optimization |
| `tang2022deep` | IEEE Transactions on Industrial Electronics | Keep: DAB variable-frequency TPS control |
| `wei2015reinforcement` | IEEE Transactions on Industrial Electronics | Keep as historical MPPT evidence, not DRL maturity evidence |
| `zeng2023deep` | IEEE Transactions on Industrial Electronics | Keep: distributed SST/DC microgrid control |
| `cui2023adaptive` | IEEE Transactions on Circuits and Systems I: Regular Papers | Keep: hybrid predictive control and DRL tuning evidence |
| `9521987` | IEEE Transactions on Circuits and Systems II: Express Briefs | Keep: buck/CPL voltage control |
| `fathollahi2023robust` | IEEE Transactions on Circuits and Systems II: Express Briefs | Keep: robustness/stabilization evidence |
| `gheisarnejad2022reducing` | IEEE Transactions on Circuits and Systems II: Express Briefs | Keep if CPL/DC energy-system relevance verifies |
| `khooban2022smartenance` | IEEE Transactions on Circuits and Systems II: Express Briefs | Keep only if Paper A uses it for control, not maintenance |

## Preferred-Conference Evidence

These match preferred conference categories and can support early or emerging evidence only.

| Key | Venue | Preliminary action |
|---|---|---|
| `teng2020reinforcement` | IEEE Energy Conversion Congress and Exposition (ECCE) | Conditional keep as proof-of-concept |
| `zeng2021deep` | IEEE Energy Conversion Congress and Exposition (ECCE) | Conditional keep as proof-of-concept leading to later journal work |

## Supplementary-High-Quality Evidence

These are not in the user's explicit preferred list but are strong enough to inspect before removal.

| Key | Venue | Preliminary action |
|---|---|---|
| `book2021transferring` | IEEE Open Journal of Power Electronics | Keep if used for sim-to-real/real-world deployment evidence |
| `huangfu2022learning` | IEEE Journal of Emerging and Selected Topics in Power Electronics | Keep if used for large-signal stability evidence |
| `tang2021rl` | IEEE Journal of Emerging and Selected Topics in Power Electronics | Keep if used for DAB current-stress optimization |

## Adjacent-Context Evidence

These are not primary Paper A evidence. They may support broader computing or adjacent-system context only.

| Key | Venue | Preliminary action |
|---|---|---|
| `chen2024asynchronous` | Journal of the Franklin Institute | Move to adjacent multi-agent/battery context or remove |
| `li2023large` | IEEE Transactions on Transportation Electrification | Adjacent energy-conversion coordination; inspect |
| `liang2022multiagent` | IEEE Transactions on Industrial Informatics | Adjacent wind-farm coordination; likely background only |
| `pinthurat2023simultaneous` | IEEE Transactions on Industrial Informatics | Adjacent distribution systems; likely background only |
| `prag2021data` | IEEE Access | Comparator only; not RL evidence |
| `qashqai2023model` | IEEE Access | Adjacent/secondary; remove unless uniquely needed |
| `tang2021deep` | IEEE Transactions on Energy Conversion | Adjacent DAB/distributed-generation evidence; inspect |
| `traue2020toward` | IEEE Transactions on Neural Networks and Learning Systems | Benchmark/toolbox context; not converter journal evidence |
| `yan2022multiagent` | IEEE Transactions on Control of Network Systems | Multi-agent theory/context; not PEC-core |
| `yang2020deep` | IEEE Transactions on Intelligent Transportation Systems | Energy management context; likely remove from Paper A |
| `schenke2021deep` | IEEE Open Journal of the Industrial Electronics Society | Motor-control context; inspect or remove |

## Exclude-by-Default

These do not match the preferred journal/conference categories and should be removed from the main Paper A evidence base unless the team records a specific exception.

`10030117`, `10141314`, `10245391`, `10246775`, `10264605`, `9660319`, `9752938`, `alfred2021model`, `anugula2021deep`, `arianborna2023mppt`, `bo2022controller`, `chen2024control`, `chou2019maximum`, `dong2022generalized`, `dragoun2019adaptive`, `he2021weighting`, `hu2021novel`, `jiang2021application`, `jung2022reinforcement`, `kosuru2022deep`, `lee2023pwm`, `lu2021speed`, `mahazabeen2022performance`, `mao2022research`, `nicola2022comparative`, `nicola2022improved`, `nicola2023improved`, `qie2023new`, `ranjbaran2023reinforcement`, `wan2021reinforcement`, `weber2023steady`, `wu2021innovative`, `yin2021quantum`, `zandi2023voltage`, `zhou2023ai`, `zou2022optimization`

## Next Source-Level Work

1. Verify the 19 preferred-core journal papers first.
2. Verify whether the two ECCE papers have later journal versions; if yes, cite the journal versions instead.
3. Decide whether JESTPE and IEEE Open Journal of Power Electronics should be promoted to preferred-core or remain supplementary.
4. Remove exclude-by-default papers from Paper A draft unless they fill an otherwise missing taxonomy cell.

## Source-Audit Link

The first preferred-core source-level audit is recorded in `preferred_core_source_audit.md`. It identifies several conditional or reclassification cases that must not be used in algorithm-distribution figures until verified from source PDFs.
