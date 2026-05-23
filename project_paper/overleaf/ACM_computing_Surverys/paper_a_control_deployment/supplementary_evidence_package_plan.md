# Paper A Supplementary Evidence Package Plan

This package is designed for ACM Computing Surveys review support. It contains only our own screening and classification data, not copyrighted IEEE PDFs.

## Files to Maintain

| File | Purpose | Submission readiness |
|---|---|---|
| `classification_table_red_yellow_batch1.md` | Human-readable audit table for the five highest-risk red/yellow papers. | Internal now; can be converted to supplementary appendix. |
| `classification_table_red_yellow_batch1.csv` | Machine-readable version for team checking and later supplement upload. | Suitable as supplemental material after final cleanup. |
| `evidence_table.md` | Master inventory of Paper A candidate sources. | Needs all high-value rows verified before submission. |
| `preferred_core_source_audit.md` | Venue-prioritized source-level audit for preferred-core journal papers. | Internal traceability file; can inform appendix. |
| `reading_notes_red_yellow_batch1.md` | Narrative notes explaining source evidence and unresolved classification limits. | Internal quality gate; can support reviewer-response traceability. |

## ACM-Oriented Data Policy

- Submit our own evidence tables and screening logs, not publisher PDFs.
- Every algorithm-family statistic must trace to a row with `Verified-source` evidence.
- Rows with `Secondary-confirmed` or weaker evidence may appear in prose only with cautious wording and must not enter algorithm-count figures.
- All supplementary rows must include DOI, venue, source URL, classification basis, and final inclusion/exclusion decision.

## Immediate Use in Paper A

1. Replace old algorithm-distribution counts with verified-only counts.
2. Treat `fathollahi2023robust` as a provisional example, not a counted SAC paper.
3. Use `hajihosseini2020dc` for real-time actor-critic deployment evidence, not for named algorithm-family statistics.
4. Move `khooban2022smartenance` from maintenance framing into hybrid MPC/DRL control.
