# 学术论文写作全流程指南 — Nature/Science 级工具链

> 适用场景：数字IC设计、芯片架构、EDA工具等方向的学术论文写作
> 目标水准：Nature/Science 子刊及以上

---

## 1. 工具总览

### 1.1 Claude Code Skills（全局安装，对话中自动触发）

| Skill 组 | 子技能 | 触发方式 |
|----------|--------|----------|
| **nature-skills** (9个) | `nature-writing` 论文写作 | 对话中提及"写论文/写Introduction"等 |
| | `nature-polishing` Nature级文字润色 | "润色到Nature标准" |
| | `nature-figure` 期刊图表绘制 | "画Nature风格的图" |
| | `nature-reader` 论文精读翻译 | "把这篇论文转成中文导读" |
| | `nature-academic-search` 文献检索 | "搜索XXX方向的最新文献" |
| | `nature-citation` 引用管理 | 自动触发，处理参考文献 |
| | `nature-data` 数据图表 | "分析这组数据" |
| | `nature-paper2ppt` 论文转PPT | "把论文转成组会PPT" |
| | `nature-response` 审稿回复 | "帮我写审稿回复" |
| **academic-research-skills** (ARS) | `academic-pipeline` 全流程10阶段 | `/ars-plan` 开始Socratic对话 |
| | `deep-research` 13-agent文献调研 | `/ars-lit-review "话题"` |
| | `academic-paper` 12-agent论文写作 | 自动触发，含风格校准 |
| | `academic-paper-reviewer` 7-agent审稿 | "审稿这篇论文" |
| **paper-polish-workflow** (16个) | `ppw:translation` 中译英 | `/ppw:translation` |
| | `ppw:polish` 英文润色 | `/ppw:polish` |
| | `ppw:de-ai` 去AI痕迹 | `/ppw:de-ai` |
| | `ppw:reviewer-simulation` 模拟审稿 | `/ppw:reviewer-simulation` |
| | `ppw:literature` 文献检索 | `/ppw:literature` |
| | `ppw:abstract` 摘要生成 | `/ppw:abstract` |
| | `ppw:repo-to-paper` 实验→论文 | `/ppw:repo-to-paper` |
| | `ppw:logic` 逻辑检查 | `/ppw:logic` |
| | `ppw:visualization` 图表优化 | `/ppw:visualization` |
| | 其他7个子技能... | 按需调用 |
| **research-paper-writing** | ML/CV/NLP论文方法论 | "用research-paper-writing优化Introduction" |

### 1.2 独立工具（project_paper/tools/）

| 工具 | 启动方式 | 用途 |
|------|----------|------|
| **GPT-Academic** (69.8K stars) | `cd project_paper/tools/gpt_academic && python main.py` | 全流程Web UI：PDF翻译(保留公式)、润色、代码解析、多模型并行 |
| **Awesome-Framework-Gallery** | 直接浏览 `project_paper/tools/awesome-framework-gallery` | Nature/Science/Cell论文框架图灵感参考 |
| **science-diagrams** | TikZ/LaTeX 模板: `project_paper/tools/science-diagrams` | 物理/化学/芯片架构矢量图模板 |

### 1.3 Python 包（全局可用）

| 包 | 用途 | 示例 |
|----|------|------|
| `tueplots` | 期刊标准尺寸/字体 (ICML/NeurIPS/CVPR) | `from tueplots import bundles` |
| `nice-figures` | APS/Nature期刊rcParams | `import nice_figures` |
| `knowledge-storm` | 斯坦福STORM综述生成 | `import knowledge_storm` |
| `gpt-researcher` | 多智能体深度研究 | `from gpt_researcher import GPTResearcher` |

---

## 2. 完整论文工作流

### 阶段0：选题与文献调研（Research）

