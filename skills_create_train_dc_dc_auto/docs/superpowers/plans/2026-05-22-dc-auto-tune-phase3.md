# DC-DC 自动调参系统 Phase 3 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) to implement this plan task-by-task.

**Goal:** 完成实验验证矩阵、发表级图表产出和论文初稿，将 Phase 1-2 的基础设施转化为可发表的实验结论。

**Architecture:** 在 Phase 1-2 代码基础上，增加实验协议模块、标准化评测框架、图表生成管道和论文写作流水线。

**Tech Stack:** Phase 1-2 已有 + matplotlib（图表）+ nature-writing + humanizer-zh（论文写作）

**Pre-requisite:** Phase 2 完成（34/34 测试通过）

---

## 实验矩阵设计

### 实验 1：元优化策略消融（Phase 2 已实现，需扩大规模）

| 策略 | 描述 | trials | episodes |
|------|------|--------|----------|
| Random Search | 随机扰动超参数 | 5 | 500 |
| Bayesian Opt | GP-EI 代理模型 | 5 | 500 |
| **LLM Meta-Opt (Ours)** | LLM 持续训练教练 | 5 | 500 |

### 实验 2：LLM 介入频率消融

| 条件 | intervention_interval | 目的 |
|------|----------------------|------|
| 无 LLM | ∞ (纯 SAC) | 下界 baseline |
| 稀疏介入 | 100 | 验证 LLM 效率 |
| 标准介入 | 50 | Phase 2 default |
| 密集介入 | 20 | 上界参考 |

### 实验 3：Domain Randomization 消融

| 条件 | perturbation.enabled | 目的 |
|------|---------------------|------|
| 无扰动 | false | 基础性能 |
| 仅 ESR | L/C/Vin/R_load 固定 | 隔离 ESR 影响 |
| 全扰动 | true (Phase 2 default) | 鲁棒性验证 |

### 实验 4：拓扑泛化

| 拓扑 | 环境 | 验证方法 |
|------|------|---------|
| Buck CCM | BuckCCMEnv | Phase 2 已有 |
| Buck CCM/DCM | BuckCCMEnv (light load) | 轻载 DCM 边界 |
| Boost CCM | BoostCCMEnv | 升压场景 |
| Boost CCM/DCM | BoostCCMEnv (light load) | 轻载 DCM 边界 |

---

## 文件结构变更

```
新增/修改:
dc_auto_tune/
├── eval/
│   ├── protocol.py          → [新增] 实验协议：定义实验矩阵，自动批量运行
│   ├── metrics.py           → [新增] 7 指标计算器：从训练历史提取达标时间
│   └── reporter.py         → [新增] 结果汇总与 LaTeX 表格生成
scripts/
│   ├── run_ablation.py      → [已创建] 消融实验入口
│   ├── plot_ablation.py     → [已创建] 消融图表
│   ├── run_full_experiment.py → [新增] 完整实验矩阵执行
│   └── plot_figures.py      → [新增] 论文全图生成
paper/
│   ├── outline.md            → [新增] 论文提纲
│   ├── draft.tex             → [新增] LaTeX 初稿
│   └── figures/              → [新增] 图表输出目录
```

---

### Task 1: 实验协议与指标计算

**Goal:** 实现实验矩阵自动执行框架和 7 指标定量评估

**Files:**
- Create: `dc_auto_tune/eval/__init__.py`
- Create: `dc_auto_tune/eval/protocol.py`
- Create: `dc_auto_tune/eval/metrics.py`
- Create: `tests/test_eval.py`

- [ ] **Step 1: 实现 7 指标计算器 `dc_auto_tune/eval/metrics.py`**

```python
@dataclass
class ConverterMetrics:
    """7 个核心指标的定量评估"""
    vo_error_pct: float      # 电压精度 (%)
    vo_ripple_pct: float     # 电压纹波 (%)
    efficiency_pct: float    # 效率 (%)
    recovery_time_ms: float  # 负载瞬态恢复时间 (ms)
    overshoot_pct: float     # 超调量 (%)
    undershoot_pct: float    # 欠调量 (%)
    startup_time_ms: float   # 启动时间 (ms)

def compute_metrics(vo_history, iL_history, params) -> ConverterMetrics:
    """从训练历史计算全指标"""
```

- [ ] **Step 2: 实现实验协议 `dc_auto_tune/eval/protocol.py`**

```python
class ExperimentProtocol:
    """定义实验矩阵并批量运行"""
    def run_matrix(self, experiments: list[dict]) -> dict:
        # 依次运行每项实验，收集结果
    def summary_table(self, results: dict) -> str:
        # 输出 LaTeX 格式汇总表
```

