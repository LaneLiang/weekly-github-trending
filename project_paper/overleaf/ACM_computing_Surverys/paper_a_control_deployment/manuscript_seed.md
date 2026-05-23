# Paper A Manuscript Seed

**Recommended title:** Deep Reinforcement Learning for Real-Time Control of Power Electronic and Energy Conversion Systems: A Survey of Safety, Deployment, and Coordination

## Abstract Draft

Deep reinforcement learning has become a prominent candidate for adaptive control in power and energy conversion systems, where nonlinear dynamics, switching constraints, parameter drift, and distributed operating conditions challenge conventional model-based controllers. Existing surveys have mainly catalogued applications by converter type or algorithm family, but this organization obscures the computing questions that determine whether learned controllers can be trusted in real-time systems: what the agent controls, how safety is enforced, how simulation policies transfer to hardware, how much computation is required online, and how coordination scales across converter-dense networks. This survey reframes DRL-based converter control through a deployment-centered taxonomy covering control role, action interface, safety mechanism, validation maturity, computational burden, and coordination scope. It distinguishes archival evidence from proof-of-concept studies, separates offline training from online inference and adaptation, and identifies where model-based power-electronics theory remains indispensable. The resulting synthesis provides a roadmap for moving DRL controllers from simulation demonstrations toward reproducible, safety-aware, and hardware-efficient deployment.

## Contribution Draft

This survey makes four contributions.

1. It introduces a deployment-centered taxonomy for DRL-based control of power and energy conversion systems, organizing prior work by control role, action interface, safety mechanism, validation maturity, computational burden, and coordination scope.
2. It establishes an evidence-audit protocol that separates journal evidence, conference proof-of-concept studies, adjacent-domain transfer, and hardware-validated work before drawing readiness conclusions.
3. It synthesizes safety and stability mechanisms for learned converter control, distinguishing reward shaping from stronger approaches such as constrained optimization, Lyapunov/barrier conditions, runtime shielding, and robust-control wrappers.
4. It develops a research agenda for reproducible and deployable DRL control, emphasizing benchmark metadata, offline/online computation, embedded implementation, and multi-agent coordination under communication constraints.

## Synthesis-First Section Seeds

### DRL in the Converter Control Stack

The central question is not which DRL algorithm appears most often, but where the learned policy enters the control stack. In direct-control studies, the policy may select switching actions, duty ratios, phase shifts, or power setpoints. In hybrid-control studies, the policy tunes gains, weighting factors, prediction horizons, or modulation parameters while a conventional controller preserves part of the control structure. In coordination studies, multiple agents distribute voltage, current, frequency, or power-sharing decisions across converter modules or energy interfaces. This distinction is essential because the same algorithm family can have very different safety and computational implications depending on whether it directly actuates a switch or only updates a supervisory parameter.

### Safety and Stability Are Deployment Requirements, Not Future Work

For safety-critical converters, reward shaping alone is not a sufficient safety mechanism. A reward penalty can discourage overvoltage, overcurrent, or unstable transients during training, but it does not certify that unsafe actions are impossible during deployment. Paper A should therefore evaluate each work by the strongest safety mechanism it reports: reward-only shaping, constrained action projection, Lyapunov or barrier conditions, robust or MPC-based wrappers, runtime shielding, or post-training validation under disturbances. This framing directly addresses the prior rejection concern that safety and stability were mentioned without sufficient rigor.

### Offline and Online Computation Must Be Separated

Computational burden has at least four separate meanings in learned converter control. Offline training cost determines whether the method can be reproduced and adapted to new operating regimes. Online inference latency determines whether the learned policy fits the switching or supervisory control period. Memory footprint determines whether the policy can run on embedded DSP, FPGA, or SoC hardware. Online adaptation determines whether the controller can track aging, topology changes, or load variation without unsafe exploration. A CSUR-ready treatment should report these dimensions separately rather than using generic statements such as "high computational cost."

### When Not to Use DRL

DRL should not be presented as a universal replacement for power-electronics theory. If an accurate low-order model exists, the operating envelope is narrow, safety constraints are hard, and latency budgets are tight, classical control, MPC, robust control, or adaptive control may provide clearer guarantees with lower verification cost. DRL becomes more compelling when the control problem involves high-dimensional observations, nonlinear or changing operating regimes, multi-objective tradeoffs, or distributed decision-making where hand-designed policies are brittle. This negative guidance is necessary for credibility with both CSUR and power-electronics reviewers.

## Research Agenda Template

Each future direction must follow this format:

| Direction | Bottleneck | Candidate computing method | Validation metric | Deployment scenario |
|---|---|---|---|---|
| Safety-guaranteed DRL | Unsafe exploration and uncertified actions | Lyapunov-constrained RL, control barrier functions, runtime shields | Constraint violation rate, worst-case transient bound, certified safe action ratio | DC/DC converters feeding CPLs; DAB converters; grid-tied inverters |
| Reproducible benchmarks | Incomparable tasks and missing training budgets | Standardized benchmark metadata and open simulation/HIL suites | Reproduction error, training budget, baseline coverage | Buck/boost, DAB, MMC, microgrid converter tasks |
| Embedded policies | Latency and memory constraints | Quantization, distillation, hardware-aware neural architecture search | Inference latency, memory footprint, switching-period compatibility | DSP/FPGA/SoC control platforms |
| Multi-agent coordination | Communication limits and non-stationarity | Centralized training/decentralized execution, federated or hierarchical RL | Stability under packet loss, coordination error, scalability | Modular converters, DC microgrids, converter-dense networks |