```
1. 粗略方向 → /ars-lit-review "your broad topic"
   → ARS deep-research (13 agents) 生成结构化文献综述
   → 输出：研究空白分析 + PRISMA流程图 + 关键论文列表

2. 补充检索 → nature-academic-search or /ppw:literature
   → 从Semantic Scholar/Google Scholar拉取最新论文

3. 论文精读 → nature-reader
   → "把这篇PDF转成中文journal-club导读"
   → 输出：带公式保留的Markdown + 思维导图
```

### 阶段1：大纲设计（Outline）

```
1. Socratic对话 → /ars-plan
   → ARS引导式对话帮你理清8~12章大纲结构
   → 每章定义核心claim + 支撑evidence

2. 大纲审稿 → 模拟审稿人
   → "用审稿人视角评估这个大纲"
   → 评估逻辑一致性、新颖性、完整性
```

### 阶段2：论文写作（Writing）

```
1. 初稿撰写 → nature-writing
   → "用nature-writing技能写Introduction"
   → 逐节生成，保持voice一致

2. ARS写作 → academic-paper (12 agents)
   → Style Calibration：学习你的写作风格
   → Writing Quality Check：检测机器写作痕迹
   → 支持MD/DOCX/LaTeX/PDF (APA 7.0, IEEE, Chicago)

3. 中译英 → /ppw:translation
   → 中文学术草稿 → 投稿级英文
   → 输出LaTeX格式 + 中英对照

4. 实验→论文 → /ppw:repo-to-paper
   → 扫描ML/IC实验仓库，逐级生成大纲→正文
   → 自动带证据标注和引用
```

### 阶段3：润色与优化（Polishing）

```
1. Nature级润色 → nature-polishing
   → ≤30词句子、分时态、英式拼写、hedging用语

2. 快速润色 → /ppw:polish
   → 期刊风格适配 + 原地编辑追踪

3. 去AI化 → /ppw:de-ai
   → 两阶段：扫描标记AI痕迹 → 批量改写
   → 关键！Nature/Science编辑对AI痕迹极度敏感

4. 逻辑检查 → /ppw:logic
   → claim-evidence对齐检查
```

### 阶段4：图表制作（Figures）

```
1. 数据图 (Matplotlib) → nature-figure
   → "用nature-figure画这张功耗对比图"
   → 自动：Nature配色 + 正确字号 + SVG可编辑输出
   → 支持：分组/堆叠柱状图、折线图、热力图、气泡散点、雷达图

2. 架构图 (TikZ) → science-diagrams
   → 参考g:/tools/science-diagrams中的模板
   → 适合芯片微架构、电路拓扑等矢量图

3. 代码调用：tueplots + nice-figures
   → tueplots自动设置期刊尺寸/字体
   → nice-figures提供Nature/APS预配置style

4. 框架图参考 → Awesome-Framework-Gallery
   → 浏览Nature/Science/Cell已发表论文的框架图
```

### 阶段5：内审（Internal Review）

```
1. ARS审稿 → academic-paper-reviewer (7 agents)
   → EIC + 3位动态审稿人 + Devil's Advocate
   → 0-100分量化评分 + R&R追溯矩阵

2. 模拟审稿 → /ppw:reviewer-simulation
   → 结构化双语审稿报告

3. 自审 → research-paper-writing预提交自审
   → reviewer视角检查claim-evidence对齐
```

### 阶段6：投稿与回复（Submission & Revision）

```
1. 润色终稿 → nature-polishing (最后一遍)
2. 生成摘要 → /ppw:abstract
3. 写Cover Letter → /ppw:cover-letter
4. 审稿回复 → nature-response
   → 逐条回复reviewer意见，保持专业语气
```

---

## 3. 快速参考卡

### "我要开始一篇新论文"

```
/ars-plan                 # 大纲设计
/ars-lit-review "topic"   # 文献综述
nature-writing            # 开始写作
```

### "我有一个初稿要打磨"

```
/ppw:translation          # 中→英
/ppw:polish               # 英文润色
/ppw:de-ai                # 去AI痕迹
nature-polishing          # Nature级润色
```

### "我要画图"

