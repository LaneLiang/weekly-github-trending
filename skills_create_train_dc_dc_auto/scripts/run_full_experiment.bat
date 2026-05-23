@echo off
REM ============================================================
REM  DC-Auto-Tune Full Ablation Experiment Launcher
REM  Runs 4 strategies sequentially, each writing to a separate
REM  results file, then merges into results_expanded.json
REM  200 episodes x 3 trials x 200 steps per episode
REM  Estimated time: 3-4 hours
REM ============================================================

setlocal enabledelayedexpansion

set "ROOT=G:\blog\claude_code_useage\skills_create_train_dc_dc_auto"
set "OUTDIR=%ROOT%\logs\ablation"
cd /d "%ROOT%"

echo.
echo ========================================
echo  DC-Auto-Tune Full Ablation Experiment
echo  4 strategies x 3 trials x 200 episodes
echo  Start: %date% %time%
echo ========================================
echo.

REM Batch 1: Random Search
echo [%time%] Batch 1/4: Random Search
python -u scripts/run_ablation.py --episodes 200 --trials 3 --strategies random --steps 200 --output "%OUTDIR%\results_random.json"
echo [%time%] Batch 1/4 (random) done.

REM Batch 2: Bayesian Optimization
echo [%time%] Batch 2/4: Bayesian Optimization
python -u scripts/run_ablation.py --episodes 200 --trials 3 --strategies bayesopt --steps 200 --output "%OUTDIR%\results_bayesopt.json"
echo [%time%] Batch 2/4 (bayesopt) done.

REM Batch 3: LLM Fixed-Interval
echo [%time%] Batch 3/4: LLM Fixed-Interval
python -u scripts/run_ablation.py --episodes 200 --trials 3 --strategies llm_fixed --steps 200 --output "%OUTDIR%\results_llm_fixed.json"
echo [%time%] Batch 3/4 (llm_fixed) done.

REM Batch 4: LLM Event-Triggered
echo [%time%] Batch 4/4: LLM Event-Triggered
python -u scripts/run_ablation.py --episodes 200 --trials 3 --strategies llm_event --steps 200 --output "%OUTDIR%\results_llm_event.json"
echo [%time%] Batch 4/4 (llm_event) done.

REM Merge results
echo [%time%] Merging results...
python -c "import json; from pathlib import Path; d={}; [d.update(json.load(open(p))) for p in sorted(Path('%OUTDIR%').glob('results_*.json')) if p.stem != 'results_expanded']; json.dump(d, open('%OUTDIR%/results_expanded.json','w'), indent=2); print(f'Merged {len(d)} strategies')"

echo.
echo ========================================
echo  ALL DONE: %date% %time%
echo  Results: logs/ablation/results_expanded.json
echo ========================================

REM Generate updated figures
echo Regenerating figures...
python scripts/plot_figures.py
echo Figures regenerated.

REM Recompile paper
echo Recompiling paper...
cd paper
pdflatex -interaction=nonstopmode draft.tex > nul
pdflatex -interaction=nonstopmode draft.tex > nul
echo Paper recompiled.

echo.
echo Experiment complete! Final paper: paper/draft.pdf
pause
