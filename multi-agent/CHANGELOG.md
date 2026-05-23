# CHANGELOG

## v1.0.0 (2026-05-23)

### 核心架构

- **CEO → Actor → Reviewer 三层编排**: Orchestrator 自动 spawn Actor/Critic 子代理，5 维度打分（意图对齐、逻辑正确性、完整性、边界覆盖、质量），任一维度 < 80 即驳回，最多 3 轮修正
- **SubAgentManager**: 统一管理 18 个 workflow 的 actor/critic 角色调度
- **SQLiteStore**: 全量持久化 TaskRequest、Job、Artifact、CriticReview、NotificationEvent、ScoreRecord
- **幂等去重**: 基于 idempotency_key 防止重复触发，支持 scheduler 自动生成 key (`{role_group}-{date}-{hour}`)

### 13 个 Workflow 组（26 角色: 13 actor + 13 critic）

| Workflow | role_group | 触发方式 |
|----------|-----------|---------|
| Fake（测试用） | `fake` | CLI 手动 |
| GitHub 热点 | `github_trending` | 每周一 09:00 |
| AI 新闻 | `ai_news` | 每周一 10:00 |
| 工具更新检查 | `update_checker` | 每天 07:00 |
| DeepSeek 余额监控 | `deepseek_monitor` | 每天 08:00 |
| 日报 | `daily_report` | 每天 22:00 |
| 反思 | `reflection` | 每天 22:30 |
| 论文调研 | `paper_research` | 按需触发 |
| 论文写作 | `paper_writing` | 按需触发（免淘汰） |
| 邮件摘要 | `mail_digest` | 按需触发 |
| 周报生成 | `weekly_report` | 每周五 21:00 |
| PPT 汇报 | `presentation` | 每周日 20:00 |
| Claude 任务 | `claude_task` | 按需触发 |
| 记忆策展 | `memory_curation` | 按需触发 |
| 文献综述 | `literature_survey` | 按需触发 |
| 投稿合规检查 | `manuscript_tracker` | 按需触发 |
| 仿真数据管线 | `simulation_data_pipeline` | 按需触发 |
| EDA 验证平台 | `eda_testbench` | 按需触发 |

### 多渠道 Ingress

- **CLI**: `lanes-ceo --role <group> --message "..."` 手动触发
- **飞书**: Webhook 回调 + 消息发送，含签名验证
- **微信**: Webhook 回调 + SHA256 签名验证（可选启用）
- **QQ Bot**: Webhook 回调 + opcode 13 验证 + sha256 签名（可选启用）
- **shared.py**: 多 bridge 共享的 HTTP 工具、签名验证、消息类型检测

### 运行时观测 (Batch E)

- **健康检查**: `GET /health` 返回 uptime/bridge/scheduler 状态，`GET /health/jobs` 返回 24h job 统计
- **心跳日志**: 每小时记录 uptime、活跃 bridge 数、scheduler job 数
- **失败恢复**: exponential backoff 重试（2s→4s→8s），3 次后标记 FAILED，failure_reason 持久化
- **优雅关闭**: SIGINT/SIGTERM 信号处理，有序停止所有 bridge 和 scheduler

### 通知系统

- **NotificationOutbox**: 统一记录和投递通知事件
- 支持 feishu/weixin/qq/cli 多通道路由
- policy.py: 授权与频率限制
- score_reporter.py: 定期评分统计报告

### 测试

- **267 tests, 0 failures**
- 252 unit tests 覆盖全部 13 个 workflow（含 56 个 literature_survey 测试）
- 7 个 real-workflow 集成测试（UpdateCheckerWorkflow 全流水线）
- 8 个现有集成测试（fake workflow + idempotency + orchestrator gate）
- 共享 mock helper 模式（`_setup_pipeline_mocks`、`_mock_update_checker_env`）
