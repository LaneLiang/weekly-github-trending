# weekly-github-trending

每周GitHub热门项目推荐 — Claude Code Skill

自动调研本周GitHub最热门的开源项目，覆盖AI编程、AI研究、AI学习三大领域，选出TOP5高Star项目，生成经过Humanizer去AI痕迹的中文推荐文章，定时发送到飞书。

## 功能

- 并行搜索三大领域（AI编程/研究/学习）的GitHub热门项目
- 智能筛选TOP5高Star项目
- 生成自然流畅的中文推荐文（经Humanizer Zh去AI痕迹）
- 支持飞书文档自动发布
- 支持每日9:00定时触发

## 安装

```bash
# 复制到Claude Code全局skills目录
cp -R . ~/.claude/skills/weekly-github-trending/

# 或作为项目skills
cp -R . <project>/.claude/skills/weekly-github-trending/
```

## 使用

在 Claude Code 会话中直接说：

- "生成本周GitHub热门项目推荐"
- "这周GitHub有什么热门项目？"
- "写一篇GitHub trending推荐"

## 定时执行

```
/cron "每天早上9点执行 weekly-github-trending，调研GitHub热门项目并生成推荐"
```

## 依赖

- WebSearch（内置）
- Humanizer Zh skill
- Feishu CLI (`@larksuite/cli`) — 可选，用于飞书发布
- GitHub CLI (`gh`) — 可选，用于存档

## 输出

- 飞书格式Markdown文档：`project_paper/weekly_feishu_final.md`

## 示例文章

见 `project_paper/weekly_feishu_final.md`

## License

MIT
