# DOI Verification Audit - Round 2: Fix Report

**Date**: 2026-05-23
**Files modified**: `paper_a_control_deployment.bib`
**Files checked**: `paper_a_control_deployment.tex` (citation validity)

---

## Fix 1: `wu2021innovative` -- Ghost DOI, Replaced Entirely (CRITICAL)

**Before (BROKEN)**:
```bibtex
@inproceedings{wu2021innovative,
  title     = {An Innovative Deep Reinforcement Learning Controller for {DC/DC} {DAB} Converters Based on Deep Deterministic Policy Gradient},
  author    = {Wu, Jing and Wang, Benfei and Zhang, Xinan},
  booktitle = {Proceedings of the IEEE International Conference on Electrical Engineering and Mechatronics Technology (ICEEMT)},
  pages     = {329--333},
  year      = {2021},
  doi       = {10.1109/ICEEMT52412.2021.9602911}
}
```
- DOI `10.1109/ICEEMT52412.2021.9602911` unresolvable (zero search results, zero citations)
- Authors Jing Wu, Benfei Wang, Xinan Zhang -- wrong (3 people, belong to another paper)
- Conference ICEEMT -- wrong venue
- Pages 329-333 -- wrong

**After (VERIFIED)**:
```bibtex
@inproceedings{wu2021innovative,
  title     = {An Innovative Deep Reinforcement Learning Controller for {DC/DC} {DAB} Converters Based on Deep Deterministic Policy Gradient},
  author    = {Wu, Han and Tian, Jinjie and Jia, Yanbing and Meng, Xiangqi and Shi, Junyi and Zhao, Pei and Yan, Zhichao},
  booktitle = {Proceedings of the 2021 IEEE 5th Conference on Energy Internet and Energy System Integration (EI{\textsuperscript{2}})},
  pages     = {665--669},
  year      = {2021},
  address   = {Taiyuan, China},
  doi       = {10.1109/EI252483.2021.9713634},
  note      = {Verified via IEEE Xplore document 9713634 and Semantic Scholar. Original ghost DOI 10.1109/ICEEMT52412.2021.9602911 replaced.}
}
```
- DOI `10.1109/EI252483.2021.9713634` -- verified via IEEE Xplore document 9713634 and Semantic Scholar
- Authors: Han Wu, Jinjie Tian, Yanbing Jia, Xiangqi Meng, Junyi Shi, Pei Zhao, Zhichao Yan (7, all confirmed)
- Venue: IEEE EI2 2021, Taiyuan, China
- Pages: 665-669

**Tex impact**: Citation `\cite{wu2021innovative}` on line 253 still valid (same bib key, same paper title, same lead author surname Wu). No tex changes needed.

---

## Fix 2: `nicola2022comparative` -- Wrong Journal, Volume, Pages, DOI (CRITICAL)

**Before (BROKEN)**:
```bibtex
journal = {Mathematics},
volume  = {10},
number  = {23},
pages   = {4525},
doi     = {10.3390/math10234525}
```
- DOI `10.3390/math10234525` does not exist
- Journal claimed as "Mathematics" -- wrong

**After (VERIFIED)**:
```bibtex
journal = {Sensors},
volume  = {22},
number  = {23},
pages   = {9535},
doi     = {10.3390/s22239535}
```
- Actual journal: Sensors (MDPI), vol 22, no 23, article 9535
- DOI `10.3390/s22239535` -- verified

**Tex impact**: Citation `\cite{nicola2022comparative}` on line 322 still valid. No tex changes needed.

---

## Fix 3: `book2021safe` -- Wrong Authors, Truncated Title, Wrong Pages (CRITICAL)

**Before (BROKEN)**:
```bibtex
author  = {Book, Gerrit and Traue, Arne and Balakrishna, Praneeth and Schenke, Maximilian and Hanke, S{\"o}ren and Kirchg{\"a}ssner, Wilhelm and Wallscheid, Oliver},
title   = {Safe Bayesian Optimization for Data-Driven Power Electronics Control Design in Microgrids},
pages   = {42791--42803},
```
- Authors copied from `book2021transferring` (Gerrit Book et al.) -- completely wrong
- Title truncated -- missing "From Simulations to Real-World Experiments"
- Pages 42791-42803 -- wrong (belong to a different paper)

**After (VERIFIED)**:
```bibtex
author  = {Weber, Daniel and Heid, Stefan and Bode, Henrik and Lange, Jarren and H{\"u}llermeier, Eyke and Wallscheid, Oliver},
title   = {Safe Bayesian Optimization for Data-Driven Power Electronics Control Design in Microgrids: From Simulations to Real-World Experiments},
pages   = {35654--35669},
```
- Real authors: Daniel Weber, Stefan Heid, Henrik Bode, Jarren Lange, Eyke Hullermeier, Oliver Wallscheid
- Full title restored
- Pages: 35654-35669 (IEEE Access, vol 9, 2021)
- DOI `10.1109/ACCESS.2021.3062144` -- already correct, verified via multiple sources

**Tex impact**: Citation `\cite{book2021safe}` on line 596 still valid. Note: tex line 596 says "adjacent domain of electric motor control" but this paper is about power electronics control in microgrids (still sim-to-real, but different domain). This is a minor tex narrative issue, not a bib fix issue.

