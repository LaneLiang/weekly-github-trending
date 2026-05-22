@echo off
REM ============================================================
REM  DC-Auto-Tune Full Ablation Experiment Launcher
REM  Runs 4 strategies x 5 trials x 500 episodes
REM  Estimated time: 3-4 hours
REM  Output: logs/ablation/results_expanded.json
REM ============================================================

echo.
echo ========================================
echo  DC-Auto-Tune Full Ablation Experiment
echo  4 strategies x 5 trials x 500 episodes
echo  Start: %date% %time%
echo ========================================
echo.

cd /d "G:\blog\claude_code_useage\skills_create_train_dc_dc_auto"

python scripts/run_ablation.py --episodes 500 --trials 5 --strategies random --steps 200
echo [%time%] Batch 1/4 (random) done.

python scripts/run_ablation.py --episodes 500 --trials 5 --strategies bayesopt --steps 200
echo [%time%] Batch 2/4 (bayesopt) done.

python scripts/run_ablation.py --episodes 500 --trials 5 --strategies llm_fixed --steps 200
echo [%time%] Batch 3/4 (llm_fixed) done.

python scripts/run_ablation.py --episodes 500 --trials 5 --strategies llm_event --steps 200
echo [%time%] Batch 4/4 (llm_event) done.

echo.
echo ========================================
echo  ALL DONE: %date% %time%
echo  Results: logs/ablation/results_expanded.json
echo ========================================

REM Generate updated figures
python scripts/plot_figures.py
echo Figures regenerated.
pause
