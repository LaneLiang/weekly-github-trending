# Paper A Next Verification Checklist

This checklist defines the next work package before any LaTeX rewriting. The aim is to close the most dangerous reviewer risks first.

## Phase 1: Source-Level Classification Audit

- [ ] Map old numeric references in reviewer comments (`[49]`, `[51]`, `[56]`, `[64]`, `[75]`, `[88]`, `[97]`, `[103]`, `[116]`) to BibTeX keys from the compiled manuscript bibliography.
- [ ] For each mapped paper, open the source PDF or official abstract and record the exact algorithm named by the authors.
- [ ] Mark each evidence-table row as one of: verified, corrected, adjacent-domain, comparator-only, or remove.
- [ ] Rebuild any algorithm-count figure only after all rows used in the figure are verified.

## Phase 2: Evidence Weighting

- [ ] Label source maturity: journal, conference proof-of-concept, benchmark/toolbox, review, or adjacent-domain transfer.
- [ ] Label validation maturity: simulation, HIL, real-time controller, embedded prototype, field/industrial evidence.
- [ ] Prevent conference-only studies from supporting strong deployment-readiness claims.
- [ ] Separate power-converter-specific evidence from adjacent systems such as motors, batteries, microgrids, wind farms, or wave energy converters.

## Phase 3: Paper A CSUR Rewrite Gate

- [ ] Replace the old timeline with a deployment-readiness map unless adoption years are source-verified.
- [ ] Add a related-review comparison table with recent DRL/power-electronics reviews.
- [ ] Draft the four planned concept figures before full prose expansion.
- [ ] Ensure every future direction includes bottleneck, method, validation metric, and deployment scenario.
- [ ] Add a "when not to use DRL" subsection to prevent universal-solution overclaiming.

## Phase 4: Readiness Definition

Paper A is ready for full manuscript rewriting only when:

- all rows used in claims are verified;
- algorithm labels are no longer inherited from the rejected draft;
- safety/stability claims use converter-specific or clearly marked transferable evidence;
- offline training, online inference, memory footprint, latency, and adaptation are separated;
- the introduction contribution list is visibly different from the rejected TPEL lifecycle framing.

