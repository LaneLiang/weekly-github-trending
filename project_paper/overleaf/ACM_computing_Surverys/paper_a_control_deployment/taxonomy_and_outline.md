# Paper A Taxonomy and CSUR Outline

**Recommended title:** Deep Reinforcement Learning for Real-Time Control of Power Electronic and Energy Conversion Systems: A Survey of Safety, Deployment, and Coordination

**Previous working title:** Deep Reinforcement Learning for Real-Time Control of Power and Energy Conversion Systems: A Survey of Safety, Deployment, and Coordination

## Title Assessment

The current title direction is suitable for CSUR because it foregrounds a computing topic (deep reinforcement learning), a deployment setting (real-time control), and three synthesis axes (safety, deployment, coordination). The recommended revision adds "Power Electronic" explicitly so the title is not too broad, while keeping "Energy Conversion Systems" to include DAB, SST, drives, microgrids, and converter-dense CPS examples.

Rejected alternatives:

| Alternative | Reason not preferred |
|---|---|
| Deep Reinforcement Learning for Power Electronics: A Survey | Too broad and likely to duplicate the rejected TPEL review framing. |
| Deep Reinforcement Learning for Power Electronic Converter Control | Too narrow; weak signal for deployment, safety, and coordination. |
| Safe and Deployable Reinforcement Learning for Power Electronic Systems | Strong CSUR signal, but underplays the existing DRL literature base and may sound like a methods paper. |

## Core CSUR Contribution

Paper A is not a survey of "which converter used which DRL algorithm." Its contribution is a computing-oriented framework for understanding how learning-based control policies move from simulation to real-time energy-conversion deployment.

## Proposed Taxonomy

| Layer | Question answered | Categories |
|---|---|---|
| Control role | What does the learned agent actually decide? | Direct switch/duty/phase control; hybrid gain tuning; modulation optimization; energy management; distributed coordination; safety wrapper. |
| Learning architecture | How is the policy optimized? | Value-based; policy-gradient; actor-critic; model-based/model-informed RL; multi-agent RL; imitation/RL hybrids. |
| Safety and stability | How is unsafe exploration or unsafe execution constrained? | Reward-only shaping; constrained policy optimization; Lyapunov/barrier certificates; MPC or robust-control shields; runtime monitors; post-training validation. |
| Sim-to-real path | How does the method leave simulation? | Domain randomization; HIL; real-time control implementation; embedded inference; hardware-in-the-loop plus fault injection; field demonstration. |
| Computational burden | Where is computation paid? | Offline training; online training; online inference; online adaptation; memory footprint; latency budget; retraining frequency. |
| Coordination scope | How many decision makers are involved? | Single converter; cascaded converter-drive system; modular converter; microgrid/energy system; multi-agent distributed network. |

## Figure Plan

| Figure | Purpose | Reviewer issue addressed |
|---|---|---|
| Fig. 1: Control-role stack | Shows where DRL enters the control loop. | R2-5, R3-4 |
| Fig. 2: Safety and deployment ladder | Separates simulation, HIL, embedded, and field readiness. | R1-5, R3-2 |
| Fig. 3: Offline/online computation pipeline | Separates training, inference, memory, latency, and adaptation. | R2-8, R3-4 |
| Fig. 4: Evidence maturity map | Plots works by source maturity and validation maturity. | R1-4, R4-3 |

## Outline

1. **Introduction**
   - Motivate real-time control and deployment, not broad lifecycle coverage.
   - State the gap: existing reviews aggregate applications but do not explain deployment readiness, safety mechanisms, or computing costs.
   - Contributions: taxonomy, evidence audit, deployment-readiness synthesis, and research agenda.

2. **Scope and Review Method**
   - Define included systems: power electronic converters and closely coupled energy-conversion systems.
   - Define exclusion rules: design-only topology synthesis moves to Paper B; maintenance-only PHM moves to Paper C.
   - Explain evidence fields and source weighting.

