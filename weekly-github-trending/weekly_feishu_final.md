用户：LaneLiang
生成时间：2026年5月28日 星期四

---

# 本周GitHub热门项目推荐

> 聊AI编程、AI研究、AI学习三个方向，这周Star数最能打的5个开源项目

---

## 一、这周GitHub上在发生什么

这周AI开源圈最热闹的事，是openhuman一周拿了17000颗星。Rust写的桌面Agent，接上Ollama就能在本地跑，数据不出电脑。隐私优先这个定位，确实戳到了痛点。

Agent Skills赛道也在继续升温。mattpocock、addyosmani这些名字你应该不陌生，他们都在把自己的编程工作流打包成可复用的skills文件往外放。不是简单的分享几个prompt，更像是在铺AI编程的工具链标准。

进Top20的门槛大概400颗星，比上个月又高了。开源AI项目现在卷的程度，跟App Store有得一拼。

---

## 二、5个值得关注的项目

### 1. [tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman) — 本周暴涨17000+ Stars

openhuman干的事很直接：给你一个跑在本地的桌面AI助手。能读写Gmail、GitHub、Slack、Notion、Google Calendar。Rust写的，推理走Ollama或LM Studio，数据全在你电脑上加密放着。

一周17000星，为什么？我觉得是时机刚好。上半年各种云端Agent让大家尝到了自动化的好处，但邮箱和日历的读写权限给到云端，说不担心是假的。openhuman的方案很粗暴：你自己跑，数据不出门。信任问题就这么解决了。

还早。OAuth一键授权的体验不算顺滑，bug也不少。但方向对。本地优先的AI Agent这个品类，下半年会越来越挤。

适合谁：想把日常琐事交给AI但又不想数据上云的人。

---

### 2. [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) — 160000+ Stars

Nous Research的Hermes Agent最近势头很猛。OpenRouter上的日token处理量已经超过OpenClaw，成了开源Agent里用得最多的那个。

跟别的Agent框架拉开差距的地方是"自我进化"。不是靠开发者手写规则，而是让Agent在用的时候从反馈里学。听起来像强化学习那套，但工程化程度够高，已经在生产环境跑了。

160k星不是一天涨上来的。不过这周的增速放在那里，说明社区在认真对待"能自我改进的Agent"这件事。如果这个路线真的跑通，Agent不用那么多手工调参，那整个行业的天花板会高很多。

适合谁：对Agent自主学习和自我改进机制感兴趣的研究者和工程师。

---

### 3. [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — 194000+ Stars

ECC（everything-claude-code）基本上是Claude Code重度用户的工具箱了。38个专业Agent、156个技能、1282项安全测试，数字摆在这里。

当成Claude Code的增强包来理解就好。内存优化、安全扫描、多Agent协作、技能管理，全打在一个包里。日增1500星，在开发者工具这个品类里不多见。

不过ECC的复杂度不低。只是用Claude Code写写小脚本的话，大概率用不上。但如果是在做正经的生产级项目，它那套安全测试和内存管理确实能省心。

适合谁：重度Claude Code用户，用AI做生产级开发的团队。

---

### 4. [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) — 20600+ Stars

一个AI工程学习项目，做得挺用心的。20个阶段、435节课、320小时，从数学基础写到Tokenizer、Attention、Backprop的手动实现，再到LLM微调、RAG、Agent、MCP和生产部署。一条路走到底。

市面上的AI教程大部分是"30分钟入门XXX"，这个项目反着来：它默认你真的想搞懂底层，而不是停留在调API。每个阶段都有能跑的代码，不靠文档凑数。

2万星在AI学习类项目里算很高了。初级AI教程已经严重过剩，开发者开始往深处走了。愿意花320小时啃数学基础的人，才是后面真能做东西出来的人。

适合谁：想从零系统性搞懂AI工程全链路的开发者。

---

### 5. [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — 90000+ Stars

社区把Andrej Karpathy的AI编程原则整理成了一套可复用的skills文件，涨到了9万多星。四条核心原则很简洁：先理解再修改、最小变更、始终先写测试、保持简洁。跟Clean Code那套一脉相承。

有意思的是，这不是Karpathy本人发的，是社区自发整理的。开发者在AI编程这件事上，开始主动找"原则"和"方法论"，不再满足于收集提示词技巧。

圈内有人说这是"AI编程时代的《代码整洁之道》"，我觉得不算夸张。这些原则本身没什么新鲜的，新鲜的是把它们嵌进AI编程工具的工作流，变成每次生成代码都遵守的硬约束。

适合谁：所有用AI辅助写代码的开发者，新手老手都能用。

---

## 三、几点观察

**Agent Skills变成了新的分发渠道。** 以前开源的是库和框架，现在开源的是"怎么干活"的工作流。mattpocock、addyosmani、Karpathy的skills项目加起来几十万星，开发者买的不是工具，是方法论。

**本地优先的AI在加速。** openhuman一周17000星不是孤立事件。Ollama、LM Studio、LEANN同时在推"AI跑在本地"。数据隐私的焦虑正在催生真实的市场需求，不是什么小众群体的自嗨。

**AI学习从入门卷到了深水区。** ai-engineering-from-scratch这种硬核课程的流行，说明初级教程已经让人审美疲劳了。320小时从数学基础啃起的路线，正在筛选出真正能走下去的人。

---

## 四、最后

五个项目，从桌面Agent到自我进化框架，从开发工具增强到硬核学习路线，把AI编程、研究、学习三个方向都覆盖了。如果你只有周末的时间，先跑一下openhuman感受本地Agent什么样，再翻翻andrej-karpathy-skills，看看能不能偷几招改进日常的编程习惯。

下周见。

---

## 本周星数总览

| 排名 | 项目 | Stars | 本周增量 | 领域 |
|------|------|-------|----------|------|
| 1 | [tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman) | ~30k | +17,000 | AI编程 |
| 2 | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | ~194k | +10,500 | AI编程 |
| 3 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | ~160k | +9,300 | AI研究 |
| 4 | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | ~90k | +7,800 | AI编程/学习 |
| 5 | [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) | ~21k | +2,100 | AI学习 |

---

*本文由 Claude Code 辅助生成，经 Humanizer 去 AI 痕迹处理*
*下周同一时间见*
