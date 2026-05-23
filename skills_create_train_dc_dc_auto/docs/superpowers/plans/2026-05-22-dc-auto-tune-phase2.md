# DC-DC 自动调参系统 Phase 2+4 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) to implement this plan task-by-task.

**Goal:** 扩展 Phase 1 MVP：真实 LLM 联调验证 + 消融实验 + DCM 模式覆盖 + Boost 拓扑 + 多域扰动鲁棒训练

**Architecture:** 在 Phase 1 三层架构基础上，env 层增加 DCM 事件驱动求解器和 Boost 拓扑，meta 层增加消融实验对比框架，env 层注入 Domain Randomization 扰动。

**Tech Stack:** 同 Phase 1 + scipy（贝叶斯优化消融对比）

**Pre-requisite:** Phase 1 完成（10/10 测试通过）

---

## 文件结构变更

```
新增/修改:
dc_auto_tune/
├── env/
│   ├── buck_ccm.py          → [修改] 增加 DCM 事件检测
│   ├── boost_ccm.py         → [新增] Boost CCM ODE 环境
│   ├── perturbation.py      → [新增] 多域扰动注入器
├── meta/
│   ├── ablation.py          → [新增] 消融实验：LLM vs Random vs BayesOpt
├── configs/
│   └── default.yaml         → [修改] 增加 perturbation 配置块
├── utils/
│   └── types_.py            → [修改] 增加 PerturbationConfig dataclass
tests/
├── test_dcm.py              → [新增] DCM 模式测试
├── test_boost_ccm.py        → [新增] Boost 环境测试
├── test_perturbation.py     → [新增] 扰动注入测试
├── test_ablation.py         → [新增] 消融实验测试
```

---

### Task 1: 真实 LLM 联调验证

**Goal:** 用真实 OpenAI API 跑完整训练，验证 LLM 元优化闭环正常工作

**Files:**
- Modify: `dc_auto_tune/meta/optimizer.py`（如需修复）
- Modify: `dc_auto_tune/train/trainer.py`（如需修复）

- [ ] **Step 1: 确保 OPENAI_API_KEY 可用**

检查环境变量或 .env 文件。若不可用则提示用户设置。

- [ ] **Step 2: 短训练验证（10 episodes, 50 steps each）**

修改配置跑一次短训练，观察 LLM 介入日志是否正常生成 JSON 格式的超参数建议。检查 `logs/*/llm_intervention_*.json`。

- [ ] **Step 3: 检查 LLM 输出格式合规性**

验证 LLM 返回的 JSON 是否包含 `analysis`、`sac_updates`、`weight_updates` 三个 key。若格式不稳定，加固 prompt 或增加 retry 逻辑。

- [ ] **Step 4: Commit**

---

### Task 2: 消融实验框架

**Goal:** 实现 LLM vs Random Search vs Bayesian Optimization 的对比实验

**Files:**
- Create: `dc_auto_tune/meta/ablation.py`
- Create: `tests/test_ablation.py`

- [ ] **Step 1: 实现 `dc_auto_tune/meta/ablation.py`**

三种元优化策略：

```python
class AblationStudy:
    """对比三种元优化策略"""
    
    @staticmethod
    def random_search_optimizer(training_state: dict) -> dict:
        """随机扰动超参数（baseline）"""
        # 在合法范围内随机采样
    
    @staticmethod
    def bayesopt_optimizer(training_state: dict) -> dict:
        """基于 scipy.optimize 的贝叶斯优化（GP-based）"""
        # 使用 Gaussian Process 建模超参数→reward 映射
    
    @staticmethod
    def llm_optimizer(training_state: dict) -> dict:
        """LLM 元优化器（本方案，已有）"""
        # 调用已有的 LLMMetaOptimizer
    
    def run_comparison(self, config, n_trials=5) -> dict:
        """运行三种策略各 n_trials 次，输出收敛曲线对比"""
```

- [ ] **Step 2: Run 对比实验**

用相同初始条件，分别运行三种策略各 200 episodes，记录收敛曲线。

- [ ] **Step 3: 生成对比图表**

reward vs episode 曲线、各指标达标时间对比。

- [ ] **Step 4: Commit**

---

### Task 3: DCM 事件驱动求解器

**Goal:** 在 BuckCCMEnv 中增加 iL 过零检测，自动切换 DCM IDLE 模式