- [ ] **Step 3: 写测试 — 指标计算边界情况**

- [ ] **Step 4: Commit**

---

### Task 2: 完整实验执行

**Goal:** 运行实验 1-4 矩阵，产出全部数据

- [ ] **Step 1: 实验 1 — 元优化消融（500 ep × 5 trials × 3 strategies）**

运行 `python scripts/run_ablation.py --episodes 500 --trials 5`，产生 `logs/ablation/results.json`

- [ ] **Step 2: 实验 2 — LLM 频率消融（3 种频率 × 3 trials）**

修改 `intervention_interval` 分别为 ∞/100/50/20，对比收敛速度。

- [ ] **Step 3: 实验 3 — Domain Randomization 消融（3 条件 × 3 trials）**

关闭、部分、全开扰动，验证老化鲁棒性提升幅度。

- [ ] **Step 4: 实验 4 — 拓扑泛化（Buck CCM/DCM + Boost CCM/DCM）**

在不同拓扑上验证 learned policy 的泛化能力。

- [ ] **Step 5: Commit 全部实验数据**

---

### Task 3: 论文图表生成

**Goal:** 生成 Nature/Science 级别发表用图

**Template:** 参考 `nature-figure` skill 规范

- [ ] **Step 1: Fig. 1 — 系统架构图**

三层架构示意图（LLM 元优化层 → SAC RL 层 → 电路环境层），用 `nature-figure` 生成。

- [ ] **Step 2: Fig. 2 — 收敛曲线对比**

3 策略 × 500 episodes，包含 error bars。

- [ ] **Step 3: Fig. 3 — 各指标达标时间对比**

7 指标雷达图或分组柱状图。

- [ ] **Step 4: Fig. 4 — CCM/DCM 时域波形**

轻载 DCM + 重载 CCM 下的 Vo/iL 波形。

- [ ] **Step 5: Fig. 5 — Domain Randomization 消融结果**

有无扰动的最终指标对比。

- [ ] **Step 6: Table 1 — 与 SOTA 方法的指标对比表**

| 方法 | 精度 | 纹波 | 效率 | 恢复时间 | 超调 | 欠调 | 启动 |
|------|------|------|------|---------|------|------|------|

- [ ] **Step 7: Commit**

---

### Task 4: 论文初稿

**Goal:** 撰写 Nature Machine Intelligence / IEEE TIE 格式初稿

**Skills 调用顺序:**
1. `nature-writing` — 起草初稿
2. `humanizer-zh` — 中文部分去 AI 痕迹
3. `nature-polishing` — 英文润色
4. `nature-citation` — 引用管理

- [ ] **Step 1: 论文提纲 `paper/outline.md`**

```markdown
# Continuous LLM-Driven Meta-Optimization for Reinforcement Learning-Based DC-DC Converter Control

## Abstract
## 1. Introduction
## 2. Related Work
   - 2.1 RL for DC-DC Control
   - 2.2 LLM for Power Electronics Design
   - 2.3 Meta-Learning and Hyperparameter Optimization
## 3. Method
   - 3.1 System Architecture
   - 3.2 SAC Agent with Multi-Objective Reward
   - 3.3 CCM/DCM Event-Driven Environment
   - 3.4 LLM as Continuous Training Meta-Optimizer
   - 3.5 Domain Randomization for Aging Robustness
## 4. Experiments
   - 4.1 Experimental Setup
   - 4.2 Ablation: LLM vs Random vs BayesOpt
   - 4.3 LLM Intervention Frequency Analysis
   - 4.4 Domain Randomization Robustness
   - 4.5 Topology Generalization
## 5. Results and Discussion
## 6. Conclusion
```

- [ ] **Step 2: 写 Abstract + Introduction**

使用 `nature-writing` 调用，输入实验数据。

- [ ] **Step 3: 写 Method 部分**

公式推导、架构描述、伪代码。

- [ ] **Step 4: 写 Experiments + Results**

插入实验数据、图表引用。

- [ ] **Step 5: 写 Discussion + Conclusion**

与 SOTA 对比分析、局限性、未来方向。

- [ ] **Step 6: `humanizer-zh` + `nature-polishing` 全稿润色**

- [ ] **Step 7: Commit**

---

### Task 5: 投稿准备

- [ ] **Step 1: Cover Letter** — 用 `ppw-cover-letter` 写投稿信
- [ ] **Step 2: 引用格式检查** — 用 `nature-citation` 验证
- [ ] **Step 3: 格式排版** — 按目标期刊模板调整
- [ ] **Step 4: Supplementary Materials** — 补充实验细节、超参数表
