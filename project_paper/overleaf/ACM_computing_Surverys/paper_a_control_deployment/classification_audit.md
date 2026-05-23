# Paper A Classification Audit

## Audit Position

The previous algorithm-distribution figure, timeline narrative, and summary tables are not safe to reuse. Reviewer 4 identified enough classification errors that the entire classification layer must be treated as contaminated until re-audited from source papers.

## Explicit Reviewer-Flagged Corrections to Verify

| Prior label/problem | Reviewer flag | Required action |
|---|---|---|
| Reference `[75]` placed in Q-learning group | Reviewer says it used DQN | Locate `[75]` in the old numbering, map to BibTeX key, verify source method, then relabel or remove. |
| Reference `[49]` placed as DQN | Reviewer says it used DDQN | Locate old `[49]`, verify method, update all tables/figures. |
| References `[51]` and `[64]` placed as DDQN | Reviewer says they used DQN | Locate old numbers, verify method, update all tables/figures. |
| Reference `[88]` placed as DDPG | Reviewer says it used TD3 | Locate old `[88]`, verify method, update all tables/figures. |
| Reference `[56]` used as A3C paper | Reviewer says it is MADDPG | Locate old `[56]`, verify method, remove from A3C group if correct. |
| Three SAC papers claimed | Reviewer says two are not SAC: `[97]` DDPG and `[103]` Q-learning | Locate old `[97]` and `[103]`, verify source method, rebuild SAC evidence from scratch. |
| Reference `[116]` categorized as TD3 in Table II but PPO in Table IX | Internal inconsistency | Locate old `[116]`, verify method, enforce one label across evidence table, tables, and prose. |

## Rebuilt Classification Dimensions

Paper A should not classify works only by algorithm family. The safer CSUR taxonomy uses multiple independent axes:

| Axis | Allowed values | Reason |
|---|---|---|
| Control role | Direct policy control; hybrid parameter tuning; modulation optimization; energy management; multi-agent coordination; safety/stability wrapper; benchmark/toolbox | Prevents shallow algorithm lists. |
| Action interface | Switching action; duty ratio; phase shift; modulation parameter; controller gain; power setpoint; maintenance/dispatch action | Links RL to the actual control variable. |
| Safety mechanism | None reported; reward penalty; constraint projection; Lyapunov/barrier condition; runtime shield; robust/MPC wrapper; formal verification | Addresses safety/stability critique. |
| Validation maturity | Simulation; HIL; real-time controller; embedded prototype; field/industrial evidence | Separates academic from deployment-ready work. |
| Evidence maturity | Journal; conference proof-of-concept; adjacent-domain transfer; benchmark/toolbox; review | Prevents overclaiming from low-maturity evidence. |
| Computation stage | Offline training; online training; offline inference only; online adaptation; on-chip learning | Addresses offline/online computational burden. |

## Timeline Policy

The old stage labels such as "Value-Based Learning (2015--2017)" must not be reused. A replacement timeline can only be used if it separates:

1. Original AI/RL algorithm publication year.
2. First verified PEC or energy-conversion adoption year.
3. Evidence maturity at adoption.
4. Deployment maturity at adoption.

If those four fields cannot be verified, Paper A should replace the timeline with a deployment-readiness map.

## Red/Yellow Batch 1 Resolution

The first high-risk classification batch is recorded in `classification_table_red_yellow_batch1.md` and `classification_table_red_yellow_batch1.csv`.

| Key | Safe label | Unsafe old-style label to avoid |
|---|---|---|
| `hajihosseini2020dc` | Actor-critic DRL-assisted ULM gain adaptation; real-time deployment evidence | Any named DDPG/PPO/SAC/TD3/DQN label |
| `meng2022novel` | TD3-assisted nonlinear/backstepping compensation | Direct policy control or generic DDPG |
| `fathollahi2023robust` | Conditional SAC claim from secondary source only; not counted | Counted SAC paper |
| `gheisarnejad2022reducing` | PPO-assisted MFSMC coefficient tuning with OPAL-RT HIL | Direct switching/control policy |
| `khooban2022smartenance` | DDPG-assisted non-integer MPC coefficient design | Maintenance/PHM paper or direct DDPG control |
