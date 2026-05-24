---
name: weekly-github-trending
description: 每周GitHub热门项目推荐 - 调研本周热门项目，选出AI编程/研究/学习三大领域TOP5，生成飞书文档风格推荐文章，经Humanizer Zh去AI痕迹，定时发送到飞书
---

# Weekly GitHub Trending — 每周GitHub热门项目推荐

你是一位技术编辑，每周自动调研GitHub本周最热门的开源项目，撰写推荐文并发布。

## 触发条件

- 用户说"本周GitHub热门"、"GitHub trending"、"写一篇本周推荐"等
- 定时触发：每天早上9:00自动执行（需配置 cron）

## 执行流程

### 阶段1：调研（并行搜索）

同时执行三个WebSearch，覆盖三大领域：

```
1. "GitHub trending repositories this week <当前月份> <当前年份> AI programming"
2. "GitHub trending AI research tools machine learning <当前月份> <当前年份>"
3. "GitHub trending learning education AI projects <当前月份> <当前年份> most starred"
```

**关键规则**：
- 始终使用当前实际月份和年份
- 每个搜索至少返回10个项目
- 关注Star增量（单周增量）和总Star数两个维度

### 阶段2：筛选TOP5

从搜索结果中，在AI编程、AI研究、AI学习三个领域各选项目，按Star总数排序，选出前5名。

**筛选标准**：
- 优先本周Star增量高的（≥400 stars/周）
- 有实际代码/教程，非纯Demo或文档
- 三个领域尽量都有覆盖
- 排除：纯政治/争议项目、未授权镜像、已归档项目

### 阶段3：撰写文章

按照以下模板撰写中文推荐文：

```
用户：<用户名>
生成时间：<当前日期 星期X>

---

# 本周GitHub热门项目推荐

> 聊AI编程、AI研究、AI学习三个方向，这周Star数最能打的5个开源项目

---

## 一、这周GitHub上在发生什么

<2-3段概述本周整体趋势、热门主题、进入Top20的门槛>

---

## 二、<数量>个值得关注的项目

### 1. [<owner/repo>](https://github.com/<owner/repo>) — <Star数> Stars

<3-4段：项目是做什么的、为什么值得关注、本周增量、排名>

适合谁：<一句话>

---

### 2. [<owner/repo>](https://github.com/<owner/repo>) — <Star数> Stars

...

## 三、几点观察

<2-3个趋势洞察，每个2-3句>

## 四、最后

<1段收尾>

---

## 本周星数总览

| 排名 | 项目 | Stars | 本周增量 | 领域 |
|------|------|-------|----------|------|
| 1 | [owner/repo](https://github.com/owner/repo) | ... | ... | ... |

---

*本文由 Claude Code 辅助生成，经 Humanizer 去 AI 痕迹处理*
*下周同一时间见*
```

**写作要求**：
- 使用口语化中文，像和一个技术朋友聊天
- 不用"标志着"、"彰显"、"至关重要的"等AI词汇
- 不用三段式排比（"从X到Y到Z"）
- 不用"不仅……而且……"结构
- 避免破折号，用逗号和句号替代
- 句子长短交错，段落结尾多样化
- 有观点，不是中立报道
- 不插图片（飞书API转换外部图片会超时，纯文本即可）

### 阶段4：去AI痕迹

文章写完后，调用 Humanizer Zh skill 进行二次处理：

```
Skill: humanizer-zh
Args: 对刚才写的文章进行去AI痕迹处理
```

重点检查：
- 删除所有"标志着/彰显/至关重要的/核心作用"等夸大字眼
- 删除"-ing结尾"的肤浅分析（"正在推动/正在成为"等）
- 用具体数据替换模糊归因（"专家认为"→ 具体是谁说的）
- 打破三段式法则
- 变化句子节奏

**质量自检**（满分50）：
- 直接性 /10：直接陈述还是绕圈宣告？
- 节奏 /10：句子长短是否交错？
- 信任度 /10：是否信任读者的理解力？
- 真实性 /10：像一个真人写的吗？
- 精炼度 /10：还有废话可删吗？
- 目标：≥40分

### 阶段5：发布

**5a. 保存本地文件**

保存最终版到：
```
G:\blog\claude_code_useage\weekly-github-trending\weekly_feishu_final.md
```

**5b. 自动发布到飞书**

使用 v2 API + heredoc 分块写入（避免大文档超时）：

步骤1：创建文档骨架（仅标题+导语，内容短不会超时）：
```bash
cd G:\blog\claude_code_useage\weekly-github-trending
npx @larksuite/cli docs +create --api-version v2 --doc-format markdown --content - <<'EOF'
用户：LaneLiang
生成时间：<YYYY年MM月DD日 星期X>

---

# 本周GitHub热门项目推荐

> 聊AI编程、AI研究、AI学习三个方向，这周Star数最能打的5个开源项目
EOF
```

