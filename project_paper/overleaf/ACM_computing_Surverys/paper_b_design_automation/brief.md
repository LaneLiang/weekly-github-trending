# Paper B Brief: Computational Design Automation

**Working title:** Learning-Based Design Automation for Power Electronic Converters: A Survey of Graph Search, Reinforcement Learning, and Constraint-Aware Optimization

## Distinct Contribution

Paper B should not be framed as "DRL applications in converter design." It should be framed as a computing survey on learning-based design automation for power electronic converters. Its novelty is a taxonomy of computational search over converter topologies, parameters, and objectives.

## Scope

Included:

- Topology generation and topology exploration.
- Graph representations of circuits.
- Constraint-aware search and synthesis.
- Reinforcement learning, graph neural networks, evolutionary search, Bayesian optimization, and generative models for design-space exploration.
- Multi-objective design tradeoffs such as efficiency, power density, thermal behavior, component count, and manufacturability.

Excluded:

- Real-time control and deployment decisions, which belong to Paper A.
- Fault diagnosis, RUL, and maintenance scheduling, which belong to Paper C.

## Required Literature Expansion

- AI-assisted CAD and EDA.
- Graph generation and graph neural networks for physical systems.
- Neural combinatorial optimization.
- Program synthesis or symbolic search for circuits.
- Constraint satisfaction and constrained RL.
- AI4Science methods for design-space exploration.

## Reviewer-Gate Fixes

- R1-1: The analytical novelty is design automation, not lifecycle breadth.
- R1-6: The paper is separated from control and maintenance.
- R3-1: DRL must be positioned against Bayesian optimization, evolutionary algorithms, supervised surrogates, and graph search.
- R4-4: Future directions must be concrete: benchmark circuits, constraints, objective functions, simulator integration, and hardware validation.

## Provisional Outline

1. Introduction: PEC design as constrained computational search.
2. Review method and scope.
3. Circuit representations: netlists, graphs, adjacency matrices, and functional blocks.
4. Search paradigms: heuristics, evolutionary methods, Bayesian optimization, RL, GNN-guided search, and generative models.
5. Constraint handling and physical validity.
6. Multi-objective optimization and design tradeoffs.
7. Simulation, evaluation, and benchmark reproducibility.
8. Research agenda for trustworthy design automation.