**Files:**
- Modify: `dc_auto_tune/env/buck_ccm.py`
- Create: `tests/test_dcm.py`

- [ ] **Step 1: 写 DCM 测试 `tests/test_dcm.py`**

```python
class TestDCM:
    def test_light_load_enters_dcm(self):
        """轻载下 iL 应降到零进入 DCM"""
        params = CircuitParams(R_load=50.0)  # 极轻载
        env = BuckCCMEnv(params)
        env.reset()
        for _ in range(1000):
            obs, _, _, _, info = env.step(0.2)  # 小占空比
        # iL 应该周期性地降到 0
        assert info.get("mode") == "DCM" or env._detect_dcm()
    
    def test_heavy_load_stays_ccm(self):
        """重载下 iL 不应降到零"""
        params = CircuitParams(R_load=2.0)  # 重载
        env = BuckCCMEnv(params)
        env.reset()
        for _ in range(1000):
            obs, _, _, _, info = env.step(0.5)
        assert info.get("mode") == "CCM" or not env._detect_dcm()
```

- [ ] **Step 2: 修改 `buck_ccm.py` 增加 DCM 逻辑**

在 `step()` 内部每个子步长后检测 `iL ≤ 0`，进入 IDLE 状态机：
- `iL = 0`（钳位）
- `dvo_dt = -vo / (R_load * C)`（仅电容放电）
- 下一 ON 周期自动恢复

- [ ] **Step 3: 状态向量增加 `mode_flag`**

从 7 维扩展到 8 维：`[Vo, iL, error, ∫error, d_prev, i_load, Vin, mode_flag]`

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_dcm.py tests/test_buck_ccm.py -v
```
确保 DCM 新测试通过，CCM 旧测试不退化。

- [ ] **Step 5: Commit**

---

### Task 4: Boost 拓扑扩展

**Goal:** 新增 Boost CCM ODE 环境

**Files:**
- Create: `dc_auto_tune/env/boost_ccm.py`
- Create: `tests/test_boost_ccm.py`

- [ ] **Step 1: 写 Boost 测试**

```python
class TestBoostCCMEnv:
    def test_steady_state_converges(self):
        """CCM Boost: Vo = Vin/(1-d), d=0.5 → Vo≈24V at Vin=12V"""
        params = CircuitParams(vin=12.0, vout_ref=24.0, L=200e-6, C=100e-6, R_load=24.0)
        env = BoostCCMEnv(params)
        env.reset()
        for _ in range(2000):
            obs, _, _, _, _ = env.step(0.5)
        vo = obs[0].item()
        assert 22 < vo < 26
```

- [ ] **Step 2: 实现 Boost ODE**

ON 阶段：`diL/dt = Vin/L`, `dvC/dt = -Vo/(R*C)`
OFF 阶段：`diL/dt = (Vin-Vo)/L`, `dvC/dt = (iL - Vo/R)/C`

- [ ] **Step 3: Run tests & commit**

---

### Task 5: 多域扰动注入（Phase 4）

**Goal:** 在 episode 开始时随机采样器件参数，训练鲁棒策略

**Files:**
- Create: `dc_auto_tune/env/perturbation.py`
- Modify: `dc_auto_tune/utils/types_.py`（增加 `PerturbationConfig`）
- Modify: `dc_auto_tune/configs/default.yaml`
- Modify: `dc_auto_tune/env/buck_ccm.py`（接收扰动参数）
- Create: `tests/test_perturbation.py`

- [ ] **Step 1: 实现 `perturbation.py`**

```python
class DomainRandomizer:
    """在 episode 开始时随机采样器件参数"""
    def sample(self, base: CircuitParams) -> CircuitParams:
        # ESR: [1.0x, 2.5x]
        # L: [0.8x, 1.0x]
        # C: [0.7x, 1.0x]
        # Vin: nominal ±10%
        # R_load: 50%-150% nominal
```

- [ ] **Step 2: 集成到 Trainer**

`trainer.py` 中每个 episode 开始时调用 `randomizer.sample()` 更新环境参数。

- [ ] **Step 3: 写扰动测试，验证 Agent 在老化条件下仍满足指标**

- [ ] **Step 4: Commit**

---

### Task 6: E2E 回归测试

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/ -v --tb=short
```

- [ ] **Step 2: 修复回归问题**

- [ ] **Step 3: Commit**