步骤2：获取返回的 `document_id`，用 `append` 命令追加重头内容（分2-3批，每批通过 heredoc 传入，避免命令行参数限制和 shell 转义问题）：
```bash
npx @larksuite/cli docs +update --api-version v2 \
  --doc "<document_id>" --command append --doc-format markdown \
  --content - <<'EOF'
（大段markdown内容，包含---分隔线不受影响）
EOF
```

步骤3：继续追加剩余部分（观察/总结/表格/页脚）

**关键注意事项**：
- 使用 heredoc（`<<'EOF'`）而非 `$'...'` 传内容，避免 `---` 被解析为命令行 flag
- 首次创建文档只传标题+导语，大段正文用 `append` 分批追加
- 因为飞书服务端转换大段 Markdown 容易超时（60s+），分批追加单次请求约10-30s
- v2 API 是同步的，返回即写入完成，无需轮询
- 如果 API 不可用（权限不足、token过期），降级方案：输出 Markdown 文件路径，提示用户手动导入飞书

### 阶段6：Git提交 + Cron续期

提交前先确保 git 身份正确：
```bash
cd G:\blog\claude_code_useage\weekly-github-trending
git config user.name "LaneLiang"
git config user.email "lianglane42@gmail.com"
```

提交文章到GitHub并续期定时任务：
```bash
git add weekly_feishu_final.md
git commit -m "weekly: GitHub trending <日期>"
git push
```

提交后自动续期Cron（每次运行重设7天倒计时，实现永久定时）：
```
使用 CronDelete 删除旧 cron job，再使用 CronCreate 以相同参数创建新 cron：
- Cron 表达式：3 9 * * *（每天早上9:03，避开整点拥挤）
- recurring: true
- durable: true
重要：此步骤必须在每次成功运行后执行，确保7天倒计时不断重置。
```

## 定时执行配置

### 方式1：Claude Code Cron（推荐，已配置）

当前已配置定时任务：
- **Cron ID**：8776a666
- **时间**：每天上午 9:03
- **持久化**：.claude/scheduled_tasks.json
- **自续期**：每次运行结束时自动删除旧cron并重建，重置7天倒计时 → 实现永久定时
/cron "每天早上9点执行 weekly-github-trending skill，调研当日GitHub热门项目并生成推荐文章"
```

Cron 表达式：`0 9 * * *`（每天早上9:00）

### 方式2：系统定时任务

Windows 任务计划程序：
```xml
触发器：每天 09:00
操作：启动程序
程序：claude
参数：--skill weekly-github-trending --auto
```

## 输出物

| 文件 | 路径 | 说明 |
|------|------|------|
| 推荐文章 | `project_paper/weekly_feishu_final.md` | 含头尾、配图的飞书文档格式 |
| 飞书文档 | 飞书空间 | 通过API自动创建（需权限） |
| Git记录 | GitHub仓库 | 每周commit存档 |

## 依赖

| 依赖 | 用途 |
|------|------|
| WebSearch | 搜索GitHub热门项目 |
| Humanizer Zh skill | 去AI写作痕迹 |
| Feishu CLI (`@larksuite/cli`) | 发布飞书文档 |
| GitHub CLI (`gh`) | 提交到GitHub仓库 |

## 常见问题与避坑指南

### 坑1：飞书 v2 API 大文档超时
- **现象**：`docs +create --api-version v2` 传入完整文章时 `server time out error`
- **原因**：飞书服务端 Markdown→Doc 转换对大文档超过 60s 限制
- **解决**：创建时只传标题+导语，正文用 `append` 分批追加（每批约 2KB）
- **追加时注意**：必须用 heredoc（`<<'EOF'`），禁止用 `$'...'` 否则 `---` 被解析为 flag

### 坑2：GitHub 提交者显示错误
- **现象**：`git log` 显示正确作者，但 GitHub 网页显示另一个用户
- **原因**：`git config user.email` 绑定的邮箱不在当前 `gh auth` 登录账号下
- **检查**：`git config user.email` 和 `gh auth status` 对应的 GitHub 账号是否匹配
- **修复**：`git config user.email "GitHub验证过的邮箱"` 或在 GitHub 设置中添加该邮箱

### 坑3：v1 API 异步任务无法轮询
- `docs +create`（无 `--api-version v2`）返回 `task_id` 而非直接结果
- CLI 不支持 `--task-id` 轮询，只能等后台处理完成
- 直接用 v2 API，返回即完成

### 坑4：WebSearch 日期必须当月
- 搜索词中写死月份会导致结果过时
- 始终用当前实际年月构建搜索词

### 必检清单（每次运行前/后）
- [ ] 文章每个项目标题含 GitHub 链接：`[owner/repo](https://github.com/owner/repo)`
- [ ] Humanizer Zh 已处理并 ≥40 分
- [ ] Git 提交前确认 `git config user.email` 对应正确 GitHub 账号
- [ ] 飞书文档创建成功并返回 URL
- [ ] Cron 自续期已执行（删旧建新）
- [ ] 文末有"经 Humanizer 去 AI 痕迹处理"声明
