# ACM Submission Team Guide for CSUR Manuscripts

**Purpose:** This document translates ACM's official author and submission guidance into a practical team workflow for the three CSUR-oriented manuscripts. It should be used together with `reviewer_response_quality_gate.md` and each paper's evidence table.

**Primary official sources checked:** ACM Submissions, ACM Information for Authors, ACM LaTeX/TAPS guidance, ACM Reference Formatting, ACM Author Rights, ACM Publication Policies, and ACM Ethics and Plagiarism Policy.

## 1. ACM Submission Route

ACM distinguishes conference proceedings, ACM journal articles, and magazine/newsletter submissions. For the CSUR manuscripts, the relevant route is **ACM journal article submission**.

Team requirements:

- Use the journal's required online submission system. ACM states that all ACM journals and transactions, except JACM, use **Manuscript Central / ScholarOne**.
- Do not assume the submission portal from an old template. Before final submission, verify the current CSUR submission link from the CSUR journal page or ACM author resources.
- Prepare all manuscript metadata before submission: title, abstract, authors, affiliations, corresponding author, keywords, CCS concepts, funding information, conflict-of-interest information, and required files.

## 2. Manuscript Template and Source Preparation

ACM requires authors to use the **ACM Primary Article Template**. The workflow differs from IEEE templates and must not inherit IEEE-specific commands, bibliography styles, author blocks, or formatting assumptions.

Local project assets:

- ACM template folder: `G:\blog\claude_code_useage\project_paper\overleaf\ACM_computing_Surverys\ACM_Journals_Primary_Article_Template`
- Local template files confirmed: `acmart.cls`, `ACM-Reference-Format.bst`, `sample-manuscript.tex`, `sample-base.bib`, `acmguide.pdf`, `README.txt`
- Local Libertine font folder: `G:\blog\claude_code_useage\project_paper\overleaf\ACM_computing_Surverys\libertine\libertine`
- Local Libertine files confirmed: Type 1/TeX support files including `.pfb`, `.tfm`, `.enc`, and `.map`

Team requirements:

- Convert from `IEEEtran` to ACM's `acmart` template before CSUR submission.
- Use the downloaded `sample-manuscript.tex` as the immediate local starting point. Its own header says the submission/review class should be `\documentclass[manuscript,screen,review]{acmart}`.
- Treat `sample-manuscript.tex` as a sample, not as the final paper name. ACM's sample file explicitly says modified versions should be renamed.
- For journal submission, remove or replace proceedings-only metadata from the sample, such as `\acmConference`, `\acmBooktitle`, and `\acmISBN`, unless CSUR's current instructions require a specific form.
- Keep rights-management commands such as `\setcopyright`, `\copyrightyear`, `\acmYear`, and `\acmDOI` as placeholders until ACM provides final rights information. Do not invent final DOI or copyright values.
- Keep source clean for TAPS processing. Avoid manual spacing, manual line breaks for layout, hard-coded page fitting, and IEEE-specific formatting hacks.
- Use semantic LaTeX commands rather than visual workarounds. Examples: use proper sectioning, table, figure, algorithm, equation, and bibliography structures.
- Do not use unsupported packages or custom macros unless they are necessary and confirmed compatible with ACM/TAPS.
- Maintain one compile path for the submission version and one for any internal draft version if the team needs comments or colored change tracking.

Compile-chain note:

- The downloaded Libertine folder contains traditional Type 1/TeX font resources. Use it only if the local TeX distribution cannot find the required Libertine fonts through its normal font map.
- The downloaded `acmart` README notes that recent `acmart` versions switch to `unicode-math` and `libertinus` for Unicode engines. Therefore, the team must not mix pdfLaTeX-specific Libertine setup with XeLaTeX/LuaLaTeX-specific Unicode font configuration without testing.
- Preferred initial compile path for the local template is pdfLaTeX + BibTeX unless Paper A later needs Unicode-engine features. If switching to LuaLaTeX/XeLaTeX, create a separate compile note and verify fonts, bibliography, math, and TAPS compatibility.

## 3. TAPS and Production Readiness

ACM uses TAPS for production processing after acceptance. A manuscript that compiles locally may still fail production if the source violates ACM/TAPS expectations.

Team requirements:

- Keep figures, tables, algorithms, references, and appendices in production-safe formats.
- Do not rely on local fonts, local paths, or hidden files.
- Keep all graphics in a predictable folder and use portable file formats.
- Avoid over-customized table packages and figure placement tricks.
- Ensure all supplementary material is clearly separated from the main article source.
- Before submission, run a clean compile from a fresh folder containing only the files needed for the ACM manuscript.

## 4. References and Citation Quality

ACM requires careful, complete, and consistent references. For these CSUR manuscripts, reference quality is also a core scientific risk because the TPEL rejection specifically flagged wrong classifications and weak literature selection.

Team requirements:

- Every cited source must have a complete BibTeX entry: authors, title, venue, year, DOI or URL where available, volume/issue/pages where applicable.
- Prefer archival journal versions over conference versions when both exist.
- Conference papers may be used for emerging ideas, but they must be marked as proof-of-concept evidence unless journal or hardware validation exists.
- Reference metadata must be checked against the official publisher page, DOI, ACM Digital Library, IEEE Xplore, arXiv, or the paper PDF.
- No algorithm label may be inferred from title alone.
- Bibliography and evidence table must agree. If a citation is removed from the evidence table, it should not support a strong claim in the manuscript.
- Avoid citation padding. Each citation should support a specific sentence, classification, comparison, or claim.

## 5. CCS Concepts and Keywords

ACM submissions require ACM Computing Classification System concepts. CSUR is a computing journal, so CCS selection should emphasize the computing contribution rather than only the power-electronics application domain.

Recommended Paper A CCS direction:

- Computing methodologies -> Reinforcement learning
- Computer systems organization -> Embedded and cyber-physical systems
- Computer systems organization -> Real-time systems
- Software and its engineering or Computing methodologies categories may apply if the paper emphasizes verification, reliability, or learning frameworks.

Team requirements:

- Add CCS concepts only after the final taxonomy is stable.
- Ensure keywords match the CSUR framing: deep reinforcement learning, real-time control, cyber-physical systems, power electronic converters, safe reinforcement learning, embedded deployment, multi-agent coordination.
- Do not let keywords imply a paper scope broader than what the evidence table supports.

## 6. Accessibility Requirements

ACM expects accessible publications. Accessibility is not a cosmetic final step; it affects figures, tables, captions, and supplementary materials.

Team requirements:

- Every figure must have a meaningful caption that explains the takeaway, not just the visual content.
- Provide alt-text or descriptive text for important figures where the ACM workflow requests it.
- Avoid color-only encodings in taxonomy figures, maturity maps, and trend plots.
- Use readable contrast and distinguishable line styles or markers.
- Tables should be machine-readable where possible; avoid turning tables into images.
- Acronyms must be defined on first use.

## 7. Ethics, Plagiarism, and Prior Work

ACM's publication ethics rules require originality, proper attribution, and avoidance of plagiarism, self-plagiarism, redundant publication, and misleading presentation.

Team requirements:

- Do not split the original review mechanically into three overlapping submissions. The three manuscripts must have non-overlapping contributions, taxonomies, abstracts, figure sets, and claims.
- Reused text from the TPEL draft must be rewritten and reframed, not copied wholesale.
- Any overlap among Papers A/B/C must be limited to short shared background motivation.
- Maintain a cross-paper overlap log: shared citations are acceptable; shared paragraphs, tables, and figures are not.
- Do not submit two papers simultaneously if their scopes could be interpreted as duplicate or salami publication.
- Clearly cite all prior surveys and explain what each new CSUR paper adds.
- If AI assistance is used in drafting, the human authors must verify technical content, references, and classifications. Do not let generated text introduce unsupported claims.

## 8. Author Rights and Open Access Choices

ACM offers publication models and author-rights choices that affect copyright, licenses, repository posting, and open access.

Team requirements:

- Before submission, decide whether the team will use the standard ACM publishing route or an open access route.
- Confirm institutional agreements or funding mandates that may require open access.
- Keep the accepted manuscript, submitted manuscript, and final published version clearly separated.
- Do not post the final ACM-formatted version unless ACM's current author-rights policy allows it.
- Track funding acknowledgments and grant requirements early, because they may affect rights and open-access choices.

## 9. Artifact and Reproducibility Expectations

