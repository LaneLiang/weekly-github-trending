# Local ACM Template Setup Notes

This note records the local ACM template and font resources already downloaded for the CSUR manuscript split.

## Local Paths

| Resource | Path | Confirmed contents |
|---|---|---|
| ACM primary article template | `G:\blog\claude_code_useage\project_paper\overleaf\ACM_computing_Surverys\ACM_Journals_Primary_Article_Template` | `acmart.cls`, `ACM-Reference-Format.bst`, `sample-manuscript.tex`, `sample-base.bib`, `acmguide.pdf`, `README.txt` |
| Libertine font package | `G:\blog\claude_code_useage\project_paper\overleaf\ACM_computing_Surverys\libertine\libertine` | Type 1/TeX font resources: `.pfb`, `.tfm`, `.enc`, `.map` |

## Starting Point for Paper A

Use the local `sample-manuscript.tex` as the conversion reference for Paper A. The current sample uses:

```latex
\documentclass[manuscript,screen,review]{acmart}
```

This is appropriate as the first local review/submission-style draft class. The file must be renamed when adapted; do not edit ACM's sample file directly.

## Files to Copy into a Paper A ACM Draft Folder

When creating the first ACM-format Paper A draft, create a new folder such as:

```text
G:\blog\claude_code_useage\project_paper\overleaf\ACM_computing_Surverys\paper_a_control_deployment\acm_draft
```

Copy in:

- `acmart.cls`
- `ACM-Reference-Format.bst`
- a renamed copy of `sample-manuscript.tex`, for example `paper_a_control_deployment.tex`
- a new bibliography file, for example `paper_a_control_deployment.bib`
- only the figures used by Paper A

Do not copy the entire old IEEE project into the ACM draft folder. Bring content over section by section after the evidence table and taxonomy are verified.

## Metadata Cleanup Before Drafting

The ACM sample contains proceedings-oriented sample fields. For a CSUR journal manuscript:

- Replace the sample title, author blocks, affiliations, abstract, CCS concepts, and keywords.
- Remove or neutralize proceedings metadata such as `\acmConference`, `\acmBooktitle`, and `\acmISBN` unless current CSUR instructions say otherwise.
- Keep rights fields as placeholders until ACM provides final publication metadata.
- Use ACM reference style:

```latex
\bibliographystyle{ACM-Reference-Format}
\bibliography{paper_a_control_deployment}
```

## Font and Compile Notes

- The local Libertine package is a fallback for traditional TeX/pdfLaTeX font resolution.
- Do not add manual font hacks unless compilation fails and the failure is clearly font-related.
- Start with pdfLaTeX + BibTeX for the local conversion test.
- If using XeLaTeX or LuaLaTeX, verify that `acmart`'s Unicode-engine font path uses the expected Libertinus/unicode-math behavior and does not conflict with the local Libertine package.

## First Compile Test

The first compile test should be minimal:

1. Copy the ACM template files into `paper_a_control_deployment/acm_draft`.
2. Rename `sample-manuscript.tex`.
3. Replace the title and abstract only.
4. Compile before importing large sections from the IEEE draft.
5. Add bibliography and figures only after the minimal template compiles.

This staged approach prevents IEEE-specific commands, unsupported packages, or font setup issues from being mixed with manuscript-content problems.