3. **DRL in the Real-Time Control Stack**
   - Direct control of switches, duty ratios, phase shifts, and power setpoints.
   - Hybrid control: DRL as tuner, compensator, or supervisor for classical controllers.
   - Coordination: multi-agent and distributed settings.

4. **Algorithmic Families Through Control Interfaces**
   - Compare algorithm families by action interface, stability behavior, sample efficiency, and control-loop compatibility.
   - Avoid unsupported distribution claims until evidence audit is complete.

5. **Safety, Stability, and Certification**
   - Reward shaping is not enough.
   - Discuss constrained RL, Lyapunov/barrier methods, runtime shielding, robust-control wrappers, and post-training verification.
   - Include "when not to use DRL."

6. **Sim-to-Real and Deployment Readiness**
   - Separate simulation, HIL, real-time implementation, embedded inference, and field evidence.
   - Discuss sensor noise, EMI, thermal drift, switching nonidealities, and latency.

7. **Computational Efficiency**
   - Offline training cost.
   - Online inference latency.
   - Memory footprint and quantization.
   - Online adaptation and retraining.

8. **Coordination in Converter-Dense Systems**
   - Single-agent versus multi-agent control.
   - Modular converters, ISOP/ISOS DAB systems, SSTs, DC microgrids, and converter-dense energy networks.
   - Communication delay, packet loss, partial observability, non-stationarity, and scalability.

9. **Evidence Synthesis**
   - Synthesize by control role, not converter type alone.
   - Summarize verified-only algorithm evidence.
   - Map evidence maturity against deployment maturity.
   - Separate direct policy control, hybrid nonlinear control, MPC/SMC/ADRC tuning, modulation optimization, and multi-agent coordination.

10. **Open Benchmarks and Reproducibility**
   - Explain why old timeline/distribution claims failed.
   - Propose benchmark metadata: converter model, task, disturbance, controller baseline, training budget, safety constraints, and hardware target.

11. **Research Agenda**
   - Safety-guaranteed learning.
   - Reproducible benchmarks.
   - Hardware-aware policies.
   - Multi-agent coordination under communication constraints.
   - Hybrid model-based plus learning-based control.

12. **Conclusion**
   - Summarize DRL as a deployable control technology only when safety, validation, and computational constraints are treated as first-class design variables.

## Section Responsibility Map

| Section | Main job | What must not happen |
|---|---|---|
| Introduction | Sell the CSUR computing gap and contribution. | Do not retell the whole PEC application history. |
| Scope and Review Method | Define evidence gates and A/B/C boundaries. | Do not include design automation or PHM maintenance as Paper A contributions. |
| DRL in the Real-Time Control Stack | Explain what the agent controls. | Do not classify papers only by DQN/DDPG/TD3/PPO/SAC. |
| Algorithmic Families Through Control Interfaces | Link algorithms to action interfaces and control-loop constraints. | Do not make unverified algorithm-distribution claims. |
| Safety, Stability, and Certification | Separate reward penalties from stronger safety mechanisms. | Do not call empirical bounded waveforms "certified stability." |
| Sim-to-Real and Deployment Readiness | Rank validation maturity from simulation to field evidence. | Do not mix simulation, HIL, and hardware as equivalent evidence. |
| Computational Efficiency | Separate training, inference, memory, latency, and adaptation. | Do not use generic "high computational cost" statements. |
| Coordination | Treat multi-agent control as a deployment architecture problem. | Do not collapse microgrid energy management into converter control without explaining the interface. |
| Evidence Synthesis | Present verified-only maps and tables. | Do not reuse contaminated timeline or old algorithm-count figures. |
| Benchmarks and Reproducibility | Propose minimum reporting fields. | Do not invent benchmark availability. |
| Research Agenda | Give bottleneck-method-metric-scenario future directions. | Do not write vague future work. |
