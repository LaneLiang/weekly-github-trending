# Claude Code Skills Catalog

一键扫描 `~/.claude/skills/` 目录，自动生成所有已安装 Skills 的完整参考文档。

## 快速使用

```bash
python generate_catalog.py
```

输出 `SKILLS_CATALOG.md`，包含每个 skill 的：名称、分类、功能描述、触发词（AI推断）、典型用例、版本、路径。

## 当前状态

- **总 Skills 数：** 450
- **来源分布：** everything-claude-code (234), hermes-agent (164), Lark/飞书 (22), Superpowers (19), nature-skills (9), Custom (2)
- **文档大小：** ~5600 行 / ~230KB
- **最后更新：** 2026-05-20

## 文档内容

| 章节 | 说明 |
|------|------|
| Overview by Source | 按来源统计 skills 数量和简介 |
| Skill Entries | 每个 skill 的详细信息（分类、描述、触发词、用例） |
| Appendix A | Skills 触发机制详解 |
| Appendix B | 常见工作流（论文写作、代码开发、调试等） |
| Appendix C | 安装指南 |
| Appendix D | 来源对比与选型建议 |
| Appendix E | 维护指南 |

## 定期更新

```bash
# 安装/卸载 skill 后重新生成
python generate_catalog.py

# 或设置 cron 每周自动更新
# 0 9 * * 1 cd /path/to/project && python generate_catalog.py && git commit -am "weekly update" && git push
```

## 相关项目

- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) — 140K+ stars
- [hermes-agent](https://github.com/NousResearch/hermes-agent) — 143K+ stars