```
nature-figure             # 数据图 (Matplotlib)
science-diagrams          # 架构图 (TikZ)
tueplots + nice-figures   # Python代码中调用
```

### "我要审稿自己的论文"

```
/ppw:reviewer-simulation  # 快速审稿
academic-paper-reviewer   # 深度7-agent审稿(ARS)
/ppw:logic                # 逻辑对齐检查
```

### "回复审稿意见"

```
nature-response           # 逐条回复
```

---

## 4. 数字IC领域特别建议

### 图表类型与工具选择

| 图表类型 | 推荐工具 | 备注 |
|----------|----------|------|
| 功耗/频率/面积对比柱状图 | `nature-figure` (Matplotlib) | 用分组柱状图，配色Okabe-Ito |
| 芯片架构框图 | `science-diagrams` (TikZ) | SVG导出，后期可在Inkscape编辑 |
| 波形/时序图 | TikZ-timing / Wavedrom | 矢量无损 |
| 版图/热力图 | `nature-figure` heatmap模式 | 色盲安全调色板必须 |
| 工艺对比雷达图 | `nature-figure` radar模式 | ≤5个工艺节点 |
| 框架overview图 | `Awesome-Framework-Gallery` 参考 | 先找灵感再自己画 |

### 公式处理

- GPT-Academic 的PDF翻译功能可保留LaTeX公式不变
- 润色时明确告知"保留所有公式和数学符号不变"
- ARS的LaTeX hardening会加固公式环境

### 常见IC论文结构（Nature Electronics / ISSCC风格）

1. Main text ≤ 5000 words + 4-6 figures
2. Methods放Supplementary
3. 强调"芯片实测结果"而非仿真
4. 比较表必须标注工艺节点和测试条件

---

## 5. 工具间协作优先级

当多个工具都能完成同一任务时，按以下优先级选择：

| 任务 | 首选 | 次选 | 何时切换 |
|------|------|------|----------|
| 文献综述 | ARS `deep-research` | STORM (`knowledge-storm`) | ARS结果太保守时用STORM拓宽 |
| 论文写作 | `nature-writing` | ARS `academic-paper` | 需要完整管线+防幻觉时用ARS |
| 文字润色 | `nature-polishing` | `/ppw:polish` | Nature/Science投稿必用前者 |
| 数据绘图 | `nature-figure` | `tueplots` 直调 | 需要精细控制时用tueplots |
| 文献检索 | `nature-academic-search` | `/ppw:literature` | 需要Semantic Scholar API时用后者 |
| AI检测改写 | `/ppw:de-ai` | — | 唯一选项，投稿前必用 |

---

## 6. 成本预估

| 工作流 | 工具 | 预估成本 |
|--------|------|----------|
| 一篇15000字论文全流程 | ARS (Claude Opus) | ~$4-6 |
| 单次Nature级润色 | nature-polishing | ~$0.3-0.5 |
| 单张Nature图表 | nature-figure | ~$0.1-0.3 |
| 一次深度审稿 | academic-paper-reviewer | ~$0.5-1 |
| 中文→英文翻译 | ppw:translation | ~$0.2-0.5/千字 |

---

## 7. 常见问题

**Q: 这些Skill会自动触发吗？**
A: 全局安装的Skill，Claude Code会在对话中根据语义自动匹配。你也可以显式指定，如"用nature-polishing润色这段"。

**Q: 如何验证AI没有编造引用？**
A: ARS内置citation hallucination检测（Levenshtein相似度≥0.70阈值），v3.8还支持claim-level审计。

**Q: GPT-Academic和Claude Code Skills有什么区别？**
A: GPT-Academic是独立的Web UI工具，支持多模型(GPT/DeepSeek/文心一言等)，适合需要GUI操作的场景。Claude Code Skills在终端/IDE中无缝集成。

**Q: 数字IC论文用什么LaTeX模板？**
A: 推荐IEEEtran（IEEE期刊）或nature.cls（Nature子刊），ARS的LaTeX hardening支持两者。