---

## Fix 4: `mahazabeen2022performance` -- Wrong Authors, Missing Pages (CRITICAL)

**Before (BROKEN)**:
```bibtex
author    = {Mahazabeen, Afrin and Nademi, Hamed},
```
- Only 2 authors listed; both names wrong
- No pages field

**After (VERIFIED)**:
```bibtex
author    = {Mahazabeen, Maliha and Abianeh, Ali Jafarian and Ebrahimi, Shayan and Ferdowsi, Farzad},
pages     = {1--5},
```
- Real authors: Maliha Mahazabeen, Ali Jafarian Abianeh, Shayan Ebrahimi, Farzad Ferdowsi (4 people)
- Pages: 1-5
- DOI `10.1109/NAPS56150.2022.10012228` -- verified, already correct

**Tex impact**: Citation `\cite{mahazabeen2022performance}` on line 322 still valid. No tex changes needed.

---

## Fix 5: `sanchez2020tinyml` -- DOI Last Digit Wrong (MEDIUM)

**Before**: `doi = {10.1109/MCAS.2020.3005467}`
**After**:  `doi = {10.1109/MCAS.2020.3005466}`

Change: 7 -> 6 (last digit). All other metadata correct.

**Tex impact**: Citation `\cite{sanchez2020tinyml}` on line 678 still valid. No tex changes needed.

---

## Fix 6: `cheng2018survey` -- Title Wording Deviation (MEDIUM)

**Before**: `title = {A Survey of Model Compression and Acceleration for Deep Neural Networks}`
**After**:  `title = {Model Compression and Acceleration for Deep Neural Networks: The Principles, Progress, and Challenges}`

Title updated to match official IEEE Signal Processing Magazine version. DOI `10.1109/MSP.2017.2765695` already correct.

**Tex impact**: Citation `\cite{cheng2018survey}` on line 677 still valid. No tex changes needed.

---

## Fix 7: `zhang2021machine` -- Bib Key Year Mismatch (LOW/NOTE ONLY)

**No structural change needed.** The `year = {2023}` field was already correct. Added note only:

```bibtex
note = {Bib key uses 2021 (arXiv preprint year); actual journal publication year is 2023. Key retained for citation stability.}
```

**Tex impact**: Citation `\cite{zhang2021machine}` on line 99 still valid. No tex changes needed.

---

## Fix 8a: `zeng2022multiagent` -- DOI Verification Note (MEDIUM)

**No DOI change needed.** The DOI `10.1109/TPEL.2022.3192345` was retained after verification against IEEE Xplore staging document 9793712. Paper metadata (title, authors, journal, volume, number, pages) all confirmed via multiple academic databases.

Added note:
```bibtex
note = {DOI verified via IEEE Xplore staging document 9793712; metadata confirmed.}
```

**Tex impact**: Citations `\cite{zeng2022multiagent}` on lines 368, 708, 749 still valid. No tex changes needed.

---

## Fix 8b: `zeng2023deep` -- DOI Wrong (MEDIUM)

**Before**: `doi = {10.1109/TIE.2023.3279277}`
**After**:  `doi = {10.1109/TIE.2023.3294584}`

DOI corrected based on verification via multiple independent academic databases (x-mol.com, scholarsportal.info, dblp.org). All other metadata (authors, journal, volume, pages) were already correct.

Added note:
```bibtex
note = {DOI corrected from 10.1109/TIE.2023.3279277; verified via multiple academic databases.}
```

**Tex impact**: Citation `\cite{zeng2023deep}` on line 713 still valid. No tex changes needed.

---

## Summary

| # | Bib Key | Severity | What Changed | Tex Impact |
|---|---------|----------|-------------|------------|
| 1 | `wu2021innovative` | CRITICAL | Authors (3->7), venue, pages, DOI -- completely replaced | None (same key, same title, same lead author surname) |
| 2 | `nicola2022comparative` | CRITICAL | Journal, volume, number, pages, DOI | None |
| 3 | `book2021safe` | CRITICAL | Authors (7 wrong -> 6 correct), title (truncated -> full), pages | None (minor tex narrative note about domain description) |
| 4 | `mahazabeen2022performance` | CRITICAL | Authors (2 wrong -> 4 correct), added pages | None |
| 5 | `sanchez2020tinyml` | MEDIUM | DOI last digit (7->6) | None |
| 6 | `cheng2018survey` | MEDIUM | Title wording updated | None |
| 7 | `zhang2021machine` | LOW | Note added (year field already correct) | None |
| 8a | `zeng2022multiagent` | MEDIUM | Note added (DOI/metadata verified, no change) | None |
| 8b | `zeng2023deep` | MEDIUM | DOI corrected (3279277->3294584), note added | None |

**All 8 bib issues fixed. Zero tex citation changes required (all bib keys preserved, all citations remain valid).**

**One narrative observation (not a bib fix)**: Tex line 596 groups `book2021safe` with `book2021transferring` under "adjacent domain of electric motor control." The Weber et al. paper (`book2021safe`) is actually about power electronics control design in microgrids, not electric motor control. Consider revising the tex narrative to better reflect the domain of the safe BO paper.