ACM encourages reproducibility and artifact review across many venues. Even if CSUR does not require artifact submission for a survey, reproducibility evidence will strengthen these papers.

Team requirements:

- Maintain a reproducible evidence table for every manuscript.
- For Paper A, preserve the classification audit trail: source PDF or official page, exact algorithm label, validation platform, and maturity level.
- For figures derived from the evidence table, keep scripts or spreadsheet formulas so the figure can be regenerated.
- Do not manually edit generated figures in ways that break traceability.
- Archive search queries, inclusion/exclusion criteria, and screening decisions.

## 10. Paper A Specific Compliance Plan

Paper A is the first CSUR target and must satisfy both ACM requirements and the TPEL rejection gates.

Mandatory pre-draft steps:

1. Finish `paper_a_control_deployment/evidence_table.md`.
2. Complete the reviewer-flagged classification audit for old numeric references `[49]`, `[51]`, `[56]`, `[64]`, `[75]`, `[88]`, `[97]`, `[103]`, and `[116]`.
3. Replace the old timeline with either a verified adoption timeline or a deployment-readiness map.
4. Build a related-review comparison table.
5. Build the four concept figures listed in `taxonomy_and_outline.md`.
6. Convert future directions into bottleneck-method-metric-scenario format.
7. Add a "when not to use DRL" subsection.

Submission-readiness test:

- A CSUR reader should understand the computing contribution even if they are not a power-electronics specialist.
- A power-electronics reviewer should see that safety, stability, hardware validation, and computation are treated rigorously.
- Every strong claim should trace to a verified row in the evidence table.

## 11. Paper B Specific Compliance Plan

Paper B should start only after Paper A taxonomy is stable.

Mandatory pre-draft steps:

1. Expand literature beyond PEC papers into AI-assisted CAD, EDA, graph generation, constrained search, and neural combinatorial optimization.
2. Define design automation inclusion/exclusion criteria.
3. Create a separate evidence table; do not reuse Paper A's control evidence table.
4. Build a taxonomy around representation, search method, constraint handling, objective evaluation, and benchmark reproducibility.
5. Position DRL against Bayesian optimization, evolutionary search, supervised surrogates, GNNs, and symbolic/programmatic design methods.

Submission-readiness test:

- The paper must read as a computing survey on design automation, not a power-electronics design review with DRL examples.

## 12. Paper C Specific Compliance Plan

Paper C requires the largest rebuild and should not be submitted until the PHM/CPS literature base is substantially expanded.

Mandatory pre-draft steps:

1. Separate monitoring, diagnosis, prognostics, prescription, and cyber-resilience.
2. Add POMDP/MDP maintenance scheduling literature.
3. Add cyberattack and cyber-physical fault response literature.
4. Add uncertainty-aware, risk-sensitive, continual, transfer, and federated learning literature.
5. Define what counts as converter-specific evidence versus adjacent CPS/PHM evidence.

Submission-readiness test:

- The paper must provide a decision-making framework for converter-dense CPS health management, not an expanded maintenance section.

## 13. Internal Team Roles

Recommended division of labor:

| Role | Responsibility |
|---|---|
| Evidence lead | Maintains evidence table, source verification, DOI/metadata checks, and classification audit. |
| Taxonomy lead | Owns computing taxonomy, figure logic, and non-overlap across A/B/C. |
| Domain lead | Checks converter/control/maintenance technical correctness. |
| ACM compliance lead | Checks template, TAPS compatibility, CCS, accessibility, rights, and submission files. |
| Writing lead | Converts synthesis into manuscript prose while preserving traceability. |

## 14. Final Pre-Submission Checklist

- [ ] Current ACM template used.
- [ ] Manuscript compiles from a clean folder.
- [ ] CCS concepts included.
- [ ] Keywords finalized.
- [ ] All references complete and checked.
- [ ] Every figure has caption and accessibility consideration.
- [ ] Evidence table archived.
- [ ] Reviewer-response gate closed or explicitly deferred.
- [ ] Related-review comparison included.
- [ ] Conference versus journal evidence separated.
- [ ] Timeline or trend claims source-verified.
- [ ] Future directions are actionable.
- [ ] Cross-paper overlap checked.
- [ ] Author rights/open access route decided.
- [ ] Submission metadata prepared.
