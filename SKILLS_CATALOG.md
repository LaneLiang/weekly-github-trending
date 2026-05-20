# Claude Code Skills Catalog

**Total skills:** 450  
**Generated:** 2026-05-20  
**Source:** `~/.claude/skills/`

> **Legend:** 🤖 = AI-inferred trigger/use case. Review before relying.

## Overview by Source

| Source | Skills | Description |
|--------|--------|-------------|
| everything-claude-code | 234 | ECC universal configuration (180+ skills, 47 agents, 79 commands) |
| hermes-agent | 164 | Digital twin agent with learning loop and skill auto-generation |
| Lark (飞书) Integration | 22 | Feishu/Lark API integrations (docs, sheets, calendar, IM, etc.) |
| Superpowers Workflow | 19 | Built-in workflow discipline skills (plan, debug, review, verify) |
| nature-skills | 9 | Nature/Science journal writing toolkit (9 skills) |
| Custom Skills | 2 | User-installed custom skills |

## Table of Contents

- [everything-claude-code](#everything-claude-code) (234 skills)
- [hermes-agent](#hermes-agent) (164 skills)
- [Lark (飞书) Integration](#lark--integration) (22 skills)
- [Superpowers Workflow](#superpowers-workflow) (19 skills)
- [nature-skills](#nature-skills) (9 skills)
- [Custom Skills](#custom-skills) (2 skills)

## everything-claude-code {{everything-claude-code}}

**Version:** 2.0.0-rc.1  
**Author:** Affaan Mustafa  
**Repo:** <https://github.com/affaan-m/ECC>  

> 234 skills — use Ctrl+F to search.

### accessibility

**Category:** Accessibility | **Path:** `everything-claude-code\skills\accessibility/`

**Description:** Design, implement, and audit inclusive digital products using WCAG 2.2 Level AA standards. Use this skill to generate semantic ARIA for Web and accessibility traits for Web and Native platforms (iOS/Android).

**Trigger Words 🤖:** When user mentions `accessibility` or related concepts

**Use Case 🤖:** Design and audit accessible digital products (WCAG)

---

### agent-architecture-audit

**Category:** Agent | **Path:** `everything-claude-code\skills\agent-architecture-audit/`

**Description:** Full-stack diagnostic for agent and LLM applications. Audits the 12-layer agent stack for wrapper regression, memory pollution, tool discipline failures, hidden repair loops, and rendering corruption. Produces severity-ranked findings with code-first fixes. Essential for developers building agent applications, autonomous loops, or any LLM-powered feature.

**Trigger Words 🤖:** When user mentions `agent-architecture-audit` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### agent-eval

**Category:** Quality | **Path:** `everything-claude-code\skills\agent-eval/`

**Description:** Head-to-head comparison of coding agents (Claude Code, Aider, Codex, etc.) on custom tasks with pass rate, cost, time, and consistency metrics

**Trigger Words 🤖:** When user mentions `agent-eval` or related concepts

**Use Case 🤖:** Evaluate and benchmark outputs

---

### agent-harness-construction

**Category:** Agent | **Path:** `everything-claude-code\skills\agent-harness-construction/`

**Description:** Design and optimize AI agent action spaces, tool definitions, and observation formatting for higher completion rates.

**Trigger Words 🤖:** When user mentions `agent-harness-construction` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### agent-introspection-debugging

**Category:** Agent | **Path:** `everything-claude-code\.agents\skills\agent-introspection-debugging/`

**Description:** Structured self-debugging workflow for AI agent failures using capture, diagnosis, contained recovery, and introspection reports.

**Trigger Words 🤖:** When user mentions `agent-introspection-debugging` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### agent-payment-x402

**Category:** Agent | **Path:** `everything-claude-code\skills\agent-payment-x402/`

**Description:** Add x402 payment execution to AI agents with per-task budgets, spending controls, and non-custodial wallets. Supports Base through agentwallet-sdk and X Layer through OKX Payments / OKX Agent Payments Protocol.

**Trigger Words 🤖:** When user mentions `agent-payment-x402` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### agent-sort

**Category:** Agent | **Path:** `everything-claude-code\.agents\skills\agent-sort/`

**Description:** Build an evidence-backed ECC install plan for a specific repo by sorting skills, commands, rules, hooks, and extras into DAILY vs LIBRARY buckets using parallel repo-aware review passes. Use when ECC should be trimmed to what a project actually needs instead of loading the full bundle.

**Trigger Words 🤖:** When user mentions `agent-sort` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### agentic-engineering

**Category:** Quality | **Path:** `everything-claude-code\.kiro\skills\agentic-engineering/`

**Description:** Operate as an agentic engineer using eval-first execution, decomposition, and cost-aware model routing. Use when AI agents perform most implementation work and humans enforce quality and risk controls.

**Trigger Words 🤖:** When user mentions `agentic-engineering` or related concepts

**Use Case 🤖:** Evaluate and benchmark outputs

---

### agentic-os

**Category:** Context | **Path:** `everything-claude-code\skills\agentic-os/`

**Description:** Build persistent multi-agent operating systems on Claude Code. Covers kernel architecture, specialist agents, slash commands, file-based memory, scheduled automation, and state management without external databases.

**Trigger Words 🤖:** When user mentions `agentic-os` or related concepts

**Use Case 🤖:** Manage persistent memory and context

---

### ai-first-engineering

**Category:** General | **Path:** `everything-claude-code\skills\ai-first-engineering/`

**Description:** Engineering operating model for teams where AI agents generate a large share of implementation output.

**Trigger Words 🤖:** When user mentions `ai-first-engineering` or related concepts

**Use Case 🤖:** Use for tasks involving ai first engineering (see description).

---

### ai-regression-testing

**Category:** Database | **Path:** `everything-claude-code\skills\ai-regression-testing/`

**Description:** Regression testing strategies for AI-assisted development. Sandbox-mode API testing without database dependencies, automated bug-check workflows, and patterns to catch AI blind spots where the same model writes and reviews code.

**Trigger Words 🤖:** When user mentions `ai-regression-testing` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### android-clean-architecture

**Category:** Data | **Path:** `everything-claude-code\skills\android-clean-architecture/`

**Description:** Clean Architecture patterns for Android and Kotlin Multiplatform projects — module structure, dependency rules, UseCases, Repositories, and data layer patterns.

**Trigger Words 🤖:** When user mentions `android-clean-architecture` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### angular-developer

**Category:** Accessibility | **Path:** `everything-claude-code\skills\angular-developer/`

**Description:** Generates Angular code and provides architectural guidance. Trigger when creating projects, components, or services, or for best practices on reactivity (signals, linkedSignal, resource), forms, dependency injection, routing, SSR, accessibility (ARIA), animations, styling (component styles, Tailwind CSS), testing, or CLI tooling.

**Trigger Words 🤖:** When user mentions `angular-developer` or related concepts

**Use Case 🤖:** Design and audit accessible digital products (WCAG)

---

### api-connector-builder

**Category:** API | **Path:** `everything-claude-code\skills\api-connector-builder/`

**Description:** Build a new API connector or provider by matching the target repo's existing integration pattern exactly. Use when adding one more integration without inventing a second architecture.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `api-connector-builder` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### api-design

**Category:** API | **Path:** `everything-claude-code\.agents\skills\api-design/`

**Description:** REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production APIs.

**Trigger Words 🤖:** When user mentions `api-design` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### architecture-decision-records

**Category:** General | **Path:** `everything-claude-code\skills\architecture-decision-records/`

**Description:** Capture architectural decisions made during Claude Code sessions as structured ADRs. Auto-detects decision moments, records context, alternatives considered, and rationale. Maintains an ADR log so future developers understand why the codebase is shaped the way it is.

**Trigger Words 🤖:** When user mentions `architecture-decision-records` or related concepts

**Use Case 🤖:** Use for tasks involving architecture decision records (see description).

---

### article-writing

**Category:** Content | **Path:** `everything-claude-code\.agents\skills\article-writing/`

**Description:** Write articles, guides, blog posts, tutorials, newsletter issues, and other long-form content in a distinctive voice derived from supplied examples or brand guidance. Use when the user wants polished written content longer than a paragraph, especially when voice consistency, structure, and credibility matter.

**Trigger Words 🤖:** When user mentions `article-writing` or related concepts

**Use Case 🤖:** Content generation and management

---

### automation-audit-ops

**Category:** Integration | **Path:** `everything-claude-code\skills\automation-audit-ops/`

**Description:** Evidence-first automation inventory and overlap audit workflow for ECC. Use when the user wants to know which jobs, hooks, connectors, MCP servers, or wrappers are live, broken, redundant, or missing before fixing anything.

**Trigger Words 🤖:** When user mentions `automation-audit-ops` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### autonomous-agent-harness

**Category:** Agent | **Path:** `everything-claude-code\skills\autonomous-agent-harness/`

**Description:** Transform Claude Code into a fully autonomous agent system with persistent memory, scheduled operations, computer use, and task queuing. Replaces standalone agent frameworks (Hermes, AutoGPT) by leveraging Claude Code's native crons, dispatch, MCP tools, and memory. Use when the user wants continuous autonomous operation, scheduled tasks, or a self-directing agent loop.

**Trigger Words 🤖:** When user mentions `autonomous-agent-harness` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### autonomous-loops

**Category:** Agent | **Path:** `everything-claude-code\skills\autonomous-loops/`

**Description:** Patterns and architectures for autonomous Claude Code loops — from simple sequential pipelines to RFC-driven multi-agent DAG systems.

**Trigger Words 🤖:** When user mentions `autonomous-loops` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### backend-patterns

**Category:** Backend | **Path:** `everything-claude-code\.agents\skills\backend-patterns/`

**Description:** Backend architecture patterns, API design, database optimization, and server-side best practices for Node.js, Express, and Next.js API routes.

**Trigger Words 🤖:** When user mentions `backend-patterns` or related concepts

**Use Case 🤖:** Build backend services and APIs

---

### benchmark

**Category:** Meta | **Path:** `everything-claude-code\skills\benchmark/`

**Description:** Use this skill to measure performance baselines, detect regressions before/after PRs, and compare stack alternatives.

**Trigger Words 🤖:** When user mentions `benchmark` or related concepts

**Use Case 🤖:** Create, manage, or discover skills

---

### blender-motion-state-inspection

**Category:** Meta | **Path:** `everything-claude-code\skills\blender-motion-state-inspection/`

**Description:** Use this skill when inspecting Blender characters, rigs, poses, animation retargeting, ground contact, facing direction, or model-vs-motion alignment where screenshots alone are not enough.

**Trigger Words 🤖:** When user mentions `blender-motion-state-inspection` or related concepts

**Use Case 🤖:** Create, manage, or discover skills

---

### blueprint

**Category:** Workflow | **Path:** `everything-claude-code\skills\blueprint/`

**Description:** Turn a one-line objective into a step-by-step construction plan for multi-session, multi-agent engineering projects. Each step has a self-contained context brief so a fresh agent can execute it cold. Includes adversarial review gate, dependency graph, parallel step detection, anti-pattern catalog, and plan mutation protocol. TRIGGER when: user requests a plan, blueprint, or roadmap for a complex multi-PR task, or describes work that needs multiple sessions. DO NOT TRIGGER when: task is completable in a single PR or fewer than 3 tool calls, or user says "just do it".

**Trigger Words 🤖:** When user mentions `blueprint` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### brand-voice

**Category:** Design | **Path:** `everything-claude-code\.agents\skills\brand-voice/`

**Description:** Build a source-derived writing style profile from real posts, essays, launch notes, docs, or site copy, then reuse that profile across content, outreach, and social workflows. Use when the user wants voice consistency without generic AI writing tropes.

**Trigger Words 🤖:** When user mentions `brand-voice` or related concepts

**Use Case 🤖:** Brand guidelines and visual identity

---

### browser-qa

**Category:** Browser | **Path:** `everything-claude-code\skills\browser-qa/`

**Description:** Use this skill to automate visual testing and UI interaction verification using browser automation after deploying features.

**Trigger Words 🤖:** When user mentions `browser-qa` or related concepts

**Use Case 🤖:** Browser automation and testing

---

### bun-runtime

**Category:** Testing | **Path:** `everything-claude-code\.agents\skills\bun-runtime/`

**Description:** Bun as runtime, package manager, bundler, and test runner. When to choose Bun vs Node, migration notes, and Vercel support.

**Trigger Words 🤖:** When user mentions `bun-runtime` or related concepts

**Use Case 🤖:** Write and run tests

---

### canary-watch

**Category:** Workflow | **Path:** `everything-claude-code\skills\canary-watch/`

**Description:** Use this skill to monitor and verify a deployed URL after releases — checks HTTP endpoints, SSE streams, static assets, console errors, and performance regressions after deploys, merges, or dependency upgrades. Smoke / canary / post-deploy verification.

**Trigger Words 🤖:** When user mentions `canary-watch` or related concepts

**Use Case 🤖:** Verify code changes work by running the app

---

### carrier-relationship-management

**Category:** General | **Path:** `everything-claude-code\skills\carrier-relationship-management/`

**Description:** Codified expertise for managing carrier portfolios, negotiating freight rates, tracking carrier performance, allocating freight, and maintaining strategic carrier relationships. Informed by transportation managers with 15+ years experience. Includes scorecarding frameworks, RFP processes, market intelligence, and compliance vetting. Use when managing carriers, negotiating rates, evaluating carrier performance, or building freight strategies.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `carrier-relationship-management` or related concepts

**Use Case 🤖:** Use for tasks involving carrier relationship management (see description).

---

### cisco-ios-patterns

**Category:** Workflow | **Path:** `everything-claude-code\skills\cisco-ios-patterns/`

**Description:** Cisco IOS and IOS-XE review patterns for show commands, config hierarchy, wildcard masks, ACL placement, interface hygiene, and safe change-window verification.

**Trigger Words 🤖:** When user mentions `cisco-ios-patterns` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### ck

**Category:** Workflow | **Path:** `everything-claude-code\skills\ck/`

**Description:** Persistent per-project memory for Claude Code. Auto-loads project context on session start, tracks sessions with git activity, and writes to native memory. Commands run deterministic Node.js scripts — behavior is consistent across model versions.

**Version:** 2.0.0  
**Trigger Words 🤖:** When user mentions `ck` or related concepts

**Use Case 🤖:** Launch and drive the project app to test changes

---

### claude-devfleet

**Category:** Planning | **Path:** `everything-claude-code\skills\claude-devfleet/`

**Description:** Orchestrate multi-agent coding tasks via Claude DevFleet — plan projects, dispatch parallel agents in isolated worktrees, monitor progress, and read structured reports.

**Trigger Words 🤖:** When user mentions `claude-devfleet` or related concepts

**Use Case 🤖:** Create implementation plans

---

### click-path-audit

**Category:** General | **Path:** `everything-claude-code\skills\click-path-audit/`

**Description:** Trace every user-facing button/touchpoint through its full state change sequence to find bugs where functions individually work but cancel each other out, produce wrong final state, or leave the UI in an inconsistent state. Use when: systematic debugging found no bugs but users report broken buttons, or after any major refactor touching shared state stores.

**Trigger Words 🤖:** When user mentions `click-path-audit` or related concepts

**Use Case 🤖:** Use for tasks involving click path audit (see description).

---

### clickhouse-io

**Category:** General | **Path:** `everything-claude-code\docs\ko-KR\skills\clickhouse-io/`

**Description:** 고성능 분석 워크로드를 위한 ClickHouse 데이터베이스 패턴, 쿼리 최적화, 분석 및 데이터 엔지니어링 모범 사례.

**Trigger Words 🤖:** When user mentions `clickhouse-io` or related concepts

**Use Case 🤖:** Use for tasks involving clickhouse io (see description).

---

### code-tour

**Category:** General | **Path:** `everything-claude-code\skills\code-tour/`

**Description:** Create CodeTour `.tour` files — persona-targeted, step-by-step walkthroughs with real file and line anchors. Use for onboarding tours, architecture walkthroughs, PR tours, RCA tours, and structured "explain how this works" requests.

**Trigger Words 🤖:** When user mentions `code-tour` or related concepts

**Use Case 🤖:** Use for tasks involving code tour (see description).

---

### codebase-onboarding

**Category:** General | **Path:** `everything-claude-code\skills\codebase-onboarding/`

**Description:** Analyze an unfamiliar codebase and generate a structured onboarding guide with architecture map, key entry points, conventions, and a starter CLAUDE.md. Use when joining a new project or setting up Claude Code for the first time in a repo.

**Trigger Words 🤖:** When user mentions `codebase-onboarding` or related concepts

**Use Case 🤖:** Use for tasks involving codebase onboarding (see description).

---

### coding-standards

**Category:** Workflow | **Path:** `everything-claude-code\.agents\skills\coding-standards/`

**Description:** Baseline cross-project coding conventions for naming, readability, immutability, and code-quality review. Use detailed frontend or backend skills for framework-specific patterns.

**Trigger Words 🤖:** When user mentions `coding-standards` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### compose-multiplatform-patterns

**Category:** General | **Path:** `everything-claude-code\skills\compose-multiplatform-patterns/`

**Description:** Compose Multiplatform and Jetpack Compose patterns for KMP projects — state management, navigation, theming, performance, and platform-specific UI.

**Trigger Words 🤖:** When user mentions `compose-multiplatform-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving compose multiplatform patterns (see description).

---

### configure-ecc

**Category:** General | **Path:** `everything-claude-code\skills\configure-ecc/`

**Description:** Interactive installer for Everything Claude Code — guides users through selecting and installing skills and rules to user-level or project-level directories, verifies paths, and optionally optimizes installed files.

**Trigger Words 🤖:** When user mentions `configure-ecc` or related concepts

**Use Case 🤖:** Use for tasks involving configure ecc (see description).

---

### connections-optimizer

**Category:** Workflow | **Path:** `everything-claude-code\skills\connections-optimizer/`

**Description:** Reorganize the user's X and LinkedIn network with review-first pruning, add/follow recommendations, and channel-specific warm outreach drafted in the user's real voice. Use when the user wants to clean up following lists, grow toward current priorities, or rebalance a social graph around higher-signal relationships.

**Trigger Words 🤖:** When user mentions `connections-optimizer` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### content-engine

**Category:** Content | **Path:** `everything-claude-code\.agents\skills\content-engine/`

**Description:** Create platform-native content systems for X, LinkedIn, TikTok, YouTube, newsletters, and repurposed multi-platform campaigns. Use when the user wants social posts, threads, scripts, content calendars, or one source asset adapted cleanly across platforms.

**Trigger Words 🤖:** When user mentions `content-engine` or related concepts

**Use Case 🤖:** Content generation and management

---

### content-hash-cache-pattern

**Category:** Content | **Path:** `everything-claude-code\skills\content-hash-cache-pattern/`

**Description:** Cache expensive file processing results using SHA-256 content hashes — path-independent, auto-invalidating, with service layer separation.

**Trigger Words 🤖:** When user mentions `content-hash-cache-pattern` or related concepts

**Use Case 🤖:** Content generation and management

---

### context-budget

**Category:** Integration | **Path:** `everything-claude-code\skills\context-budget/`

**Description:** Audits Claude Code context window consumption across agents, skills, MCP servers, and rules. Identifies bloat, redundant components, and produces prioritized token-savings recommendations.

**Trigger Words 🤖:** When user mentions `context-budget` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### continuous-agent-loop

**Category:** Workflow | **Path:** `everything-claude-code\skills\continuous-agent-loop/`

**Description:** Patterns for continuous autonomous agent loops with quality gates, evals, and recovery controls.

**Trigger Words 🤖:** When user mentions `continuous-agent-loop` or related concepts

**Use Case 🤖:** Run recurring tasks on a timer interval

---

### continuous-learning

**Category:** General | **Path:** `everything-claude-code\docs\ko-KR\skills\continuous-learning/`

**Description:** Claude Code 세션에서 재사용 가능한 패턴을 자동으로 추출하여 향후 사용을 위한 학습된 스킬로 저장합니다.

**Trigger Words 🤖:** When user mentions `continuous-learning` or related concepts

**Use Case 🤖:** Use for tasks involving continuous learning (see description).

---

### continuous-learning-v2

**Category:** General | **Path:** `everything-claude-code\docs\ko-KR\skills\continuous-learning-v2/`

**Description:** 훅을 통해 세션을 관찰하고, 신뢰도 점수가 있는 원자적 본능을 생성하며, 이를 스킬/명령어/에이전트로 진화시키는 본능 기반 학습 시스템. v2.1에서는 프로젝트 간 오염을 방지하기 위한 프로젝트 범위 본능이 추가되었습니다.

**Version:** 2.1.0  
**Trigger Words 🤖:** When user mentions `continuous-learning-v2` or related concepts

**Use Case 🤖:** Use for tasks involving continuous learning v2 (see description).

---

### cost-aware-llm-pipeline

**Category:** Orchestration | **Path:** `everything-claude-code\skills\cost-aware-llm-pipeline/`

**Description:** Cost optimization patterns for LLM API usage — model routing by task complexity, budget tracking, retry logic, and prompt caching.

**Trigger Words 🤖:** When user mentions `cost-aware-llm-pipeline` or related concepts

**Use Case 🤖:** Master orchestrator for multi-stage workflows

---

### cost-tracking

**Category:** Database | **Path:** `everything-claude-code\skills\cost-tracking/`

**Description:** Track and report Claude Code token usage, spending, and budgets from a local cost-tracking database. Use when the user asks about costs, spending, usage, tokens, budgets, or cost breakdowns by project, tool, session, or date.

**Trigger Words 🤖:** When user mentions `cost-tracking` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### council

**Category:** General | **Path:** `everything-claude-code\skills\council/`

**Description:** Convene a four-voice council for ambiguous decisions, tradeoffs, and go/no-go calls. Use when multiple valid paths exist and you need structured disagreement before choosing.

**Trigger Words 🤖:** When user mentions `council` or related concepts

**Use Case 🤖:** Use for tasks involving council (see description).

---

### cpp-coding-standards

**Category:** General | **Path:** `everything-claude-code\skills\cpp-coding-standards/`

**Description:** C++ coding standards based on the C++ Core Guidelines (isocpp.github.io). Use when writing, reviewing, or refactoring C++ code to enforce modern, safe, and idiomatic practices.

**Trigger Words 🤖:** When user mentions `cpp-coding-standards` or related concepts

**Use Case 🤖:** Use for tasks involving cpp coding standards (see description).

---

### cpp-testing

**Category:** General | **Path:** `everything-claude-code\skills\cpp-testing/`

**Description:** Use only when writing/updating/fixing C++ tests, configuring GoogleTest/CTest, diagnosing failing or flaky tests, or adding coverage/sanitizers.

**Trigger Words 🤖:** When user mentions `cpp-testing` or related concepts

**Use Case 🤖:** Use for tasks involving cpp testing (see description).

---

### crosspost

**Category:** Content | **Path:** `everything-claude-code\.agents\skills\crosspost/`

**Description:** Multi-platform content distribution across X, LinkedIn, Threads, and Bluesky. Adapts content per platform using content-engine patterns. Never posts identical content cross-platform. Use when the user wants to distribute content across social platforms.

**Trigger Words 🤖:** When user mentions `crosspost` or related concepts

**Use Case 🤖:** Content generation and management

---

### csharp-testing

**Category:** Testing | **Path:** `everything-claude-code\skills\csharp-testing/`

**Description:** C# and .NET testing patterns with xUnit, FluentAssertions, mocking, integration tests, and test organization best practices.

**Trigger Words 🤖:** When user mentions `csharp-testing` or related concepts

**Use Case 🤖:** Write and run tests

---

### customer-billing-ops

**Category:** Planning | **Path:** `everything-claude-code\skills\customer-billing-ops/`

**Description:** Operate customer billing workflows such as subscriptions, refunds, churn triage, billing-portal recovery, and plan analysis using connected billing tools like Stripe. Use when the user needs to help a customer, inspect subscription state, or manage revenue-impacting billing operations.

**Trigger Words 🤖:** When user mentions `customer-billing-ops` or related concepts

**Use Case 🤖:** Create implementation plans

---

### customs-trade-compliance

**Category:** Quality | **Path:** `everything-claude-code\skills\customs-trade-compliance/`

**Description:** Codified expertise for customs documentation, tariff classification, duty optimization, restricted party screening, and regulatory compliance across multiple jurisdictions. Informed by trade compliance specialists with 15+ years experience. Includes HS classification logic, Incoterms application, FTA utilization, and penalty mitigation. Use when handling customs clearance, tariff classification, trade compliance, import/export documentation, or duty optimization.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `customs-trade-compliance` or related concepts

**Use Case 🤖:** Check logical flow and argument coherence

---

### dart-flutter-patterns

**Category:** General | **Path:** `everything-claude-code\skills\dart-flutter-patterns/`

**Description:** Production-ready Dart and Flutter patterns covering null safety, immutable state, async composition, widget architecture, popular state management frameworks (BLoC, Riverpod, Provider), GoRouter navigation, Dio networking, Freezed code generation, and clean architecture.

**Trigger Words 🤖:** When user mentions `dart-flutter-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving dart flutter patterns (see description).

---

### dashboard-builder

**Category:** General | **Path:** `everything-claude-code\skills\dashboard-builder/`

**Description:** Build monitoring dashboards that answer real operator questions for Grafana, SigNoz, and similar platforms. Use when turning metrics into a working dashboard instead of a vanity board.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `dashboard-builder` or related concepts

**Use Case 🤖:** Use for tasks involving dashboard builder (see description).

---

### data-scraper-agent

**Category:** Data | **Path:** `everything-claude-code\skills\data-scraper-agent/`

**Description:** Build a fully automated AI-powered data collection agent for any public source — job boards, prices, news, GitHub, sports, anything. Scrapes on a schedule, enriches data with a free LLM (Gemini Flash), stores results in Notion/Sheets/Supabase, and learns from user feedback. Runs 100% free on GitHub Actions. Use when the user wants to monitor, collect, or track any public data automatically.

**Trigger Words 🤖:** When user mentions `data-scraper-agent` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### database-migrations

**Category:** Database | **Path:** `everything-claude-code\.kiro\skills\database-migrations/`

**Description:** Database migration best practices for schema changes, data migrations, rollbacks, and zero-downtime deployments across PostgreSQL, MySQL, and common ORMs (Prisma, Drizzle, Django, TypeORM, golang-migrate). Use when planning or implementing database schema changes.

**Trigger Words 🤖:** When user mentions `database-migrations` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### deep-research

**Category:** Research | **Path:** `everything-claude-code\.agents\skills\deep-research/`

**Description:** Multi-source deep research using firecrawl and exa MCPs. Searches the web, synthesizes findings, and delivers cited reports with source attribution. Use when the user wants thorough research on any topic with evidence and citations.

**Trigger Words 🤖:** When user mentions `deep-research` or related concepts

**Use Case 🤖:** Conduct in-depth literature research and analysis

---

### defi-amm-security

**Category:** Security | **Path:** `everything-claude-code\skills\defi-amm-security/`

**Description:** Security checklist for Solidity AMM contracts, liquidity pools, and swap flows. Covers reentrancy, CEI ordering, donation or inflation attacks, oracle manipulation, slippage, admin controls, and integer math.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `defi-amm-security` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### deployment-patterns

**Category:** Orchestration | **Path:** `everything-claude-code\.kiro\skills\deployment-patterns/`

**Description:** Deployment workflows, CI/CD pipeline patterns, Docker containerization, health checks, rollback strategies, and production readiness checklists for web applications. Use when setting up deployment infrastructure or planning releases.

**Trigger Words 🤖:** When user mentions `deployment-patterns` or related concepts

**Use Case 🤖:** Master orchestrator for multi-stage workflows

---

### design-system

**Category:** Workflow | **Path:** `everything-claude-code\skills\design-system/`

**Description:** Use this skill to generate or audit design systems, check visual consistency, and review PRs that touch styling.

**Trigger Words 🤖:** When user mentions `design-system` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### django-celery

**Category:** Design | **Path:** `everything-claude-code\skills\django-celery/`

**Description:** Django + Celery async task patterns — configuration, task design, beat scheduling, retries, canvas workflows, monitoring, and testing. Use when adding background jobs, scheduled tasks, or async processing to a Django app.

**Trigger Words 🤖:** When user mentions `django-celery` or related concepts

**Use Case 🤖:** Canvas-based visual design

---

### django-patterns

**Category:** API | **Path:** `everything-claude-code\docs\tr\skills\django-patterns/`

**Description:** DRF ile Django mimari desenleri, REST API tasarımı, ORM en iyi uygulamaları, caching, signal'ler, middleware ve production-grade Django uygulamaları.

**Trigger Words 🤖:** When user mentions `django-patterns` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### django-security

**Category:** Security | **Path:** `everything-claude-code\skills\django-security/`

**Description:** Django security best practices, authentication, authorization, CSRF protection, SQL injection prevention, XSS prevention, and secure deployment configurations.

**Trigger Words 🤖:** When user mentions `django-security` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### django-tdd

**Category:** General | **Path:** `everything-claude-code\skills\django-tdd/`

**Description:** Django testing strategies with pytest-django, TDD methodology, factory_boy, mocking, coverage, and testing Django REST Framework APIs.

**Trigger Words 🤖:** When user mentions `django-tdd` or related concepts

**Use Case 🤖:** Use for tasks involving django tdd (see description).

---

### django-verification

**Category:** Workflow | **Path:** `everything-claude-code\skills\django-verification/`

**Description:** Verification loop for Django projects: migrations, linting, tests with coverage, security scans, and deployment readiness checks before release or PR.

**Trigger Words 🤖:** When user mentions `django-verification` or related concepts

**Use Case 🤖:** Run recurring tasks on a timer interval

---

### dmux-workflows

**Category:** Agent | **Path:** `everything-claude-code\.agents\skills\dmux-workflows/`

**Description:** Multi-agent orchestration using dmux (tmux pane manager for AI agents). Patterns for parallel agent workflows across Claude Code, Codex, OpenCode, and other harnesses. Use when running multiple agent sessions in parallel or coordinating multi-agent development workflows.

**Trigger Words 🤖:** When user mentions `dmux-workflows` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### docker-patterns

**Category:** DevOps | **Path:** `everything-claude-code\.kiro\skills\docker-patterns/`

**Description:** Docker and Docker Compose patterns for local development, container security, networking, volume strategies, and multi-service orchestration. Use when setting up containerized development environments or reviewing Docker configurations.

**Trigger Words 🤖:** When user mentions `docker-patterns` or related concepts

**Use Case 🤖:** Container management and Docker configuration

---

### documentation-lookup

**Category:** Integration | **Path:** `everything-claude-code\.agents\skills\documentation-lookup/`

**Description:** Use up-to-date library and framework docs via Context7 MCP instead of training data. Activates for setup questions, API references, code examples, or when the user names a framework (e.g. React, Next.js, Prisma).

**Trigger Words 🤖:** When user mentions `documentation-lookup` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### dotnet-patterns

**Category:** General | **Path:** `everything-claude-code\skills\dotnet-patterns/`

**Description:** Idiomatic C# and .NET patterns, conventions, dependency injection, async/await, and best practices for building robust, maintainable .NET applications.

**Trigger Words 🤖:** When user mentions `dotnet-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving dotnet patterns (see description).

---

### e2e-testing

**Category:** Testing | **Path:** `everything-claude-code\.agents\skills\e2e-testing/`

**Description:** Playwright E2E testing patterns, Page Object Model, configuration, CI/CD integration, artifact management, and flaky test strategies.

**Trigger Words 🤖:** When user mentions `e2e-testing` or related concepts

**Use Case 🤖:** Write and run tests

---

### ecc-guide

**Category:** General | **Path:** `everything-claude-code\skills\ecc-guide/`

**Description:** Guide users through ECC's current agents, skills, commands, hooks, rules, install profiles, and project onboarding by reading the live repository surface before answering.

**Trigger Words 🤖:** When user mentions `ecc-guide` or related concepts

**Use Case 🤖:** Use for tasks involving ecc guide (see description).

---

### ecc-tools-cost-audit

**Category:** Workflow | **Path:** `everything-claude-code\skills\ecc-tools-cost-audit/`

**Description:** Evidence-first ECC Tools burn and billing audit workflow. Use when investigating runaway PR creation, quota bypass, premium-model leakage, duplicate jobs, or GitHub App cost spikes in the ECC Tools repo.

**Trigger Words 🤖:** When user mentions `ecc-tools-cost-audit` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### email-ops

**Category:** Workflow | **Path:** `everything-claude-code\skills\email-ops/`

**Description:** Evidence-first mailbox triage, drafting, send verification, and sent-mail-safe follow-up workflow for ECC. Use when the user wants to organize email, draft or send through the real mail surface, or prove what landed in Sent.

**Trigger Words 🤖:** When user mentions `email-ops` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### energy-procurement

**Category:** General | **Path:** `everything-claude-code\skills\energy-procurement/`

**Description:** Codified expertise for electricity and gas procurement, tariff optimization, demand charge management, renewable PPA evaluation, and multi-facility energy cost management. Informed by energy procurement managers with 15+ years experience at large commercial and industrial consumers. Includes market structure analysis, hedging strategies, load profiling, and sustainability reporting frameworks. Use when procuring energy, optimizing tariffs, managing demand charges, evaluating PPAs, or developing energy strategies.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `energy-procurement` or related concepts

**Use Case 🤖:** Use for tasks involving energy procurement (see description).

---

### enterprise-agent-ops

**Category:** Agent | **Path:** `everything-claude-code\skills\enterprise-agent-ops/`

**Description:** Operate long-lived agent workloads with observability, security boundaries, and lifecycle management.

**Trigger Words 🤖:** When user mentions `enterprise-agent-ops` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### error-handling

**Category:** General | **Path:** `everything-claude-code\skills\error-handling/`

**Description:** Patterns for robust error handling across TypeScript, Python, and Go. Covers typed errors, error boundaries, retries, circuit breakers, and user-facing error messages.

**Trigger Words 🤖:** When user mentions `error-handling` or related concepts

**Use Case 🤖:** Use for tasks involving error handling (see description).

---

### eval-harness

**Category:** Quality | **Path:** `everything-claude-code\.agents\skills\eval-harness/`

**Description:** Formal evaluation framework for Claude Code sessions implementing eval-driven development (EDD) principles

**Trigger Words 🤖:** When user mentions `eval-harness` or related concepts

**Use Case 🤖:** Evaluate and benchmark outputs

---

### everything-claude-code

**Category:** General | **Path:** `everything-claude-code\.agents\skills\everything-claude-code/`

**Description:** Development conventions and patterns for everything-claude-code. JavaScript project with conventional commits.

**Trigger Words 🤖:** When user mentions `everything-claude-code` or related concepts

**Use Case 🤖:** Use for tasks involving everything claude code (see description).

---

### everything-claude-code-conventions

**Category:** General | **Path:** `everything-claude-code\.claude\skills\everything-claude-code/`

**Description:** Development conventions and patterns for everything-claude-code. JavaScript project with conventional commits.

**Trigger Words 🤖:** When user mentions `everything-claude-code-conventions` or related concepts

**Use Case 🤖:** Use for tasks involving everything claude code conventions (see description).

---

### evm-token-decimals

**Category:** General | **Path:** `everything-claude-code\skills\evm-token-decimals/`

**Description:** Prevent silent decimal mismatch bugs across EVM chains. Covers runtime decimal lookup, chain-aware caching, bridged-token precision drift, and safe normalization for bots, dashboards, and DeFi tools.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `evm-token-decimals` or related concepts

**Use Case 🤖:** Use for tasks involving evm token decimals (see description).

---

### exa-search

**Category:** Research | **Path:** `everything-claude-code\.agents\skills\exa-search/`

**Description:** Neural search via Exa MCP for web, code, and company research. Use when the user needs web search, code examples, company intel, people lookup, or AI-powered deep research with Exa's neural search engine.

**Trigger Words 🤖:** When user mentions `exa-search` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### fal-ai-media

**Category:** Integration | **Path:** `everything-claude-code\.agents\skills\fal-ai-media/`

**Description:** Unified media generation via fal.ai MCP — image, video, and audio. Covers text-to-image (Nano Banana), text/image-to-video (Seedance, Kling, Veo 3), text-to-speech (CSM-1B), and video-to-audio (ThinkSound). Use when the user wants to generate images, videos, or audio with AI.

**Trigger Words 🤖:** When user mentions `fal-ai-media` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### fastapi-patterns

**Category:** Review | **Path:** `everything-claude-code\skills\fastapi-patterns/`

**Description:** FastAPI patterns for async APIs, dependency injection, Pydantic request and response models, OpenAPI docs, tests, security, and production readiness.

**Trigger Words 🤖:** When user mentions `fastapi-patterns` or related concepts

**Use Case 🤖:** Draft responses to peer review comments

---

### finance-billing-ops

**Category:** Workflow | **Path:** `everything-claude-code\skills\finance-billing-ops/`

**Description:** Evidence-first revenue, pricing, refunds, team-billing, and billing-model truth workflow for ECC. Use when the user wants a sales snapshot, pricing comparison, duplicate-charge diagnosis, or code-backed billing reality instead of generic payments advice.

**Trigger Words 🤖:** When user mentions `finance-billing-ops` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### flox-environments

**Category:** Workflow | **Path:** `everything-claude-code\skills\flox-environments/`

**Description:** Create reproducible, cross-platform development environments with Flox — a declarative environment manager built on Nix. ALWAYS use this skill when the user needs to: set up a project with system-level dependencies (compilers, databases, native libraries like openssl, libvips, BLAS, LAPACK); configure reproducible toolchains for Python, Node.js, Rust, Go, C/C++, Java, Ruby, Elixir, PHP, or any language; manage environments that must work identically across macOS and Linux; pin exact package versions for a team; run local services (PostgreSQL, Redis, Kafka) alongside development tools; onboard new developers with a single command; or solve 'works on my machine' problems. Especially valuable for AI-assisted and vibe coding — Flox lets agents install tools into a project-scoped environment without sudo, system pollution, or sandbox restrictions, and the resulting environment is committed to the repo so anyone can reproduce it instantly. Use this skill even if the user doesn't mention Flox — if they describe needing reproducible, declarative, cross-platform dev environments with system packages, this is the right tool. Also use when the user mentions .flox/, manifest.toml, flox activate, or FloxHub.

**Trigger Words 🤖:** When user mentions `flox-environments` or related concepts

**Use Case 🤖:** Launch and drive the project app to test changes

---

### flutter-dart-code-review

**Category:** Quality | **Path:** `everything-claude-code\skills\flutter-dart-code-review/`

**Description:** Library-agnostic Flutter/Dart code review checklist covering widget best practices, state management patterns (BLoC, Riverpod, Provider, GetX, MobX, Signals), Dart idioms, performance, accessibility, security, and clean architecture.

**Trigger Words 🤖:** When user mentions `flutter-dart-code-review` or related concepts

**Use Case 🤖:** Review code for quality and correctness

---

### foundation-models-on-device

**Category:** General | **Path:** `everything-claude-code\skills\foundation-models-on-device/`

**Description:** Apple FoundationModels framework for on-device LLM — text generation, guided generation with @Generable, tool calling, and snapshot streaming in iOS 26+.

**Trigger Words 🤖:** When user mentions `foundation-models-on-device` or related concepts

**Use Case 🤖:** Use for tasks involving foundation models on device (see description).

---

### frontend-design-direction

**Category:** Frontend | **Path:** `everything-claude-code\skills\frontend-design-direction/`

**Description:** Set an ECC-specific frontend design direction for production UI work. Use when building or improving websites, dashboards, applications, components, landing pages, visual tools, or any web UI that needs stronger product-specific design judgment.

**Trigger Words 🤖:** When user mentions `frontend-design-direction` or related concepts

**Use Case 🤖:** Build frontend UI components and patterns

---

### frontend-patterns

**Category:** Frontend | **Path:** `everything-claude-code\.agents\skills\frontend-patterns/`

**Description:** Frontend development patterns for React, Next.js, state management, performance optimization, and UI best practices.

**Trigger Words 🤖:** When user mentions `frontend-patterns` or related concepts

**Use Case 🤖:** Build frontend UI components and patterns

---

### frontend-slides

**Category:** Frontend | **Path:** `everything-claude-code\.agents\skills\frontend-slides/`

**Description:** Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when the user wants to build a presentation, convert a PPT/PPTX to web, or create slides for a talk/pitch. Helps non-designers discover their aesthetic through visual exploration rather than abstract choices.

**Trigger Words 🤖:** When user mentions `frontend-slides` or related concepts

**Use Case 🤖:** Build frontend UI components and patterns

---

### fsharp-testing

**Category:** Testing | **Path:** `everything-claude-code\skills\fsharp-testing/`

**Description:** F# testing patterns with xUnit, FsUnit, Unquote, FsCheck property-based testing, integration tests, and test organization best practices.

**Trigger Words 🤖:** When user mentions `fsharp-testing` or related concepts

**Use Case 🤖:** Write and run tests

---

### gan-style-harness

**Category:** Agent | **Path:** `everything-claude-code\skills\gan-style-harness/`

**Description:** GAN-inspired Generator-Evaluator agent harness for building high-quality applications autonomously. Based on Anthropic's March 2026 harness design paper.

**Trigger Words 🤖:** When user mentions `gan-style-harness` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### gateguard

**Category:** Data | **Path:** `everything-claude-code\skills\gateguard/`

**Description:** Fact-forcing gate that blocks Edit/Write/Bash (including MultiEdit) and demands concrete investigation (importers, data schemas, user instruction) before allowing the action. Measurably improves output quality by +2.25 points vs ungated agents.

**Trigger Words 🤖:** When user mentions `gateguard` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### gget

**Category:** Database | **Path:** `everything-claude-code\skills\scientific-pkg-gget/`

**Description:** gget CLI and Python workflow for quick genomic database queries, sequence lookup, BLAST-style searches, enrichment checks, and reproducible bioinformatics evidence logs.

**Trigger Words 🤖:** When user mentions `gget` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### git-workflow

**Category:** Workflow | **Path:** `everything-claude-code\skills\git-workflow/`

**Description:** Git workflow patterns including branching strategies, commit conventions, merge vs rebase, conflict resolution, and collaborative development best practices for teams of all sizes.

**Trigger Words 🤖:** When user mentions `git-workflow` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### github-ops

**Category:** Security | **Path:** `everything-claude-code\skills\github-ops/`

**Description:** GitHub repository operations, automation, and management. Issue triage, PR management, CI/CD operations, release management, and security monitoring using the gh CLI. Use when the user wants to manage GitHub issues, PRs, CI status, releases, contributors, stale items, or any GitHub operational task beyond simple git commands.

**Trigger Words 🤖:** When user mentions `github-ops` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### golang-patterns

**Category:** General | **Path:** `everything-claude-code\.kiro\skills\golang-patterns/`

**Description:** Go-specific design patterns and best practices including functional options, small interfaces, dependency injection, concurrency patterns, error handling, and package organization. Use when working with Go code to apply idiomatic Go patterns.

**Trigger Words 🤖:** When user mentions `golang-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving golang patterns (see description).

---

### golang-testing

**Category:** Testing | **Path:** `everything-claude-code\.kiro\skills\golang-testing/`

**Description:** Go testing best practices including table-driven tests, test helpers, benchmarking, race detection, coverage analysis, and integration testing patterns. Use when writing or improving Go tests.

**Trigger Words 🤖:** When user mentions `golang-testing` or related concepts

**Use Case 🤖:** Write and run tests

---

### google-workspace-ops

**Category:** Workflow | **Path:** `everything-claude-code\skills\google-workspace-ops/`

**Description:** Operate across Google Drive, Docs, Sheets, and Slides as one workflow surface for plans, trackers, decks, and shared documents. Use when the user needs to find, summarize, edit, migrate, or clean up Google Workspace assets without dropping to raw tool calls.

**Trigger Words 🤖:** When user mentions `google-workspace-ops` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### healthcare-cdss-patterns

**Category:** General | **Path:** `everything-claude-code\skills\healthcare-cdss-patterns/`

**Description:** Clinical Decision Support System (CDSS) development patterns. Drug interaction checking, dose validation, clinical scoring (NEWS2, qSOFA), alert severity classification, and integration into EMR workflows.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `healthcare-cdss-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving healthcare cdss patterns (see description).

---

### healthcare-emr-patterns

**Category:** Accessibility | **Path:** `everything-claude-code\skills\healthcare-emr-patterns/`

**Description:** EMR/EHR development patterns for healthcare applications. Clinical safety, encounter workflows, prescription generation, clinical decision support integration, and accessibility-first UI for medical data entry.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `healthcare-emr-patterns` or related concepts

**Use Case 🤖:** Design and audit accessible digital products (WCAG)

---

### healthcare-eval-harness

**Category:** Quality | **Path:** `everything-claude-code\skills\healthcare-eval-harness/`

**Description:** Patient safety evaluation harness for healthcare application deployments. Automated test suites for CDSS accuracy, PHI exposure, clinical workflow integrity, and integration compliance. Blocks deployments on safety failures.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `healthcare-eval-harness` or related concepts

**Use Case 🤖:** Evaluate and benchmark outputs

---

### healthcare-phi-compliance

**Category:** Data | **Path:** `everything-claude-code\skills\healthcare-phi-compliance/`

**Description:** Protected Health Information (PHI) and Personally Identifiable Information (PII) compliance patterns for healthcare applications. Covers data classification, access control, audit trails, encryption, and common leak vectors.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `healthcare-phi-compliance` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### hermes-imports

**Category:** Agent | **Path:** `everything-claude-code\skills\hermes-imports/`

**Description:** Convert local Hermes operator workflows into sanitized ECC skills and release-pack artifacts. Use when preparing a Hermes workflow for public ECC reuse without leaking private workspace state, credentials, or local-only paths.

**Trigger Words 🤖:** When user mentions `hermes-imports` or related concepts

**Use Case 🤖:** Digital twin agent with learning and memory capabilities

---

### hexagonal-architecture

**Category:** General | **Path:** `everything-claude-code\skills\hexagonal-architecture/`

**Description:** Design, implement, and refactor Ports & Adapters systems with clear domain boundaries, dependency inversion, and testable use-case orchestration across TypeScript, Java, Kotlin, and Go services.

**Trigger Words 🤖:** When user mentions `hexagonal-architecture` or related concepts

**Use Case 🤖:** Use for tasks involving hexagonal architecture (see description).

---

### hipaa-compliance

**Category:** Security | **Path:** `everything-claude-code\skills\hipaa-compliance/`

**Description:** HIPAA-specific entrypoint for healthcare privacy and security work. Use when a task is explicitly framed around HIPAA, PHI handling, covered entities, BAAs, breach posture, or US healthcare compliance requirements.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `hipaa-compliance` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### homelab-network-readiness

**Category:** General | **Path:** `everything-claude-code\skills\homelab-network-readiness/`

**Description:** Readiness checklist for homelab VLAN segmentation, local DNS filtering, and WireGuard-style remote access before changing router, firewall, DHCP, or VPN configuration.

**Trigger Words 🤖:** When user mentions `homelab-network-readiness` or related concepts

**Use Case 🤖:** Use for tasks involving homelab network readiness (see description).

---

### homelab-network-setup

**Category:** General | **Path:** `everything-claude-code\skills\homelab-network-setup/`

**Description:** Practical home and homelab network planning for gateways, switches, access points, IP ranges, DHCP reservations, DNS, cabling, and common beginner mistakes.

**Trigger Words 🤖:** When user mentions `homelab-network-setup` or related concepts

**Use Case 🤖:** Use for tasks involving homelab network setup (see description).

---

### homelab-pihole-dns

**Category:** General | **Path:** `everything-claude-code\skills\homelab-pihole-dns/`

**Description:** Pi-hole installation, blocklist management, DNS-over-HTTPS setup, DHCP integration, local DNS records, and troubleshooting broken DNS resolution on a home network.

**Trigger Words 🤖:** When user mentions `homelab-pihole-dns` or related concepts

**Use Case 🤖:** Use for tasks involving homelab pihole dns (see description).

---

### homelab-vlan-segmentation

**Category:** Configuration | **Path:** `everything-claude-code\skills\homelab-vlan-segmentation/`

**Description:** Segmenting home networks into VLANs for IoT, guest, trusted, and server traffic using UniFi, pfSense/OPNsense, and MikroTik — including switch trunk config, firewall rules, and wireless SSID mapping.

**Trigger Words 🤖:** When user mentions `homelab-vlan-segmentation` or related concepts

**Use Case 🤖:** Configure settings and preferences

---

### homelab-wireguard-vpn

**Category:** General | **Path:** `everything-claude-code\skills\homelab-wireguard-vpn/`

**Description:** WireGuard VPN server setup, peer configuration, key generation, split tunneling vs full tunnel routing, and remote access to a home network from mobile and laptop clients.

**Trigger Words 🤖:** When user mentions `homelab-wireguard-vpn` or related concepts

**Use Case 🤖:** Use for tasks involving homelab wireguard vpn (see description).

---

### hookify-rules

**Category:** Integration | **Path:** `everything-claude-code\skills\hookify-rules/`

**Description:** This skill should be used when the user asks to create a hookify rule, write a hook rule, configure hookify, add a hookify rule, or needs guidance on hookify rule syntax and patterns.

**Trigger Words 🤖:** When user mentions `hookify-rules` or related concepts

**Use Case 🤖:** Configure and manage hooks

---

### inventory-demand-planning

**Category:** General | **Path:** `everything-claude-code\skills\inventory-demand-planning/`

**Description:** Codified expertise for demand forecasting, safety stock optimization, replenishment planning, and promotional lift estimation at multi-location retailers. Informed by demand planners with 15+ years experience managing hundreds of SKUs. Includes forecasting method selection, ABC/XYZ analysis, seasonal transition management, and vendor negotiation frameworks. Use when forecasting demand, setting safety stock, planning replenishment, managing promotions, or optimizing inventory levels.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `inventory-demand-planning` or related concepts

**Use Case 🤖:** Use for tasks involving inventory demand planning (see description).

---

### investor-materials

**Category:** Editing | **Path:** `everything-claude-code\.agents\skills\investor-materials/`

**Description:** Create and update pitch decks, one-pagers, investor memos, accelerator applications, financial models, and fundraising materials. Use when the user needs investor-facing documents, projections, use-of-funds tables, milestone plans, or materials that must stay internally consistent across multiple fundraising assets.

**Trigger Words 🤖:** When user mentions `investor-materials` or related concepts

**Use Case 🤖:** Revise and update content

---

### investor-outreach

**Category:** Editing | **Path:** `everything-claude-code\.agents\skills\investor-outreach/`

**Description:** Draft cold emails, warm intro blurbs, follow-ups, update emails, and investor communications for fundraising. Use when the user wants outreach to angels, VCs, strategic investors, or accelerators and needs concise, personalized, investor-facing messaging.

**Trigger Words 🤖:** When user mentions `investor-outreach` or related concepts

**Use Case 🤖:** Revise and update content

---

### ios-icon-gen

**Category:** API | **Path:** `everything-claude-code\skills\ios-icon-gen/`

**Description:** Generate iOS app icons as PNG imagesets for Xcode asset catalogs from SF Symbols (5000+ Apple-native) or Iconify API (275k+ open source icons from 200+ collections). Use when generating icons, creating icon assets, adding icons to asset catalog, or searching for icons for iOS projects.

**Trigger Words 🤖:** When user mentions `ios-icon-gen` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### iterative-retrieval

**Category:** General | **Path:** `everything-claude-code\docs\ko-KR\skills\iterative-retrieval/`

**Description:** 서브에이전트 컨텍스트 문제를 해결하기 위한 점진적 컨텍스트 검색 개선 패턴

**Trigger Words 🤖:** When user mentions `iterative-retrieval` or related concepts

**Use Case 🤖:** Use for tasks involving iterative retrieval (see description).

---

### java-coding-standards

**Category:** General | **Path:** `everything-claude-code\skills\java-coding-standards/`

**Description:** Java coding standards for Spring Boot and Quarkus services: naming, immutability, Optional usage, streams, exceptions, generics, CDI, reactive patterns, and project layout. Automatically applies framework-specific conventions.

**Trigger Words 🤖:** When user mentions `java-coding-standards` or related concepts

**Use Case 🤖:** Use for tasks involving java coding standards (see description).

---

### jira-integration

**Category:** Integration | **Path:** `everything-claude-code\skills\jira-integration/`

**Description:** Use this skill when retrieving Jira tickets, analyzing requirements, updating ticket status, adding comments, or transitioning issues. Provides Jira API patterns via MCP or direct REST calls.

**Trigger Words 🤖:** When user mentions `jira-integration` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### jpa-patterns

**Category:** General | **Path:** `everything-claude-code\docs\tr\skills\jpa-patterns/`

**Description:** Spring Boot'ta entity tasarımı, ilişkiler, sorgu optimizasyonu, transaction'lar, auditing, indeksleme, sayfalama ve pooling için JPA/Hibernate kalıpları.

**Trigger Words 🤖:** When user mentions `jpa-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving jpa patterns (see description).

---

### knowledge-ops

**Category:** Integration | **Path:** `everything-claude-code\skills\knowledge-ops/`

**Description:** Knowledge base management, ingestion, sync, and retrieval across multiple storage layers (local files, MCP memory, vector stores, Git repos). Use when the user wants to save, organize, sync, deduplicate, or search across their knowledge systems.

**Trigger Words 🤖:** When user mentions `knowledge-ops` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### kotlin-coroutines-flows

**Category:** General | **Path:** `everything-claude-code\skills\kotlin-coroutines-flows/`

**Description:** Kotlin Coroutines and Flow patterns for Android and KMP — structured concurrency, Flow operators, StateFlow, error handling, and testing.

**Trigger Words 🤖:** When user mentions `kotlin-coroutines-flows` or related concepts

**Use Case 🤖:** Use for tasks involving kotlin coroutines flows (see description).

---

### kotlin-exposed-patterns

**Category:** Architecture | **Path:** `everything-claude-code\skills\kotlin-exposed-patterns/`

**Description:** JetBrains Exposed ORM patterns including DSL queries, DAO pattern, transactions, HikariCP connection pooling, Flyway migrations, and repository pattern.

**Trigger Words 🤖:** When user mentions `kotlin-exposed-patterns` or related concepts

**Use Case 🤖:** Software design patterns

---

### kotlin-ktor-patterns

**Category:** General | **Path:** `everything-claude-code\skills\kotlin-ktor-patterns/`

**Description:** Ktor server patterns including routing DSL, plugins, authentication, Koin DI, kotlinx.serialization, WebSockets, and testApplication testing.

**Trigger Words 🤖:** When user mentions `kotlin-ktor-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving kotlin ktor patterns (see description).

---

### kotlin-patterns

**Category:** General | **Path:** `everything-claude-code\docs\tr\skills\kotlin-patterns/`

**Description:** Coroutine'ler, null safety ve DSL builder'lar ile sağlam, verimli ve sürdürülebilir Kotlin uygulamaları oluşturmak için idiomatic Kotlin kalıpları, en iyi uygulamalar ve konvansiyonlar.

**Trigger Words 🤖:** When user mentions `kotlin-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving kotlin patterns (see description).

---

### kotlin-testing

**Category:** Testing | **Path:** `everything-claude-code\docs\tr\skills\kotlin-testing/`

**Description:** Kotest, MockK, coroutine testi, property-based testing ve Kover coverage ile Kotlin test kalıpları. İdiomatic Kotlin uygulamalarıyla TDD metodolojisini takip eder.

**Trigger Words 🤖:** When user mentions `kotlin-testing` or related concepts

**Use Case 🤖:** Write and run tests

---

### laravel-patterns

**Category:** API | **Path:** `everything-claude-code\docs\tr\skills\laravel-patterns/`

**Description:** Laravel architecture patterns, routing/controllers, Eloquent ORM, service layers, queues, events, caching, and API resources for production apps.

**Trigger Words 🤖:** When user mentions `laravel-patterns` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### laravel-plugin-discovery

**Category:** Integration | **Path:** `everything-claude-code\skills\laravel-plugin-discovery/`

**Description:** Discover and evaluate Laravel packages via LaraPlugins.io MCP. Use when the user wants to find plugins, check package health, or assess Laravel/PHP compatibility.

**Trigger Words 🤖:** When user mentions `laravel-plugin-discovery` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### laravel-security

**Category:** Security | **Path:** `everything-claude-code\docs\tr\skills\laravel-security/`

**Description:** Laravel security best practices for authn/authz, validation, CSRF, mass assignment, file uploads, secrets, rate limiting, and secure deployment.

**Trigger Words 🤖:** When user mentions `laravel-security` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### laravel-tdd

**Category:** Database | **Path:** `everything-claude-code\docs\tr\skills\laravel-tdd/`

**Description:** Test-driven development for Laravel with PHPUnit and Pest, factories, database testing, fakes, and coverage targets.

**Trigger Words 🤖:** When user mentions `laravel-tdd` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### laravel-verification

**Category:** Workflow | **Path:** `everything-claude-code\skills\laravel-verification/`

**Description:** Verification loop for Laravel projects: env checks, linting, static analysis, tests with coverage, security scans, and deployment readiness.

**Trigger Words 🤖:** When user mentions `laravel-verification` or related concepts

**Use Case 🤖:** Run recurring tasks on a timer interval

---

### lead-intelligence

**Category:** Orchestration | **Path:** `everything-claude-code\skills\lead-intelligence/`

**Description:** AI-native lead intelligence and outreach pipeline. Replaces Apollo, Clay, and ZoomInfo with agent-powered signal scoring, mutual ranking, warm path discovery, source-derived voice modeling, and channel-specific outreach across email, LinkedIn, and X. Use when the user wants to find, qualify, and reach high-value contacts.

**Trigger Words 🤖:** When user mentions `lead-intelligence` or related concepts

**Use Case 🤖:** Master orchestrator for multi-stage workflows

---

### liquid-glass-design

**Category:** General | **Path:** `everything-claude-code\skills\liquid-glass-design/`

**Description:** iOS 26 Liquid Glass design system — dynamic glass material with blur, reflection, and interactive morphing for SwiftUI, UIKit, and WidgetKit.

**Trigger Words 🤖:** When user mentions `liquid-glass-design` or related concepts

**Use Case 🤖:** Use for tasks involving liquid glass design (see description).

---

### literature-review

**Category:** Workflow | **Path:** `everything-claude-code\skills\scientific-thinking-literature-review/`

**Description:** Systematic literature-review workflow for academic, biomedical, technical, and scientific topics, including search planning, source screening, synthesis, citation checks, and evidence logging.

**Trigger Words 🤖:** When user mentions `literature-review` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### llm-trading-agent-security

**Category:** Security | **Path:** `everything-claude-code\skills\llm-trading-agent-security/`

**Description:** Security patterns for autonomous trading agents with wallet or transaction authority. Covers prompt injection, spend limits, pre-send simulation, circuit breakers, MEV protection, and key handling.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `llm-trading-agent-security` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### logistics-exception-management

**Category:** General | **Path:** `everything-claude-code\skills\logistics-exception-management/`

**Description:** Codified expertise for handling freight exceptions, shipment delays, damages, losses, and carrier disputes. Informed by logistics professionals with 15+ years operational experience. Includes escalation protocols, carrier-specific behaviors, claims procedures, and judgment frameworks. Use when handling shipping exceptions, freight claims, delivery issues, or carrier disputes.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `logistics-exception-management` or related concepts

**Use Case 🤖:** Use for tasks involving logistics exception management (see description).

---

### make-interfaces-feel-better

**Category:** General | **Path:** `everything-claude-code\skills\make-interfaces-feel-better/`

**Description:** Apply concrete design-engineering details that make interfaces feel polished. Use when reviewing or improving UI spacing, typography, borders, shadows, motion, hit areas, icons, text wrapping, and interaction states.

**Trigger Words 🤖:** When user mentions `make-interfaces-feel-better` or related concepts

**Use Case 🤖:** Use for tasks involving make interfaces feel better (see description).

---

### manim-video

**Category:** General | **Path:** `everything-claude-code\skills\manim-video/`

**Description:** Build reusable Manim explainers for technical concepts, graphs, system diagrams, and product walkthroughs, then hand off to the wider ECC video stack if needed. Use when the user wants a clean animated explainer rather than a generic talking-head script.

**Trigger Words 🤖:** When user mentions `manim-video` or related concepts

**Use Case 🤖:** Use for tasks involving manim video (see description).

---

### market-research

**Category:** General | **Path:** `everything-claude-code\.agents\skills\market-research/`

**Description:** Conduct market research, competitive analysis, investor due diligence, and industry intelligence with source attribution and decision-oriented summaries. Use when the user wants market sizing, competitor comparisons, fund research, technology scans, or research that informs business decisions.

**Trigger Words 🤖:** When user mentions `market-research` or related concepts

**Use Case 🤖:** Use for tasks involving market research (see description).

---

### mcp-server-patterns

**Category:** Integration | **Path:** `everything-claude-code\.agents\skills\mcp-server-patterns/`

**Description:** Build MCP servers with Node/TypeScript SDK — tools, resources, prompts, Zod validation, stdio vs Streamable HTTP. Use Context7 or official MCP docs for latest API.

**Trigger Words 🤖:** When user mentions `mcp-server-patterns` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### messages-ops

**Category:** Workflow | **Path:** `everything-claude-code\skills\messages-ops/`

**Description:** Evidence-first live messaging workflow for ECC. Use when the user wants to read texts or DMs, recover a recent one-time code, inspect a thread before replying, or prove which message source was actually checked.

**Trigger Words 🤖:** When user mentions `messages-ops` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### mle-workflow

**Category:** Workflow | **Path:** `everything-claude-code\.agents\skills\mle-workflow/`

**Description:** Production machine-learning engineering workflow for data contracts, reproducible training, model evaluation, deployment, monitoring, and rollback. Use when building, reviewing, or hardening ML systems beyond one-off notebooks.

**Trigger Words 🤖:** When user mentions `mle-workflow` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### motion-advanced

**Category:** API | **Path:** `everything-claude-code\skills\motion-advanced/`

**Description:** Advanced motion patterns for React / Next.js — drag & drop, gestures, text animations, SVG path drawing, custom hooks, imperative sequences (useAnimate), loaders, and the full API decision tree. Requires motion-foundations.

**Version:** 1.0  
**Trigger Words 🤖:** When user mentions `motion-advanced` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### motion-foundations

**Category:** Accessibility | **Path:** `everything-claude-code\skills\motion-foundations/`

**Description:** Motion tokens, spring presets, performance rules, device adaptation, accessibility enforcement, and SSR safety for React / Next.js using motion/react. Foundation layer — all other motion skills depend on this.

**Version:** 1.0  
**Trigger Words 🤖:** When user mentions `motion-foundations` or related concepts

**Use Case 🤖:** Design and audit accessible digital products (WCAG)

---

### motion-patterns

**Category:** General | **Path:** `everything-claude-code\skills\motion-patterns/`

**Description:** Production-ready animation patterns for React / Next.js — button, modal, toast, stagger, page transitions, exit animations, scroll, and layout — built on motion-foundations tokens and springs.

**Version:** 1.0  
**Trigger Words 🤖:** When user mentions `motion-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving motion patterns (see description).

---

### motion-ui

**Category:** General | **Path:** `everything-claude-code\skills\motion-ui/`

**Description:** Production-ready UI motion system for React/Next.js. Use when implementing animations, transitions, or motion patterns.

**Trigger Words 🤖:** When user mentions `motion-ui` or related concepts

**Use Case 🤖:** Use for tasks involving motion ui (see description).

---

### mysql-patterns

**Category:** General | **Path:** `everything-claude-code\skills\mysql-patterns/`

**Description:** MySQL and MariaDB schema, query, indexing, transaction, replication, and connection-pool patterns for production backends.

**Trigger Words 🤖:** When user mentions `mysql-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving mysql patterns (see description).

---

### nanoclaw-repl

**Category:** General | **Path:** `everything-claude-code\skills\nanoclaw-repl/`

**Description:** Operate and extend NanoClaw v2, ECC's zero-dependency session-aware REPL built on claude -p.

**Trigger Words 🤖:** When user mentions `nanoclaw-repl` or related concepts

**Use Case 🤖:** Use for tasks involving nanoclaw repl (see description).

---

### nestjs-patterns

**Category:** Configuration | **Path:** `everything-claude-code\skills\nestjs-patterns/`

**Description:** NestJS architecture patterns for modules, controllers, providers, DTO validation, guards, interceptors, config, and production-grade TypeScript backends.

**Trigger Words 🤖:** When user mentions `nestjs-patterns` or related concepts

**Use Case 🤖:** Configure settings and preferences

---

### netmiko-ssh-automation

**Category:** Configuration | **Path:** `everything-claude-code\skills\netmiko-ssh-automation/`

**Description:** Safe Python Netmiko patterns for read-only collection, bounded batch SSH, TextFSM parsing, guarded config changes, timeouts, and network automation error handling.

**Trigger Words 🤖:** When user mentions `netmiko-ssh-automation` or related concepts

**Use Case 🤖:** Configure settings and preferences

---

### network-bgp-diagnostics

**Category:** General | **Path:** `everything-claude-code\skills\network-bgp-diagnostics/`

**Description:** Diagnostics-only BGP troubleshooting patterns for neighbor state, route exchange, prefix policy, AS path inspection, and safe evidence collection.

**Trigger Words 🤖:** When user mentions `network-bgp-diagnostics` or related concepts

**Use Case 🤖:** Use for tasks involving network bgp diagnostics (see description).

---

### network-config-validation

**Category:** Configuration | **Path:** `everything-claude-code\skills\network-config-validation/`

**Description:** Pre-deployment checks for router and switch configuration, including dangerous commands, duplicate addresses, subnet overlaps, stale references, management-plane risk, and IOS-style security hygiene.

**Trigger Words 🤖:** When user mentions `network-config-validation` or related concepts

**Use Case 🤖:** Configure settings and preferences

---

### network-interface-health

**Category:** General | **Path:** `everything-claude-code\skills\network-interface-health/`

**Description:** Diagnose interface errors, drops, CRCs, duplex mismatches, flapping, speed negotiation issues, and counter trends on routers, switches, and Linux hosts.

**Trigger Words 🤖:** When user mentions `network-interface-health` or related concepts

**Use Case 🤖:** Use for tasks involving network interface health (see description).

---

### nextjs-turbopack

**Category:** General | **Path:** `everything-claude-code\.agents\skills\nextjs-turbopack/`

**Description:** Next.js 16+ and Turbopack — incremental bundling, FS caching, dev speed, and when to use Turbopack vs webpack.

**Trigger Words 🤖:** When user mentions `nextjs-turbopack` or related concepts

**Use Case 🤖:** Use for tasks involving nextjs turbopack (see description).

---

### nodejs-keccak256

**Category:** General | **Path:** `everything-claude-code\skills\nodejs-keccak256/`

**Description:** Prevent Ethereum hashing bugs in JavaScript and TypeScript. Node's sha3-256 is NIST SHA3, not Ethereum Keccak-256, and silently breaks selectors, signatures, storage slots, and address derivation.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `nodejs-keccak256` or related concepts

**Use Case 🤖:** Use for tasks involving nodejs keccak256 (see description).

---

### nutrient-document-processing

**Category:** Documents | **Path:** `everything-claude-code\skills\nutrient-document-processing/`

**Description:** Process, convert, OCR, extract, redact, sign, and fill documents using the Nutrient DWS API. Works with PDFs, DOCX, XLSX, PPTX, HTML, and images.

**Trigger Words 🤖:** When user mentions `nutrient-document-processing` or related concepts

**Use Case 🤖:** Excel spreadsheet creation and editing

---

### nuxt4-patterns

**Category:** Data | **Path:** `everything-claude-code\skills\nuxt4-patterns/`

**Description:** Nuxt 4 app patterns for hydration safety, performance, route rules, lazy loading, and SSR-safe data fetching with useFetch and useAsyncData.

**Trigger Words 🤖:** When user mentions `nuxt4-patterns` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### openclaw-persona-forge

**Category:** Agent | **Path:** `everything-claude-code\skills\openclaw-persona-forge/`

**Description:** 为 OpenClaw AI Agent 锻造完整的龙虾灵魂方案。根据用户偏好或随机抽卡， 输出身份定位、灵魂描述(SOUL.md)、角色化底线规则、名字和头像生图提示词。 如当前环境提供已审核的生图 skill，可自动生成统一风格头像图片。 当用户需要创建、设计或定制 OpenClaw 龙虾灵魂时使用。 不适用于：微调已有 SOUL.md、非 OpenClaw 平台的角色设计、纯工具型无性格 Agent。 触发词：龙虾灵魂、虾魂、OpenClaw 灵魂、养虾灵魂、龙虾角色、龙虾定位、 龙虾剧本杀角色、龙虾游戏角色、龙虾 NPC、龙虾性格、龙虾背景故事、 lobster soul、lobster character、抽卡、随机龙虾、龙虾 SOUL、gacha。

**Trigger Words 🤖:** When user mentions `openclaw-persona-forge` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### opensource-pipeline

**Category:** Orchestration | **Path:** `everything-claude-code\skills\opensource-pipeline/`

**Description:** Open-source pipeline: fork, sanitize, and package private projects for safe public release. Chains 3 agents (forker, sanitizer, packager). Triggers: '/opensource', 'open source this', 'make this public', 'prepare for open source'.

**Trigger Words 🤖:** When user mentions `opensource-pipeline` or related concepts

**Use Case 🤖:** Master orchestrator for multi-stage workflows

---

### perl-patterns

**Category:** General | **Path:** `everything-claude-code\skills\perl-patterns/`

**Description:** Modern Perl 5.36+ idioms, best practices, and conventions for building robust, maintainable Perl applications.

**Trigger Words 🤖:** When user mentions `perl-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving perl patterns (see description).

---

### perl-security

**Category:** Security | **Path:** `everything-claude-code\skills\perl-security/`

**Description:** Comprehensive Perl security covering taint mode, input validation, safe process execution, DBI parameterized queries, web security (XSS/SQLi/CSRF), and perlcritic security policies.

**Trigger Words 🤖:** When user mentions `perl-security` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### perl-testing

**Category:** Testing | **Path:** `everything-claude-code\skills\perl-testing/`

**Description:** Perl testing patterns using Test2::V0, Test::More, prove runner, mocking, coverage with Devel::Cover, and TDD methodology.

**Trigger Words 🤖:** When user mentions `perl-testing` or related concepts

**Use Case 🤖:** Write and run tests

---

### plan-orchestrate

**Category:** Planning | **Path:** `everything-claude-code\skills\plan-orchestrate/`

**Description:** Read a plan document, decompose it into steps, design a per-step agent chain from the ECC catalogue, and emit ready-to-paste /orchestrate custom prompts. Generative only — never invokes /orchestrate itself. Use when the user has a multi-step plan and wants to drive it through orchestrate without composing chains by hand.

**Trigger Words 🤖:** When user mentions `plan-orchestrate` or related concepts

**Use Case 🤖:** Create implementation plans

---

### plankton-code-quality

**Category:** Writing | **Path:** `everything-claude-code\skills\plankton-code-quality/`

**Description:** Write-time code quality enforcement using Plankton — auto-formatting, linting, and Claude-powered fixes on every file edit via hooks.

**Trigger Words 🤖:** When user mentions `plankton-code-quality` or related concepts

**Use Case 🤖:** Draft or plan content

---

### postgres-patterns

**Category:** Database | **Path:** `everything-claude-code\.kiro\skills\postgres-patterns/`

**Description:** PostgreSQL database patterns for query optimization, schema design, indexing, and security. Quick reference for common patterns, index types, data types, and anti-pattern detection. Based on Supabase best practices.

**Trigger Words 🤖:** When user mentions `postgres-patterns` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### prisma-patterns

**Category:** General | **Path:** `everything-claude-code\skills\prisma-patterns/`

**Description:** Prisma ORM patterns for TypeScript backends — schema design, query optimization, transactions, pagination, and critical traps like updateMany returning count not records, $transaction timeouts, migrate dev resetting the DB, @updatedAt skipped on bulk writes, and serverless connection exhaustion.

**Trigger Words 🤖:** When user mentions `prisma-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving prisma patterns (see description).

---

### product-capability

**Category:** Planning | **Path:** `everything-claude-code\.agents\skills\product-capability/`

**Description:** Translate PRD intent, roadmap asks, or product discussions into an implementation-ready capability plan that exposes constraints, invariants, interfaces, and unresolved decisions before multi-service work starts. Use when the user needs an ECC-native PRD-to-SRS lane instead of vague planning prose.

**Trigger Words 🤖:** When user mentions `product-capability` or related concepts

**Use Case 🤖:** Create implementation plans

---

### product-lens

**Category:** Workflow | **Path:** `everything-claude-code\skills\product-lens/`

**Description:** Use this skill to validate the "why" before building, run product diagnostics, and pressure-test product direction before the request becomes an implementation contract.

**Trigger Words 🤖:** When user mentions `product-lens` or related concepts

**Use Case 🤖:** Launch and drive the project app to test changes

---

### production-audit

**Category:** Data | **Path:** `everything-claude-code\skills\production-audit/`

**Description:** Local-evidence production readiness audit for shipped apps, pre-launch reviews, post-merge checks, and "what breaks in prod?" questions without sending repo data to an external audit service.

**Trigger Words 🤖:** When user mentions `production-audit` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### production-scheduling

**Category:** Review | **Path:** `everything-claude-code\skills\production-scheduling/`

**Description:** Codified expertise for production scheduling, job sequencing, line balancing, changeover optimization, and bottleneck resolution in discrete and batch manufacturing. Informed by production schedulers with 15+ years experience. Includes TOC/drum-buffer-rope, SMED, OEE analysis, disruption response frameworks, and ERP/MES interaction patterns. Use when scheduling production, resolving bottlenecks, optimizing changeovers, responding to disruptions, or balancing manufacturing lines.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `production-scheduling` or related concepts

**Use Case 🤖:** Draft responses to peer review comments

---

### project-flow-ops

**Category:** General | **Path:** `everything-claude-code\skills\project-flow-ops/`

**Description:** Operate execution flow across GitHub and Linear by triaging issues and pull requests, linking active work, and keeping GitHub public-facing while Linear remains the internal execution layer. Use when the user wants backlog control, PR triage, or GitHub-to-Linear coordination.

**Trigger Words 🤖:** When user mentions `project-flow-ops` or related concepts

**Use Case 🤖:** Use for tasks involving project flow ops (see description).

---

### prompt-optimizer

**Category:** Writing | **Path:** `everything-claude-code\skills\prompt-optimizer/`

**Description:** Analyze raw prompts, identify intent and gaps, match ECC components (skills/commands/agents/hooks), and output a ready-to-paste optimized prompt. Advisory role only — never executes the task itself. TRIGGER when: user says "optimize prompt", "improve my prompt", "how to write a prompt for", "help me prompt", "rewrite this prompt", or explicitly asks to enhance prompt quality. Also triggers on Chinese equivalents: "优化prompt", "改进prompt", "怎么写prompt", "帮我优化这个指令". DO NOT TRIGGER when: user wants the task executed directly, or says "just do it" / "直接做". DO NOT TRIGGER when user says "优化代码", "优化性能", "optimize performance", "optimize this code" — those are refactoring/performance tasks, not prompt optimization.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `prompt-optimizer` or related concepts

**Use Case 🤖:** Draft or plan content

---

### pubmed-database

**Category:** Database | **Path:** `everything-claude-code\skills\scientific-db-pubmed-database/`

**Description:** Direct PubMed and NCBI E-utilities search workflows for biomedical literature, MeSH queries, PMID lookup, citation retrieval, and API-backed literature monitoring.

**Trigger Words 🤖:** When user mentions `pubmed-database` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### python-patterns

**Category:** General | **Path:** `everything-claude-code\.kiro\skills\python-patterns/`

**Description:** Python-specific design patterns and best practices including protocols, dataclasses, context managers, decorators, async/await, type hints, and package organization. Use when working with Python code to apply Pythonic patterns.

**Trigger Words 🤖:** When user mentions `python-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving python patterns (see description).

---

### python-testing

**Category:** Testing | **Path:** `everything-claude-code\.kiro\skills\python-testing/`

**Description:** Python testing best practices using pytest including fixtures, parametrization, mocking, coverage analysis, async testing, and test organization. Use when writing or improving Python tests.

**Trigger Words 🤖:** When user mentions `python-testing` or related concepts

**Use Case 🤖:** Write and run tests

---

### pytorch-patterns

**Category:** Data | **Path:** `everything-claude-code\skills\pytorch-patterns/`

**Description:** PyTorch deep learning patterns and best practices for building robust, efficient, and reproducible training pipelines, model architectures, and data loading.

**Trigger Words 🤖:** When user mentions `pytorch-patterns` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### quality-nonconformance

**Category:** Data | **Path:** `everything-claude-code\skills\quality-nonconformance/`

**Description:** Codified expertise for quality control, non-conformance investigation, root cause analysis, corrective action, and supplier quality management in regulated manufacturing. Informed by quality engineers with 15+ years experience across FDA, IATF 16949, and AS9100 environments. Includes NCR lifecycle management, CAPA systems, SPC interpretation, and audit methodology. Use when investigating non-conformances, performing root cause analysis, managing CAPAs, interpreting SPC data, or handling supplier quality issues.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `quality-nonconformance` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### quarkus-patterns

**Category:** Backend | **Path:** `everything-claude-code\docs\tr\skills\quarkus-patterns/`

**Description:** Quarkus 3.x LTS architecture patterns with Camel for messaging, RESTful API design, CDI services, data access with Panache, and async processing. Use for Java Quarkus backend work with event-driven architectures.

**Trigger Words 🤖:** When user mentions `quarkus-patterns` or related concepts

**Use Case 🤖:** Build backend services and APIs

---

### quarkus-security

**Category:** Security | **Path:** `everything-claude-code\docs\tr\skills\quarkus-security/`

**Description:** Quarkus Security best practices for authentication, authorization, JWT/OIDC, RBAC, input validation, CSRF, secrets management, and dependency security.

**Trigger Words 🤖:** When user mentions `quarkus-security` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### quarkus-tdd

**Category:** Testing | **Path:** `everything-claude-code\docs\tr\skills\quarkus-tdd/`

**Description:** Test-driven development for Quarkus 3.x LTS using JUnit 5, Mockito, REST Assured, Camel testing, and JaCoCo. Use when adding features, fixing bugs, or refactoring event-driven services.

**Trigger Words 🤖:** When user mentions `quarkus-tdd` or related concepts

**Use Case 🤖:** Write and run tests

---

### quarkus-verification

**Category:** Workflow | **Path:** `everything-claude-code\docs\tr\skills\quarkus-verification/`

**Description:** Verification loop for Quarkus projects: build, static analysis, tests with coverage, security scans, native compilation, and diff review before release or PR.

**Trigger Words 🤖:** When user mentions `quarkus-verification` or related concepts

**Use Case 🤖:** Run recurring tasks on a timer interval

---

### ralphinho-rfc-pipeline

**Category:** Orchestration | **Path:** `everything-claude-code\skills\ralphinho-rfc-pipeline/`

**Description:** RFC-driven multi-agent DAG execution pattern with quality gates, merge queues, and work unit orchestration.

**Trigger Words 🤖:** When user mentions `ralphinho-rfc-pipeline` or related concepts

**Use Case 🤖:** Master orchestrator for multi-stage workflows

---

### recsys-pipeline-architect

**Category:** Orchestration | **Path:** `everything-claude-code\skills\recsys-pipeline-architect/`

**Description:** Design composable recommendation, ranking, and feed pipelines using the six-stage Source→Hydrator→Filter→Scorer→Selector→SideEffect framework popularized by xAI's open-sourced For You algorithm. Use this skill whenever the user is building any system that picks "the top K items for a (user, context)" — social feeds, content CMSs, RAG rerankers, task prioritizers, notification triage, search reranking, ad ranking.

**Trigger Words 🤖:** When user mentions `recsys-pipeline-architect` or related concepts

**Use Case 🤖:** Master orchestrator for multi-stage workflows

---

### redis-patterns

**Category:** Data | **Path:** `everything-claude-code\skills\redis-patterns/`

**Description:** Redis data structure patterns, caching strategies, distributed locks, rate limiting, pub/sub, and connection management for production applications.

**Trigger Words 🤖:** When user mentions `redis-patterns` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### regex-vs-llm-structured-text

**Category:** General | **Path:** `everything-claude-code\skills\regex-vs-llm-structured-text/`

**Description:** Decision framework for choosing between regex and LLM when parsing structured text — start with regex, add LLM only for low-confidence edge cases.

**Trigger Words 🤖:** When user mentions `regex-vs-llm-structured-text` or related concepts

**Use Case 🤖:** Use for tasks involving regex vs llm structured text (see description).

---

### remotion-video-creation

**Category:** General | **Path:** `everything-claude-code\skills\remotion-video-creation/`

**Description:** Best practices for Remotion - Video creation in React. 29 domain-specific rules covering 3D, animations, audio, captions, charts, transitions, and more.

**Trigger Words 🤖:** When user mentions `remotion-video-creation` or related concepts

**Use Case 🤖:** Use for tasks involving remotion video creation (see description).

---

### repo-scan

**Category:** General | **Path:** `everything-claude-code\skills\repo-scan/`

**Description:** Cross-stack source code asset audit — classifies every file, detects embedded third-party libraries, and delivers actionable four-level verdicts per module with interactive HTML reports.

**Trigger Words 🤖:** When user mentions `repo-scan` or related concepts

**Use Case 🤖:** Use for tasks involving repo scan (see description).

---

### research-ops

**Category:** Workflow | **Path:** `everything-claude-code\skills\research-ops/`

**Description:** Evidence-first current-state research workflow for ECC. Use when the user wants fresh facts, comparisons, enrichment, or a recommendation built from current public evidence and any supplied local context.

**Trigger Words 🤖:** When user mentions `research-ops` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### returns-reverse-logistics

**Category:** Architecture | **Path:** `everything-claude-code\skills\returns-reverse-logistics/`

**Description:** Codified expertise for returns authorization, receipt and inspection, disposition decisions, refund processing, fraud detection, and warranty claims management. Informed by returns operations managers with 15+ years experience. Includes grading frameworks, disposition economics, fraud pattern recognition, and vendor recovery processes. Use when handling product returns, reverse logistics, refund decisions, return fraud detection, or warranty claims.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `returns-reverse-logistics` or related concepts

**Use Case 🤖:** Software design patterns

---

### rules-distill

**Category:** General | **Path:** `everything-claude-code\skills\rules-distill/`

**Description:** Scan skills to extract cross-cutting principles and distill them into rules — append, revise, or create new rule files

**Trigger Words 🤖:** When user mentions `rules-distill` or related concepts

**Use Case 🤖:** Use for tasks involving rules distill (see description).

---

### rust-patterns

**Category:** General | **Path:** `everything-claude-code\docs\tr\skills\rust-patterns/`

**Description:** Idiomatic Rust patterns, ownership, error handling, traits, concurrency, and best practices for building safe, performant applications.

**Trigger Words 🤖:** When user mentions `rust-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving rust patterns (see description).

---

### rust-testing

**Category:** General | **Path:** `everything-claude-code\docs\tr\skills\rust-testing/`

**Description:** Rust testing patterns including unit tests, integration tests, async testing, property-based testing, mocking, and coverage. Follows TDD methodology.

**Trigger Words 🤖:** When user mentions `rust-testing` or related concepts

**Use Case 🤖:** Use for tasks involving rust testing (see description).

---

### safety-guard

**Category:** Meta | **Path:** `everything-claude-code\skills\safety-guard/`

**Description:** Use this skill to prevent destructive operations when working on production systems or running agents autonomously.

**Trigger Words 🤖:** When user mentions `safety-guard` or related concepts

**Use Case 🤖:** Create, manage, or discover skills

---

### santa-method

**Category:** Workflow | **Path:** `everything-claude-code\skills\santa-method/`

**Description:** Multi-agent adversarial verification with convergence loop. Two independent review agents must both pass before output ships.

**Trigger Words 🤖:** When user mentions `santa-method` or related concepts

**Use Case 🤖:** Run recurring tasks on a timer interval

---

### scholar-evaluation

**Category:** References | **Path:** `everything-claude-code\skills\scientific-thinking-scholar-evaluation/`

**Description:** Structured scholarly-work evaluation for papers, proposals, literature reviews, methods sections, evidence quality, citation support, and research-writing feedback.

**Trigger Words 🤖:** When user mentions `scholar-evaluation` or related concepts

**Use Case 🤖:** Manage, format, or check citations

---

### search-first

**Category:** Research | **Path:** `everything-claude-code\.kiro\skills\search-first/`

**Description:** Research-before-coding workflow. Search for existing tools, libraries, and patterns before writing custom code. Systematizes the "search for existing solutions before implementing" approach. Use when starting new features or adding functionality.

**Trigger Words 🤖:** When user mentions `search-first` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### security-bounty-hunter

**Category:** Security | **Path:** `everything-claude-code\skills\security-bounty-hunter/`

**Description:** Hunt for exploitable, bounty-worthy security issues in repositories. Focuses on remotely reachable vulnerabilities that qualify for real reports instead of noisy local-only findings.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `security-bounty-hunter` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### security-review

**Category:** Workflow | **Path:** `everything-claude-code\.agents\skills\security-review/`

**Description:** Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive features. Provides comprehensive security checklist and patterns.

**Trigger Words 🤖:** When user mentions `security-review` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### security-scan

**Category:** Security | **Path:** `everything-claude-code\skills\security-scan/`

**Description:** Scan your Claude Code configuration (.claude/ directory) for security vulnerabilities, misconfigurations, and injection risks using AgentShield. Checks CLAUDE.md, settings.json, MCP servers, hooks, and agent definitions.

**Trigger Words 🤖:** When user mentions `security-scan` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### seo

**Category:** Content | **Path:** `everything-claude-code\skills\seo/`

**Description:** Audit, plan, and implement SEO improvements across technical SEO, on-page optimization, structured data, Core Web Vitals, and content strategy. Use when the user wants better search visibility, SEO remediation, schema markup, sitemap/robots work, or keyword mapping.

**Trigger Words 🤖:** When user mentions `seo` or related concepts

**Use Case 🤖:** Content generation and management

---

### skill-comply

**Category:** Meta | **Path:** `everything-claude-code\skills\skill-comply/`

**Description:** Visualize whether skills, rules, and agent definitions are actually followed — auto-generates scenarios at 3 prompt strictness levels, runs agents, classifies behavioral sequences, and reports compliance rates with full tool call timelines

**Trigger Words 🤖:** When user mentions `skill-comply` or related concepts

**Use Case 🤖:** Create, manage, or discover skills

---

### skill-scout

**Category:** Meta | **Path:** `everything-claude-code\skills\skill-scout/`

**Description:** Search existing local, marketplace, GitHub, and web skill sources before creating a new skill. Use when the user wants to create, build, fork, or find a skill for a workflow.

**Trigger Words 🤖:** When user mentions `skill-scout` or related concepts

**Use Case 🤖:** Create, manage, or discover skills

---

### skill-stocktake

**Category:** Meta | **Path:** `everything-claude-code\skills\skill-stocktake/`

**Description:** Use when auditing Claude skills and commands for quality. Supports Quick Scan (changed skills only) and Full Stocktake modes with sequential subagent batch evaluation.

**Trigger Words 🤖:** When user mentions `skill-stocktake` or related concepts

**Use Case 🤖:** Create, manage, or discover skills

---

### social-graph-ranker

**Category:** Workflow | **Path:** `everything-claude-code\skills\social-graph-ranker/`

**Description:** Weighted social-graph ranking for warm intro discovery, bridge scoring, and network gap analysis across X and LinkedIn. Use when the user wants the reusable graph-ranking engine itself, not the broader outreach or network-maintenance workflow layered on top of it.

**Trigger Words 🤖:** When user mentions `social-graph-ranker` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### springboot-patterns

**Category:** Backend | **Path:** `everything-claude-code\docs\tr\skills\springboot-patterns/`

**Description:** Spring Boot architecture patterns, REST API design, layered services, data access, caching, async processing, and logging. Use for Java Spring Boot backend work.

**Trigger Words 🤖:** When user mentions `springboot-patterns` or related concepts

**Use Case 🤖:** Build backend services and APIs

---

### springboot-security

**Category:** Security | **Path:** `everything-claude-code\docs\tr\skills\springboot-security/`

**Description:** Spring Security best practices for authn/authz, validation, CSRF, secrets, headers, rate limiting, and dependency security in Java Spring Boot services.

**Trigger Words 🤖:** When user mentions `springboot-security` or related concepts

**Use Case 🤖:** Security review and vulnerability scanning

---

### springboot-tdd

**Category:** Testing | **Path:** `everything-claude-code\docs\tr\skills\springboot-tdd/`

**Description:** Test-driven development for Spring Boot using JUnit 5, Mockito, MockMvc, Testcontainers, and JaCoCo. Use when adding features, fixing bugs, or refactoring.

**Trigger Words 🤖:** When user mentions `springboot-tdd` or related concepts

**Use Case 🤖:** Write and run tests

---

### springboot-verification

**Category:** Workflow | **Path:** `everything-claude-code\docs\tr\skills\springboot-verification/`

**Description:** Verification loop for Spring Boot projects: build, static analysis, tests with coverage, security scans, and diff review before release or PR.

**Trigger Words 🤖:** When user mentions `springboot-verification` or related concepts

**Use Case 🤖:** Run recurring tasks on a timer interval

---

### strategic-compact

**Category:** General | **Path:** `everything-claude-code\.agents\skills\strategic-compact/`

**Description:** Suggests manual context compaction at logical intervals to preserve context through task phases rather than arbitrary auto-compaction.

**Trigger Words 🤖:** When user mentions `strategic-compact` or related concepts

**Use Case 🤖:** Use for tasks involving strategic compact (see description).

---

### swift-actor-persistence

**Category:** Context | **Path:** `everything-claude-code\skills\swift-actor-persistence/`

**Description:** Thread-safe data persistence in Swift using actors — in-memory cache with file-backed storage, eliminating data races by design.

**Trigger Words 🤖:** When user mentions `swift-actor-persistence` or related concepts

**Use Case 🤖:** Manage persistent memory and context

---

### swift-concurrency-6-2

**Category:** General | **Path:** `everything-claude-code\skills\swift-concurrency-6-2/`

**Description:** Swift 6.2 Approachable Concurrency — single-threaded by default, @concurrent for explicit background offloading, isolated conformances for main actor types.

**Trigger Words 🤖:** When user mentions `swift-concurrency-6-2` or related concepts

**Use Case 🤖:** Use for tasks involving swift concurrency 6 2 (see description).

---

### swift-protocol-di-testing

**Category:** General | **Path:** `everything-claude-code\skills\swift-protocol-di-testing/`

**Description:** Protocol-based dependency injection for testable Swift code — mock file system, network, and external APIs using focused protocols and Swift Testing.

**Trigger Words 🤖:** When user mentions `swift-protocol-di-testing` or related concepts

**Use Case 🤖:** Use for tasks involving swift protocol di testing (see description).

---

### swiftui-patterns

**Category:** General | **Path:** `everything-claude-code\skills\swiftui-patterns/`

**Description:** SwiftUI architecture patterns, state management with @Observable, view composition, navigation, performance optimization, and modern iOS/macOS UI best practices.

**Trigger Words 🤖:** When user mentions `swiftui-patterns` or related concepts

**Use Case 🤖:** Use for tasks involving swiftui patterns (see description).

---

### tdd-workflow

**Category:** Workflow | **Path:** `everything-claude-code\.agents\skills\tdd-workflow/`

**Description:** Use this skill when writing new features, fixing bugs, or refactoring code. Enforces test-driven development with 80%+ coverage including unit, integration, and E2E tests.

**Trigger Words 🤖:** When user mentions `tdd-workflow` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### team-builder

**Category:** Collaboration | **Path:** `everything-claude-code\skills\team-builder/`

**Description:** Interactive agent picker for composing and dispatching parallel teams

**Trigger Words 🤖:** When user mentions `team-builder` or related concepts

**Use Case 🤖:** Coordinate multi-author workflows

---

### terminal-ops

**Category:** Workflow | **Path:** `everything-claude-code\skills\terminal-ops/`

**Description:** Evidence-first repo execution workflow for ECC. Use when the user wants a command run, a repo checked, a CI failure debugged, or a narrow fix pushed with exact proof of what was executed and verified.

**Trigger Words 🤖:** When user mentions `terminal-ops` or related concepts

**Use Case 🤖:** Launch and drive the project app to test changes

---

### tinystruct-patterns

**Category:** Database | **Path:** `everything-claude-code\skills\tinystruct-patterns/`

**Description:** Expert guidance for developing with the tinystruct Java framework. Use when working on the tinystruct codebase or any project built on tinystruct — including creating Application classes, @Action-mapped routes, unit tests, ActionRegistry, HTTP/CLI dual-mode handling, the built-in HTTP server, the event system, JSON with Builder/Builders, database persistence with AbstractData, POJO generation, Server-Sent Events (SSE), file uploads, and outbound HTTP networking.

**Trigger Words 🤖:** When user mentions `tinystruct-patterns` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### token-budget-advisor

**Category:** Review | **Path:** `everything-claude-code\skills\token-budget-advisor/`

**Description:** Offers the user an informed choice about how much response depth to consume before answering. Use this skill when the user explicitly wants to control response length, depth, or token budget. TRIGGER when: "token budget", "token count", "token usage", "token limit", "response length", "answer depth", "short version", "brief answer", "detailed answer", "exhaustive answer", "respuesta corta vs larga", "cuántos tokens", "ahorrar tokens", "responde al 50%", "dame la versión corta", "quiero controlar cuánto usas", or clear variants where the user is explicitly asking to control answer size or depth. DO NOT TRIGGER when: user has already specified a level in the current session (maintain it), the request is clearly a one-word answer, or "token" refers to auth/session/payment tokens rather than response size.

**Trigger Words 🤖:** When user mentions `token-budget-advisor` or related concepts

**Use Case 🤖:** Draft responses to peer review comments

---

### ui-demo

**Category:** General | **Path:** `everything-claude-code\skills\ui-demo/`

**Description:** Record polished UI demo videos using Playwright. Use when the user asks to create a demo, walkthrough, screen recording, or tutorial video of a web application. Produces WebM videos with visible cursor, natural pacing, and professional feel.

**Trigger Words 🤖:** When user mentions `ui-demo` or related concepts

**Use Case 🤖:** Use for tasks involving ui demo (see description).

---

### ui-to-vue

**Category:** General | **Path:** `everything-claude-code\skills\ui-to-vue/`

**Description:** Use when the user has UI screenshots or design exports that need batch conversion into Vue 3 components, especially with Vant, Element Plus, or Ant Design Vue.

**Trigger Words 🤖:** When user mentions `ui-to-vue` or related concepts

**Use Case 🤖:** Use for tasks involving ui to vue (see description).

---

### uncloud

**Category:** General | **Path:** `everything-claude-code\skills\uncloud/`

**Description:** Use when managing an Uncloud cluster — deploying services, configuring Caddy ingress, adding static proxy routes for non-cluster devices, publishing ports, scaling, inspecting logs, or managing machines and volumes with the `uc` CLI.

**Trigger Words 🤖:** When user mentions `uncloud` or related concepts

**Use Case 🤖:** Use for tasks involving uncloud (see description).

---

### unified-notifications-ops

**Category:** Workflow | **Path:** `everything-claude-code\skills\unified-notifications-ops/`

**Description:** Operate notifications as one ECC-native workflow across GitHub, Linear, desktop alerts, hooks, and connected communication surfaces. Use when the real problem is alert routing, deduplication, escalation, or inbox collapse.

**Trigger Words 🤖:** When user mentions `unified-notifications-ops` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### uspto-database

**Category:** Database | **Path:** `everything-claude-code\skills\scientific-db-uspto-database/`

**Description:** USPTO patent and trademark data workflow for official record lookup, PatentSearch queries, TSDR checks, assignment data, and reproducible IP research logs.

**Trigger Words 🤖:** When user mentions `uspto-database` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### verification-loop

**Category:** Workflow | **Path:** `everything-claude-code\.agents\skills\verification-loop/`

**Description:** A comprehensive verification system for Claude Code sessions.

**Trigger Words 🤖:** When user mentions `verification-loop` or related concepts

**Use Case 🤖:** Run recurring tasks on a timer interval

---

### video-editing

**Category:** Text Refinement | **Path:** `everything-claude-code\.agents\skills\video-editing/`

**Description:** AI-assisted video editing workflows for cutting, structuring, and augmenting real footage. Covers the full pipeline from raw capture through FFmpeg, Remotion, ElevenLabs, fal.ai, and final polish in Descript or CapCut. Use when the user wants to edit video, cut footage, create vlogs, or build video content.

**Trigger Words 🤖:** When user mentions `video-editing` or related concepts

**Use Case 🤖:** Polish/refine English academic text for submission

---

### videodb

**Category:** Research | **Path:** `everything-claude-code\skills\videodb/`

**Description:** See, Understand, Act on video and audio. See- ingest from local files, URLs, RTSP/live feeds, or live record desktop; return realtime context and playable stream links. Understand- extract frames, build visual/semantic/temporal indexes, and search moments with timestamps and auto-clips. Act- transcode and normalize (codec, fps, resolution, aspect ratio), perform timeline edits (subtitles, text/image overlays, branding, audio overlays, dubbing, translation), generate media assets (image, audio, video), and create real time alerts for events from live streams or desktop capture.

**Trigger Words 🤖:** When user mentions `videodb` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### visa-doc-translate

**Category:** General | **Path:** `everything-claude-code\skills\visa-doc-translate/`

**Description:** Translate visa application documents (images) to English and create a bilingual PDF with original and translation

**Trigger Words 🤖:** When user mentions `visa-doc-translate` or related concepts

**Use Case 🤖:** Use for tasks involving visa doc translate (see description).

---

### vite-patterns

**Category:** Configuration | **Path:** `everything-claude-code\skills\vite-patterns/`

**Description:** Vite build tool patterns including config, plugins, HMR, env variables, proxy setup, SSR, library mode, dependency pre-bundling, and build optimization. Activate when working with vite.config.ts, Vite plugins, or Vite-based projects.

**Trigger Words 🤖:** When user mentions `vite-patterns` or related concepts

**Use Case 🤖:** Configure settings and preferences

---

### windows-desktop-e2e

**Category:** General | **Path:** `everything-claude-code\skills\windows-desktop-e2e/`

**Description:** E2E testing for Windows native desktop apps (WPF, WinForms, Win32/MFC, Qt) using pywinauto and Windows UI Automation.

**Trigger Words 🤖:** When user mentions `windows-desktop-e2e` or related concepts

**Use Case 🤖:** Use for tasks involving windows desktop e2e (see description).

---

### workspace-surface-audit

**Category:** Integration | **Path:** `everything-claude-code\skills\workspace-surface-audit/`

**Description:** Audit the active repo, MCP servers, plugins, connectors, env surfaces, and harness setup, then recommend the highest-value ECC-native skills, hooks, agents, and operator workflows. Use when the user wants help setting up Claude Code or understanding what capabilities are actually available in their environment.

**Trigger Words 🤖:** When user mentions `workspace-surface-audit` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### x-api

**Category:** API | **Path:** `everything-claude-code\.agents\skills\x-api/`

**Description:** X/Twitter API integration for posting tweets, threads, reading timelines, search, and analytics. Covers OAuth auth patterns, rate limits, and platform-native content posting. Use when the user wants to interact with X programmatically.

**Trigger Words 🤖:** When user mentions `x-api` or related concepts

**Use Case 🤖:** Design and implement APIs


## hermes-agent {{hermes-agent}}

> 164 skills — use Ctrl+F to search.

### 1password

**Category:** General | **Path:** `hermes-agent\optional-skills\security\1password/`

**Description:** Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in, and reading/injecting secrets for commands.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `1password` or related concepts

**Use Case 🤖:** Use for tasks involving 1password (see description).

---

### 3-statement-model

**Category:** General | **Path:** `hermes-agent\optional-skills\finance\3-statement-model/`

**Description:** Build fully-integrated 3-statement models (IS, BS, CF) in Excel with working capital schedules, D&A roll-forwards, debt schedule, and the plugs that make cash and retained earnings tie. Pairs with excel-author.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `3-statement-model` or related concepts

**Use Case 🤖:** Use for tasks involving 3 statement model (see description).

---

### adversarial-ux-test

**Category:** Testing | **Path:** `hermes-agent\optional-skills\dogfood\adversarial-ux-test/`

**Description:** Roleplay the most difficult, tech-resistant user for your product. Browse the app as that persona, find every UX pain point, then filter complaints through a pragmatism layer to separate real problems from noise. Creates actionable tickets from genuine issues only.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `adversarial-ux-test` or related concepts

**Use Case 🤖:** Write and run tests

---

### agentmail

**Category:** Agent | **Path:** `hermes-agent\optional-skills\email\agentmail/`

**Description:** Give the agent its own dedicated email inbox via AgentMail. Send, receive, and manage email autonomously using agent-owned email addresses (e.g. hermes-agent@agentmail.to).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `agentmail` or related concepts

**Use Case 🤖:** Digital twin agent with learning and memory capabilities

---

### airtable

**Category:** API | **Path:** `hermes-agent\skills\productivity\airtable/`

**Description:** Airtable REST API via curl. Records CRUD, filters, upserts.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `airtable` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### apple-notes

**Category:** Research | **Path:** `hermes-agent\skills\apple\apple-notes/`

**Description:** Manage Apple Notes via memo CLI: create, search, edit.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `apple-notes` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### apple-reminders

**Category:** General | **Path:** `hermes-agent\skills\apple\apple-reminders/`

**Description:** Apple Reminders via remindctl: add, list, complete.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `apple-reminders` or related concepts

**Use Case 🤖:** Use for tasks involving apple reminders (see description).

---

### architecture-diagram

**Category:** General | **Path:** `hermes-agent\skills\creative\architecture-diagram/`

**Description:** Dark-themed SVG architecture/cloud/infra diagrams as HTML.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `architecture-diagram` or related concepts

**Use Case 🤖:** Use for tasks involving architecture diagram (see description).

---

### arxiv

**Category:** Research | **Path:** `hermes-agent\skills\research\arxiv/`

**Description:** Search arXiv papers by keyword, author, category, or ID.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `arxiv` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### ascii-art

**Category:** Creative | **Path:** `hermes-agent\skills\creative\ascii-art/`

**Description:** ASCII art: pyfiglet, cowsay, boxes, image-to-ascii.

**Version:** 4.0.0  
**Trigger Words 🤖:** When user mentions `ascii-art` or related concepts

**Use Case 🤖:** Algorithmic art generation

---

### ascii-video

**Category:** General | **Path:** `hermes-agent\skills\creative\ascii-video/`

**Description:** ASCII video: convert video/audio to colored ASCII MP4/GIF.

**Trigger Words 🤖:** When user mentions `ascii-video` or related concepts

**Use Case 🤖:** Use for tasks involving ascii video (see description).

---

### audiocraft-audio-generation

**Category:** General | **Path:** `hermes-agent\skills\mlops\models\audiocraft/`

**Description:** AudioCraft: MusicGen text-to-music, AudioGen text-to-sound.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `audiocraft-audio-generation` or related concepts

**Use Case 🤖:** Use for tasks involving audiocraft audio generation (see description).

---

### axolotl

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\training\axolotl/`

**Description:** Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `axolotl` or related concepts

**Use Case 🤖:** Use for tasks involving axolotl (see description).

---

### baoyu-article-illustrator

**Category:** General | **Path:** `hermes-agent\skills\creative\baoyu-article-illustrator/`

**Description:** Article illustrations: type × style × palette consistency.

**Version:** 1.57.0  
**Trigger Words 🤖:** When user mentions `baoyu-article-illustrator` or related concepts

**Use Case 🤖:** Use for tasks involving baoyu article illustrator (see description).

---

### baoyu-comic

**Category:** General | **Path:** `hermes-agent\skills\creative\baoyu-comic/`

**Description:** Knowledge comics (知识漫画): educational, biography, tutorial.

**Version:** 1.56.1  
**Trigger Words 🤖:** When user mentions `baoyu-comic` or related concepts

**Use Case 🤖:** Use for tasks involving baoyu comic (see description).

---

### baoyu-infographic

**Category:** General | **Path:** `hermes-agent\skills\creative\baoyu-infographic/`

**Description:** Infographics: 21 layouts x 21 styles (信息图, 可视化).

**Version:** 1.56.1  
**Trigger Words 🤖:** When user mentions `baoyu-infographic` or related concepts

**Use Case 🤖:** Use for tasks involving baoyu infographic (see description).

---

### bioinformatics

**Category:** General | **Path:** `hermes-agent\optional-skills\research\bioinformatics/`

**Description:** Gateway to 400+ bioinformatics skills from bioSkills and ClawBio. Covers genomics, transcriptomics, single-cell, variant calling, pharmacogenomics, metagenomics, structural biology, and more. Fetches domain-specific reference material on demand.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `bioinformatics` or related concepts

**Use Case 🤖:** Use for tasks involving bioinformatics (see description).

---

### blackbox

**Category:** API | **Path:** `hermes-agent\optional-skills\autonomous-ai-agents\blackbox/`

**Description:** Delegate coding tasks to Blackbox AI CLI agent. Multi-model agent with built-in judge that runs tasks through multiple LLMs and picks the best result. Requires the blackbox CLI and a Blackbox AI API key.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `blackbox` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### blender-mcp

**Category:** Integration | **Path:** `hermes-agent\optional-skills\creative\blender-mcp/`

**Description:** Control Blender directly from Hermes via socket connection to the blender-mcp addon. Create 3D objects, materials, animations, and run arbitrary Blender Python (bpy) code. Use when user wants to create or modify anything in Blender.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `blender-mcp` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### blogwatcher

**Category:** General | **Path:** `hermes-agent\skills\research\blogwatcher/`

**Description:** Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool.

**Version:** 2.0.0  
**Trigger Words 🤖:** When user mentions `blogwatcher` or related concepts

**Use Case 🤖:** Use for tasks involving blogwatcher (see description).

---

### canvas

**Category:** Design | **Path:** `hermes-agent\optional-skills\productivity\canvas/`

**Description:** Canvas LMS integration — fetch enrolled courses and assignments using API token authentication.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `canvas` or related concepts

**Use Case 🤖:** Canvas-based visual design

---

### chroma

**Category:** Database | **Path:** `hermes-agent\optional-skills\mlops\chroma/`

**Description:** Open-source embedding database for AI applications. Store embeddings and metadata, perform vector and full-text search, filter by metadata. Simple 4-function API. Scales from notebooks to production clusters. Use for semantic search, RAG applications, or document retrieval. Best for local development and open-source projects.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `chroma` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### claude-code

**Category:** General | **Path:** `hermes-agent\skills\autonomous-ai-agents\claude-code/`

**Description:** Delegate coding to Claude Code CLI (features, PRs).

**Version:** 2.2.0  
**Trigger Words 🤖:** When user mentions `claude-code` or related concepts

**Use Case 🤖:** Use for tasks involving claude code (see description).

---

### claude-design

**Category:** General | **Path:** `hermes-agent\skills\creative\claude-design/`

**Description:** Design one-off HTML artifacts (landing, deck, prototype).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `claude-design` or related concepts

**Use Case 🤖:** Use for tasks involving claude design (see description).

---

### clip

**Category:** Content | **Path:** `hermes-agent\optional-skills\mlops\clip/`

**Description:** OpenAI's model connecting vision and language. Enables zero-shot image classification, image-text matching, and cross-modal retrieval. Trained on 400M image-text pairs. Use for image search, content moderation, or vision-language tasks without fine-tuning. Best for general-purpose image understanding.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `clip` or related concepts

**Use Case 🤖:** Content generation and management

---

### codebase-inspection

**Category:** General | **Path:** `hermes-agent\skills\github\codebase-inspection/`

**Description:** Inspect codebases w/ pygount: LOC, languages, ratios.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `codebase-inspection` or related concepts

**Use Case 🤖:** Use for tasks involving codebase inspection (see description).

---

### codex

**Category:** General | **Path:** `hermes-agent\skills\autonomous-ai-agents\codex/`

**Description:** Delegate coding to OpenAI Codex CLI (features, PRs).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `codex` or related concepts

**Use Case 🤖:** Use for tasks involving codex (see description).

---

### comfyui

**Category:** Workflow | **Path:** `hermes-agent\skills\creative\comfyui/`

**Description:** Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, run workflows with parameter injection. Uses the official comfy-cli for lifecycle and direct REST/WebSocket API for execution.

**Version:** 5.1.0  
**Trigger Words 🤖:** When user mentions `comfyui` or related concepts

**Use Case 🤖:** Launch and drive the project app to test changes

---

### comps-analysis

**Category:** General | **Path:** `hermes-agent\optional-skills\finance\comps-analysis/`

**Description:** Build comparable company analysis in Excel — operating metrics, valuation multiples, statistical benchmarking vs peer sets. Pairs with excel-author. Use for public-company valuation, IPO pricing, sector benchmarking, or outlier detection.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `comps-analysis` or related concepts

**Use Case 🤖:** Use for tasks involving comps analysis (see description).

---

### concept-diagrams

**Category:** Meta | **Path:** `hermes-agent\optional-skills\creative\concept-diagrams/`

**Description:** Generate flat, minimal light/dark-aware SVG diagrams as standalone HTML files, using a unified educational visual language with 9 semantic color ramps, sentence-case typography, and automatic dark mode. Best suited for educational and non-software visuals — physics setups, chemistry mechanisms, math curves, physical objects (aircraft, turbines, smartphones, mechanical watches), anatomy, floor plans, cross-sections, narrative journeys (lifecycle of X, process of Y), hub-spoke system integrations (smart city, IoT), and exploded layer views. If a more specialized skill exists for the subject (dedicated software/cloud architecture, hand-drawn sketches, animated explainers, etc.), prefer that — otherwise this skill can also serve as a general-purpose SVG diagram fallback with a clean educational look. Ships with 15 example diagrams.

**Version:** 0.1.0  
**Trigger Words 🤖:** When user mentions `concept-diagrams` or related concepts

**Use Case 🤖:** Create, manage, or discover skills

---

### darwinian-evolver

**Category:** Workflow | **Path:** `hermes-agent\optional-skills\research\darwinian-evolver/`

**Description:** Evolve prompts/regex/SQL/code with Imbue's evolution loop.

**Version:** 0.1.0  
**Trigger Words 🤖:** When user mentions `darwinian-evolver` or related concepts

**Use Case 🤖:** Run recurring tasks on a timer interval

---

### dcf-model

**Category:** General | **Path:** `hermes-agent\optional-skills\finance\dcf-model/`

**Description:** Build institutional-quality DCF valuation models in Excel — revenue projections, FCF build, WACC, terminal value, Bear/Base/Bull scenarios, 5x5 sensitivity tables. Pairs with excel-author. Use for intrinsic-value equity analysis.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `dcf-model` or related concepts

**Use Case 🤖:** Use for tasks involving dcf model (see description).

---

### debugging-hermes-tui-commands

**Category:** Agent | **Path:** `hermes-agent\skills\software-development\debugging-hermes-tui-commands/`

**Description:** Debug Hermes TUI slash commands: Python, gateway, Ink UI.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `debugging-hermes-tui-commands` or related concepts

**Use Case 🤖:** Digital twin agent with learning and memory capabilities

---

### design-md

**Category:** General | **Path:** `hermes-agent\skills\creative\design-md/`

**Description:** Author/validate/export Google's DESIGN.md token spec files.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `design-md` or related concepts

**Use Case 🤖:** Use for tasks involving design md (see description).

---

### distributed-llm-pretraining-torchtitan

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\torchtitan/`

**Description:** Provides PyTorch-native distributed LLM pretraining using torchtitan with 4D parallelism (FSDP2, TP, PP, CP). Use when pretraining Llama 3.1, DeepSeek V3, or custom models at scale from 8 to 512+ GPUs with Float8, torch.compile, and distributed checkpointing.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `distributed-llm-pretraining-torchtitan` or related concepts

**Use Case 🤖:** Use for tasks involving distributed llm pretraining torchtitan (see description).

---

### docker-management

**Category:** DevOps | **Path:** `hermes-agent\optional-skills\devops\docker-management/`

**Description:** Manage Docker containers, images, volumes, networks, and Compose stacks — lifecycle ops, debugging, cleanup, and Dockerfile optimization.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `docker-management` or related concepts

**Use Case 🤖:** Container management and Docker configuration

---

### dogfood

**Category:** General | **Path:** `hermes-agent\skills\dogfood/`

**Description:** Exploratory QA of web apps: find bugs, evidence, reports.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `dogfood` or related concepts

**Use Case 🤖:** Use for tasks involving dogfood (see description).

---

### domain-intel

**Category:** API | **Path:** `hermes-agent\optional-skills\research\domain-intel/`

**Description:** Passive domain reconnaissance using Python stdlib. Subdomain discovery, SSL certificate inspection, WHOIS lookups, DNS records, domain availability checks, and bulk multi-domain analysis. No API keys required.

**Trigger Words 🤖:** When user mentions `domain-intel` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### drug-discovery

**Category:** Accessibility | **Path:** `hermes-agent\optional-skills\research\drug-discovery/`

**Description:** Pharmaceutical research assistant for drug discovery workflows. Search bioactive compounds on ChEMBL, calculate drug-likeness (Lipinski Ro5, QED, TPSA, synthetic accessibility), look up drug-drug interactions via OpenFDA, interpret ADMET profiles, and assist with lead optimization. Use for medicinal chemistry questions, molecule property analysis, clinical pharmacology, and open-science drug research.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `drug-discovery` or related concepts

**Use Case 🤖:** Design and audit accessible digital products (WCAG)

---

### dspy

**Category:** General | **Path:** `hermes-agent\skills\mlops\research\dspy/`

**Description:** DSPy: declarative LM programs, auto-optimize prompts, RAG.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `dspy` or related concepts

**Use Case 🤖:** Use for tasks involving dspy (see description).

---

### duckduckgo-search

**Category:** Research | **Path:** `hermes-agent\optional-skills\research\duckduckgo-search/`

**Description:** Free web search via DuckDuckGo — text, news, images, videos. No API key needed. Prefer the `ddgs` CLI when installed; use the Python DDGS library only after verifying that `ddgs` is available in the current runtime.

**Version:** 1.3.0  
**Trigger Words 🤖:** When user mentions `duckduckgo-search` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### evaluating-llms-harness

**Category:** Quality | **Path:** `hermes-agent\skills\mlops\evaluation\lm-evaluation-harness/`

**Description:** lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `evaluating-llms-harness` or related concepts

**Use Case 🤖:** Evaluate and benchmark outputs

---

### evm

**Category:** General | **Path:** `hermes-agent\optional-skills\blockchain\evm/`

**Description:** Read-only EVM client: wallets, tokens, gas across 8 chains.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `evm` or related concepts

**Use Case 🤖:** Use for tasks involving evm (see description).

---

### excalidraw

**Category:** General | **Path:** `hermes-agent\skills\creative\excalidraw/`

**Description:** Hand-drawn Excalidraw JSON diagrams (arch, flow, seq).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `excalidraw` or related concepts

**Use Case 🤖:** Use for tasks involving excalidraw (see description).

---

### excel-author

**Category:** General | **Path:** `hermes-agent\optional-skills\finance\excel-author/`

**Description:** Build auditable Excel workbooks headless with openpyxl — blue/black/green cell conventions, formulas over hardcodes, named ranges, balance checks, sensitivity tables. Use for financial models, audit outputs, reconciliations.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `excel-author` or related concepts

**Use Case 🤖:** Use for tasks involving excel author (see description).

---

### faiss

**Category:** Research | **Path:** `hermes-agent\optional-skills\mlops\faiss/`

**Description:** Facebook's library for efficient similarity search and clustering of dense vectors. Supports billions of vectors, GPU acceleration, and various index types (Flat, IVF, HNSW). Use for fast k-NN search, large-scale vector retrieval, or when you need pure similarity search without metadata. Best for high-performance applications.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `faiss` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### fastmcp

**Category:** Database | **Path:** `hermes-agent\optional-skills\mcp\fastmcp/`

**Description:** Build, test, inspect, install, and deploy MCP servers with FastMCP in Python. Use when creating a new MCP server, wrapping an API or database as MCP tools, exposing resources or prompts, or preparing a FastMCP server for Claude Code, Cursor, or HTTP deployment.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `fastmcp` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### findmy

**Category:** General | **Path:** `hermes-agent\skills\apple\findmy/`

**Description:** Track Apple devices/AirTags via FindMy.app on macOS.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `findmy` or related concepts

**Use Case 🤖:** Use for tasks involving findmy (see description).

---

### fine-tuning-with-trl

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\training\trl-fine-tuning/`

**Description:** TRL: SFT, DPO, PPO, GRPO, reward modeling for LLM RLHF.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `fine-tuning-with-trl` or related concepts

**Use Case 🤖:** Use for tasks involving fine tuning with trl (see description).

---

### fitness-nutrition

**Category:** Research | **Path:** `hermes-agent\optional-skills\health\fitness-nutrition/`

**Description:** Gym workout planner and nutrition tracker. Search 690+ exercises by muscle, equipment, or category via wger. Look up macros and calories for 380,000+ foods via USDA FoodData Central. Compute BMI, TDEE, one-rep max, macro splits, and body fat — pure Python, no pip installs. Built for anyone chasing gains, cutting weight, or just trying to eat better.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `fitness-nutrition` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### gif-search

**Category:** Research | **Path:** `hermes-agent\skills\media\gif-search/`

**Description:** Search/download GIFs from Tenor via curl + jq.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `gif-search` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### github-auth

**Category:** General | **Path:** `hermes-agent\skills\github\github-auth/`

**Description:** GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `github-auth` or related concepts

**Use Case 🤖:** Use for tasks involving github auth (see description).

---

### github-code-review

**Category:** Quality | **Path:** `hermes-agent\skills\github\github-code-review/`

**Description:** Review PRs: diffs, inline comments via gh or REST.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `github-code-review` or related concepts

**Use Case 🤖:** Review code for quality and correctness

---

### github-issues

**Category:** General | **Path:** `hermes-agent\skills\github\github-issues/`

**Description:** Create, triage, label, assign GitHub issues via gh or REST.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `github-issues` or related concepts

**Use Case 🤖:** Use for tasks involving github issues (see description).

---

### github-pr-workflow

**Category:** Workflow | **Path:** `hermes-agent\skills\github\github-pr-workflow/`

**Description:** GitHub PR lifecycle: branch, commit, open, CI, merge.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `github-pr-workflow` or related concepts

**Use Case 🤖:** Manage multi-step workflows

---

### github-repo-management

**Category:** General | **Path:** `hermes-agent\skills\github\github-repo-management/`

**Description:** Clone/create/fork repos; manage remotes, releases.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `github-repo-management` or related concepts

**Use Case 🤖:** Use for tasks involving github repo management (see description).

---

### gitnexus-explorer

**Category:** General | **Path:** `hermes-agent\optional-skills\research\gitnexus-explorer/`

**Description:** Index a codebase with GitNexus and serve an interactive knowledge graph via web UI + Cloudflare tunnel.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `gitnexus-explorer` or related concepts

**Use Case 🤖:** Use for tasks involving gitnexus explorer (see description).

---

### godmode

**Category:** General | **Path:** `hermes-agent\skills\red-teaming\godmode/`

**Description:** Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `godmode` or related concepts

**Use Case 🤖:** Use for tasks involving godmode (see description).

---

### google-workspace

**Category:** General | **Path:** `hermes-agent\skills\productivity\google-workspace/`

**Description:** Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `google-workspace` or related concepts

**Use Case 🤖:** Use for tasks involving google workspace (see description).

---

### google_meet

**Category:** Agent | **Path:** `hermes-agent\plugins\google_meet/`

**Description:** Join a Google Meet call, transcribe live captions, optionally speak in realtime, and do the followup work afterwards. Use when the user asks the agent to sit in on a meeting, take notes, summarize, respond in-call, or action items from it.

**Version:** 0.2.0  
**Trigger Words 🤖:** When user mentions `google_meet` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### guidance

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\guidance/`

**Description:** Control LLM output with regex and grammars, guarantee valid JSON/XML/code generation, enforce structured formats, and build multi-step workflows with Guidance - Microsoft Research's constrained generation framework

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `guidance` or related concepts

**Use Case 🤖:** Use for tasks involving guidance (see description).

---

### heartmula

**Category:** General | **Path:** `hermes-agent\skills\media\heartmula/`

**Description:** HeartMuLa: Suno-like song generation from lyrics + tags.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `heartmula` or related concepts

**Use Case 🤖:** Use for tasks involving heartmula (see description).

---

### here.now

**Category:** Agent | **Path:** `hermes-agent\optional-skills\productivity\here-now/`

**Description:** Publish static sites to {slug}.here.now and store private files in cloud Drives for agent-to-agent handoff.

**Version:** 1.15.3  
**Trigger Words 🤖:** When user mentions `here.now` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### hermes-agent

**Category:** Agent | **Path:** `hermes-agent\skills\autonomous-ai-agents\hermes-agent/`

**Description:** Configure, extend, or contribute to Hermes Agent.

**Version:** 2.1.0  
**Trigger Words 🤖:** When user mentions `hermes-agent` or related concepts

**Use Case 🤖:** Digital twin agent with learning and memory capabilities

---

### hermes-agent-skill-authoring

**Category:** Agent | **Path:** `hermes-agent\skills\software-development\hermes-agent-skill-authoring/`

**Description:** Author in-repo SKILL.md: frontmatter, validator, structure.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `hermes-agent-skill-authoring` or related concepts

**Use Case 🤖:** Digital twin agent with learning and memory capabilities

---

### himalaya

**Category:** General | **Path:** `hermes-agent\skills\email\himalaya/`

**Description:** Himalaya CLI: IMAP/SMTP email from terminal.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `himalaya` or related concepts

**Use Case 🤖:** Use for tasks involving himalaya (see description).

---

### honcho

**Category:** Context | **Path:** `hermes-agent\optional-skills\autonomous-ai-agents\honcho/`

**Description:** Configure and use Honcho memory with Hermes -- cross-session user modeling, multi-profile peer isolation, observation config, dialectic reasoning, session summaries, and context budget enforcement. Use when setting up Honcho, troubleshooting memory, managing profiles with Honcho peers, or tuning observation, recall, and dialectic settings.

**Version:** 2.0.0  
**Trigger Words 🤖:** When user mentions `honcho` or related concepts

**Use Case 🤖:** Manage persistent memory and context

---

### huggingface-accelerate

**Category:** API | **Path:** `hermes-agent\optional-skills\mlops\accelerate/`

**Description:** Simplest distributed training API. 4 lines to add distributed support to any PyTorch script. Unified API for DeepSpeed/FSDP/Megatron/DDP. Automatic device placement, mixed precision (FP16/BF16/FP8). Interactive config, single launch command. HuggingFace ecosystem standard.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `huggingface-accelerate` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### huggingface-hub

**Category:** Research | **Path:** `hermes-agent\skills\mlops\huggingface-hub/`

**Description:** HuggingFace hf CLI: search/download/upload models, datasets.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `huggingface-hub` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### huggingface-tokenizers

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\huggingface-tokenizers/`

**Description:** Fast tokenizers optimized for research and production. Rust-based implementation tokenizes 1GB in <20 seconds. Supports BPE, WordPiece, and Unigram algorithms. Train custom vocabularies, track alignments, handle padding/truncation. Integrates seamlessly with transformers. Use when you need high-performance tokenization or custom tokenizer training.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `huggingface-tokenizers` or related concepts

**Use Case 🤖:** Use for tasks involving huggingface tokenizers (see description).

---

### humanizer

**Category:** General | **Path:** `hermes-agent\skills\creative\humanizer/`

**Description:** Humanize text: strip AI-isms and add real voice.

**Version:** 2.5.1  
**Trigger Words 🤖:** When user mentions `humanizer` or related concepts

**Use Case 🤖:** Use for tasks involving humanizer (see description).

---

### hyperframes

**Category:** General | **Path:** `hermes-agent\optional-skills\creative\hyperframes/`

**Description:** Create HTML-based video compositions, animated title cards, social overlays, captioned talking-head videos, audio-reactive visuals, and shader transitions using HyperFrames. HTML is the source of truth for video. Use when the user wants a rendered MP4/WebM from an HTML composition, wants to animate text/logos/charts over media, needs captions synced to audio, wants TTS narration, or wants to convert a website into a video.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `hyperframes` or related concepts

**Use Case 🤖:** Use for tasks involving hyperframes (see description).

---

### hyperliquid

**Category:** Workflow | **Path:** `hermes-agent\optional-skills\blockchain\hyperliquid/`

**Description:** Hyperliquid market data, account history, trade review.

**Version:** 0.1.0  
**Trigger Words 🤖:** When user mentions `hyperliquid` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### ideation

**Category:** General | **Path:** `hermes-agent\skills\creative\creative-ideation/`

**Description:** Generate project ideas via creative constraints.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `ideation` or related concepts

**Use Case 🤖:** Use for tasks involving ideation (see description).

---

### imessage

**Category:** General | **Path:** `hermes-agent\skills\apple\imessage/`

**Description:** Send and receive iMessages/SMS via the imsg CLI on macOS.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `imessage` or related concepts

**Use Case 🤖:** Use for tasks involving imessage (see description).

---

### inference-sh-cli

**Category:** Workflow | **Path:** `hermes-agent\optional-skills\devops\cli/`

**Description:** Run 150+ AI apps via inference.sh CLI (infsh) — image generation, video creation, LLMs, search, 3D, social automation. Uses the terminal tool. Triggers: inference.sh, infsh, ai apps, flux, veo, image generation, video generation, seedream, seedance, tavily

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `inference-sh-cli` or related concepts

**Use Case 🤖:** Launch and drive the project app to test changes

---

### instructor

**Category:** Data | **Path:** `hermes-agent\optional-skills\mlops\instructor/`

**Description:** Extract structured data from LLM responses with Pydantic validation, retry failed extractions automatically, parse complex JSON with type safety, and stream partial results with Instructor - battle-tested structured output library

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `instructor` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### jupyter-live-kernel

**Category:** General | **Path:** `hermes-agent\skills\data-science\jupyter-live-kernel/`

**Description:** Iterative Python via live Jupyter kernel (hamelnb).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `jupyter-live-kernel` or related concepts

**Use Case 🤖:** Use for tasks involving jupyter live kernel (see description).

---

### kanban-codex-lane

**Category:** Workflow | **Path:** `hermes-agent\skills\autonomous-ai-agents\kanban-codex-lane/`

**Description:** Use when a Hermes Kanban worker wants to run Codex CLI as an isolated implementation lane while Hermes keeps ownership of task lifecycle, reconciliation, testing, and handoff.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `kanban-codex-lane` or related concepts

**Use Case 🤖:** Launch and drive the project app to test changes

---

### kanban-orchestrator

**Category:** Meta | **Path:** `hermes-agent\skills\devops\kanban-orchestrator/`

**Description:** Decomposition playbook + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work yourself" rule and the basic lifecycle are auto-injected into every kanban worker's system prompt; this skill is the deeper playbook when you're specifically playing the orchestrator role.

**Version:** 3.0.0  
**Trigger Words 🤖:** When user mentions `kanban-orchestrator` or related concepts

**Use Case 🤖:** Create, manage, or discover skills

---

### kanban-video-orchestrator

**Category:** Workflow | **Path:** `hermes-agent\optional-skills\creative\kanban-video-orchestrator/`

**Description:** Plan, set up, and monitor a multi-agent video production pipeline backed by Hermes Kanban. Use when the user wants to make ANY video — narrative film, product/marketing, music video, explainer, ASCII/terminal art, abstract/generative loop, comic, 3D, real-time/installation — and the work warrants decomposition into specialized profiles (writer, designer, animator, renderer, voice, editor, etc.) coordinated through a kanban board. Performs adaptive discovery to scope the brief, designs an appropriate team for the requested style, generates the setup script that creates Hermes profiles + initial kanban task, then helps monitor execution and intervene when tasks stall or fail. Routes scenes to whichever Hermes rendering / audio / design skill fits each beat (`ascii-video`, `manim-video`, `p5js`, `comfyui`, `touchdesigner-mcp`, `blender-mcp`, `pixel-art`, `baoyu-comic`, `claude-design`, `excalidraw`, `songsee`, `heartmula`, …) plus external APIs for TTS, image-gen, and image-to-video as needed.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `kanban-video-orchestrator` or related concepts

**Use Case 🤖:** Run recurring tasks on a timer interval

---

### kanban-worker

**Category:** Agent | **Path:** `hermes-agent\skills\devops\kanban-worker/`

**Description:** Pitfalls, examples, and edge cases for Hermes Kanban workers. The lifecycle itself is auto-injected into every worker's system prompt as KANBAN_GUIDANCE (from agent/prompt_builder.py); this skill is what you load when you want deeper detail on specific scenarios.

**Version:** 2.0.0  
**Trigger Words 🤖:** When user mentions `kanban-worker` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### lambda-labs-gpu-cloud

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\lambda-labs/`

**Description:** Reserved and on-demand GPU cloud instances for ML training and inference. Use when you need dedicated GPU instances with simple SSH access, persistent filesystems, or high-performance multi-node clusters for large-scale training.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lambda-labs-gpu-cloud` or related concepts

**Use Case 🤖:** Use for tasks involving lambda labs gpu cloud (see description).

---

### lbo-model

**Category:** General | **Path:** `hermes-agent\optional-skills\finance\lbo-model/`

**Description:** Build leveraged buyout models in Excel — sources & uses, debt schedule, cash sweep, exit multiple, IRR/MOIC sensitivity. Pairs with excel-author. Use for PE screening, sponsor-case valuation, or illustrative LBO in a pitch.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lbo-model` or related concepts

**Use Case 🤖:** Use for tasks involving lbo model (see description).

---

### linear

**Category:** General | **Path:** `hermes-agent\skills\productivity\linear/`

**Description:** Linear: manage issues, projects, teams via GraphQL + curl.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `linear` or related concepts

**Use Case 🤖:** Use for tasks involving linear (see description).

---

### llama-cpp

**Category:** General | **Path:** `hermes-agent\skills\mlops\inference\llama-cpp/`

**Description:** llama.cpp local GGUF inference + HF Hub model discovery.

**Version:** 2.1.2  
**Trigger Words 🤖:** When user mentions `llama-cpp` or related concepts

**Use Case 🤖:** Use for tasks involving llama cpp (see description).

---

### llava

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\llava/`

**Description:** Large Language and Vision Assistant. Enables visual instruction tuning and image-based conversations. Combines CLIP vision encoder with Vicuna/LLaMA language models. Supports multi-turn image chat, visual question answering, and instruction following. Use for vision-language chatbots or image understanding tasks. Best for conversational image analysis.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `llava` or related concepts

**Use Case 🤖:** Use for tasks involving llava (see description).

---

### llm-wiki

**Category:** General | **Path:** `hermes-agent\skills\research\llm-wiki/`

**Description:** Karpathy's LLM Wiki: build/query interlinked markdown KB.

**Version:** 2.1.0  
**Trigger Words 🤖:** When user mentions `llm-wiki` or related concepts

**Use Case 🤖:** Use for tasks involving llm wiki (see description).

---

### macos-computer-use

**Category:** Meta | **Path:** `hermes-agent\skills\apple\macos-computer-use/`

**Description:** Drive the macOS desktop in the background — screenshots, mouse, keyboard, scroll, drag — without stealing the user's cursor, keyboard focus, or Space. Works with any tool-capable model. Load this skill whenever the `computer_use` tool is available.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `macos-computer-use` or related concepts

**Use Case 🤖:** Create, manage, or discover skills

---

### maps

**Category:** General | **Path:** `hermes-agent\skills\productivity\maps/`

**Description:** Geocode, POIs, routes, timezones via OpenStreetMap/OSRM.

**Version:** 1.2.0  
**Trigger Words 🤖:** When user mentions `maps` or related concepts

**Use Case 🤖:** Use for tasks involving maps (see description).

---

### mcporter

**Category:** Integration | **Path:** `hermes-agent\optional-skills\mcp\mcporter/`

**Description:** Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and CLI/type generation.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `mcporter` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### meme-generation

**Category:** General | **Path:** `hermes-agent\optional-skills\creative\meme-generation/`

**Description:** Generate real meme images by picking a template and overlaying text with Pillow. Produces actual .png meme files.

**Version:** 2.0.0  
**Trigger Words 🤖:** When user mentions `meme-generation` or related concepts

**Use Case 🤖:** Use for tasks involving meme generation (see description).

---

### memento-flashcards

**Category:** Workflow | **Path:** `hermes-agent\optional-skills\productivity\memento-flashcards/`

**Description:** Spaced-repetition flashcard system. Create cards from facts or text, chat with flashcards using free-text answers graded by the agent, generate quizzes from YouTube transcripts, review due cards with adaptive scheduling, and export/import decks as CSV.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `memento-flashcards` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### merger-model

**Category:** General | **Path:** `hermes-agent\optional-skills\finance\merger-model/`

**Description:** Build accretion/dilution (merger) models in Excel — pro-forma P&L, synergies, financing mix, EPS impact. Pairs with excel-author. Use for M&A pitches, board materials, or deal evaluation.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `merger-model` or related concepts

**Use Case 🤖:** Use for tasks involving merger model (see description).

---

### minecraft-modpack-server

**Category:** General | **Path:** `hermes-agent\skills\gaming\minecraft-modpack-server/`

**Description:** Host modded Minecraft servers (CurseForge, Modrinth).

**Trigger Words 🤖:** When user mentions `minecraft-modpack-server` or related concepts

**Use Case 🤖:** Use for tasks involving minecraft modpack server (see description).

---

### modal-serverless-gpu

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\modal/`

**Description:** Serverless GPU cloud platform for running ML workloads. Use when you need on-demand GPU access without infrastructure management, deploying ML models as APIs, or running batch jobs with automatic scaling.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `modal-serverless-gpu` or related concepts

**Use Case 🤖:** Use for tasks involving modal serverless gpu (see description).

---

### nano-pdf

**Category:** General | **Path:** `hermes-agent\skills\productivity\nano-pdf/`

**Description:** Edit PDF text/typos/titles via nano-pdf CLI (NL prompts).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `nano-pdf` or related concepts

**Use Case 🤖:** Use for tasks involving nano pdf (see description).

---

### native-mcp

**Category:** Integration | **Path:** `hermes-agent\skills\mcp\native-mcp/`

**Description:** MCP client: connect servers, register tools (stdio/HTTP).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `native-mcp` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### nemo-curator

**Category:** Data | **Path:** `hermes-agent\optional-skills\mlops\nemo-curator/`

**Description:** GPU-accelerated data curation for LLM training. Supports text/image/video/audio. Features fuzzy deduplication (16× faster), quality filtering (30+ heuristics), semantic deduplication, PII redaction, NSFW detection. Scales across GPUs with RAPIDS. Use for preparing high-quality training datasets, cleaning web data, or deduplicating large corpora.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `nemo-curator` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### neuroskill-bci

**Category:** General | **Path:** `hermes-agent\optional-skills\health\neuroskill-bci/`

**Description:** Connect to a running NeuroSkill instance and incorporate the user's real-time cognitive and emotional state (focus, relaxation, mood, cognitive load, drowsiness, heart rate, HRV, sleep staging, and 40+ derived EXG scores) into responses. Requires a BCI wearable (Muse 2/S or OpenBCI) and the NeuroSkill desktop app running locally.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `neuroskill-bci` or related concepts

**Use Case 🤖:** Use for tasks involving neuroskill bci (see description).

---

### node-inspect-debugger

**Category:** Debugging | **Path:** `hermes-agent\skills\software-development\node-inspect-debugger/`

**Description:** Debug Node.js via --inspect + Chrome DevTools Protocol CLI.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `node-inspect-debugger` or related concepts

**Use Case 🤖:** Systematically debug issues

---

### notion

**Category:** API | **Path:** `hermes-agent\skills\productivity\notion/`

**Description:** Notion API + ntn CLI: pages, databases, markdown, Workers.

**Version:** 2.0.0  
**Trigger Words 🤖:** When user mentions `notion` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### obliteratus

**Category:** General | **Path:** `hermes-agent\skills\mlops\inference\obliteratus/`

**Description:** OBLITERATUS: abliterate LLM refusals (diff-in-means).

**Version:** 2.0.0  
**Trigger Words 🤖:** When user mentions `obliteratus` or related concepts

**Use Case 🤖:** Use for tasks involving obliteratus (see description).

---

### obsidian

**Category:** Research | **Path:** `hermes-agent\skills\note-taking\obsidian/`

**Description:** Read, search, create, and edit notes in the Obsidian vault.

**Trigger Words 🤖:** When user mentions `obsidian` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### ocr-and-documents

**Category:** General | **Path:** `hermes-agent\skills\productivity\ocr-and-documents/`

**Description:** Extract text from PDFs/scans (pymupdf, marker-pdf).

**Version:** 2.3.0  
**Trigger Words 🤖:** When user mentions `ocr-and-documents` or related concepts

**Use Case 🤖:** Use for tasks involving ocr and documents (see description).

---

### one-three-one-rule

**Category:** Planning | **Path:** `hermes-agent\optional-skills\communication\one-three-one-rule/`

**Description:** Structured decision-making framework for technical proposals and trade-off analysis. When the user faces a choice between multiple approaches (architecture decisions, tool selection, refactoring strategies, migration paths), this skill produces a 1-3-1 format: one clear problem statement, three distinct options with pros/cons, and one concrete recommendation with definition of done and implementation plan. Use when the user asks for a "1-3-1", says "give me options", or needs help choosing between competing approaches.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `one-three-one-rule` or related concepts

**Use Case 🤖:** Create implementation plans

---

### openclaw-migration

**Category:** Agent | **Path:** `hermes-agent\optional-skills\migration\openclaw-migration/`

**Description:** Migrate a user's OpenClaw customization footprint into Hermes Agent. Imports Hermes-compatible memories, SOUL.md, command allowlists, user skills, and selected workspace assets from ~/.openclaw, then reports exactly what could not be migrated and why.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `openclaw-migration` or related concepts

**Use Case 🤖:** Digital twin agent with learning and memory capabilities

---

### opencode

**Category:** Workflow | **Path:** `hermes-agent\skills\autonomous-ai-agents\opencode/`

**Description:** Delegate coding to OpenCode CLI (features, PR review).

**Version:** 1.2.0  
**Trigger Words 🤖:** When user mentions `opencode` or related concepts

**Use Case 🤖:** Review code changes for quality and correctness

---

### openhue

**Category:** General | **Path:** `hermes-agent\skills\smart-home\openhue/`

**Description:** Control Philips Hue lights, scenes, rooms via OpenHue CLI.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `openhue` or related concepts

**Use Case 🤖:** Use for tasks involving openhue (see description).

---

### optimizing-attention-flash

**Category:** Context | **Path:** `hermes-agent\optional-skills\mlops\flash-attention/`

**Description:** Optimizes transformer attention with Flash Attention for 2-4x speedup and 10-20x memory reduction. Use when training/running transformers with long sequences (>512 tokens), encountering GPU memory issues with attention, or need faster inference. Supports PyTorch native SDPA, flash-attn library, H100 FP8, and sliding window attention.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `optimizing-attention-flash` or related concepts

**Use Case 🤖:** Manage persistent memory and context

---

### osint-investigation

**Category:** General | **Path:** `hermes-agent\optional-skills\research\osint-investigation/`

**Description:** Public-records OSINT investigation framework — SEC EDGAR filings, USAspending contracts, Senate lobbying, OFAC sanctions, ICIJ offshore leaks, NYC property records (ACRIS), OpenCorporates registries, CourtListener court records, Wayback Machine archives, Wikipedia + Wikidata, GDELT news monitoring. Entity resolution across sources, cross-link analysis, timing correlation, evidence chains. Python stdlib only.

**Version:** 0.1.0  
**Trigger Words 🤖:** When user mentions `osint-investigation` or related concepts

**Use Case 🤖:** Use for tasks involving osint investigation (see description).

---

### oss-forensics

**Category:** General | **Path:** `hermes-agent\optional-skills\security\oss-forensics/`

**Description:** Supply chain investigation, evidence recovery, and forensic analysis for GitHub repositories. Covers deleted commit recovery, force-push detection, IOC extraction, multi-source evidence collection, hypothesis formation/validation, and structured forensic reporting. Inspired by RAPTOR's 1800+ line OSS Forensics system.

**Trigger Words 🤖:** When user mentions `oss-forensics` or related concepts

**Use Case 🤖:** Use for tasks involving oss forensics (see description).

---

### outlines

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\inference\outlines/`

**Description:** Outlines: structured JSON/regex/Pydantic LLM generation.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `outlines` or related concepts

**Use Case 🤖:** Use for tasks involving outlines (see description).

---

### p5js

**Category:** Creative | **Path:** `hermes-agent\skills\creative\p5js/`

**Description:** p5.js sketches: gen art, shaders, interactive, 3D.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `p5js` or related concepts

**Use Case 🤖:** Algorithmic art generation

---

### page-agent

**Category:** Agent | **Path:** `hermes-agent\optional-skills\web-development\page-agent/`

**Description:** Embed alibaba/page-agent into your own web application — a pure-JavaScript in-page GUI agent that ships as a single <script> tag or npm package and lets end-users of your site drive the UI with natural language ("click login, fill username as John"). No Python, no headless browser, no extension required. Use this skill when the user is a web developer who wants to add an AI copilot to their SaaS / admin panel / B2B tool, make a legacy web app accessible via natural language, or evaluate page-agent against a local (Ollama) or cloud (Qwen / OpenAI / OpenRouter) LLM. NOT for server-side browser automation — point those users to Hermes' built-in browser tool instead.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `page-agent` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### parallel-cli

**Category:** Research | **Path:** `hermes-agent\optional-skills\research\parallel-cli/`

**Description:** Optional vendor skill for Parallel CLI — agent-native web search, extraction, deep research, enrichment, FindAll, and monitoring. Prefer JSON output and non-interactive flows.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `parallel-cli` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### peft-fine-tuning

**Category:** Context | **Path:** `hermes-agent\optional-skills\mlops\peft/`

**Description:** Parameter-efficient fine-tuning for LLMs using LoRA, QLoRA, and 25+ methods. Use when fine-tuning large models (7B-70B) with limited GPU memory, when you need to train <1% of parameters with minimal accuracy loss, or for multi-adapter serving. HuggingFace's official library integrated with transformers ecosystem.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `peft-fine-tuning` or related concepts

**Use Case 🤖:** Manage persistent memory and context

---

### pinecone

**Category:** Database | **Path:** `hermes-agent\optional-skills\mlops\pinecone/`

**Description:** Managed vector database for production AI applications. Fully managed, auto-scaling, with hybrid search (dense + sparse), metadata filtering, and namespaces. Low latency (<100ms p95). Use for production RAG, recommendation systems, or semantic search at scale. Best for serverless, managed infrastructure.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `pinecone` or related concepts

**Use Case 🤖:** Database design, migration, and optimization

---

### pinggy-tunnel

**Category:** General | **Path:** `hermes-agent\optional-skills\devops\pinggy-tunnel/`

**Description:** Zero-install localhost tunnels over SSH via Pinggy.

**Version:** 0.1.0  
**Trigger Words 🤖:** When user mentions `pinggy-tunnel` or related concepts

**Use Case 🤖:** Use for tasks involving pinggy tunnel (see description).

---

### pixel-art

**Category:** Creative | **Path:** `hermes-agent\skills\creative\pixel-art/`

**Description:** Pixel art w/ era palettes (NES, Game Boy, PICO-8).

**Version:** 2.0.0  
**Trigger Words 🤖:** When user mentions `pixel-art` or related concepts

**Use Case 🤖:** Algorithmic art generation

---

### plan

**Category:** Planning | **Path:** `hermes-agent\skills\software-development\plan/`

**Description:** Plan mode: write markdown plan to .hermes/plans/, no exec.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `plan` or related concepts

**Use Case 🤖:** Create implementation plans

---

### pokemon-player

**Category:** General | **Path:** `hermes-agent\skills\gaming\pokemon-player/`

**Description:** Play Pokemon via headless emulator + RAM reads.

**Trigger Words 🤖:** When user mentions `pokemon-player` or related concepts

**Use Case 🤖:** Use for tasks involving pokemon player (see description).

---

### polymarket

**Category:** General | **Path:** `hermes-agent\skills\research\polymarket/`

**Description:** Query Polymarket: markets, prices, orderbooks, history.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `polymarket` or related concepts

**Use Case 🤖:** Use for tasks involving polymarket (see description).

---

### popular-web-designs

**Category:** General | **Path:** `hermes-agent\skills\creative\popular-web-designs/`

**Description:** 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `popular-web-designs` or related concepts

**Use Case 🤖:** Use for tasks involving popular web designs (see description).

---

### powerpoint

**Category:** Documents | **Path:** `hermes-agent\skills\productivity\powerpoint/`

**Description:** Create, read, edit .pptx decks, slides, notes, templates.

**Trigger Words 🤖:** When user mentions `powerpoint` or related concepts

**Use Case 🤖:** PowerPoint creation and editing

---

### pptx-author

**Category:** Documents | **Path:** `hermes-agent\optional-skills\finance\pptx-author/`

**Description:** Build PowerPoint decks headless with python-pptx. Pairs with excel-author for model-backed decks where every number traces to a workbook cell. Use for pitch decks, IC memos, earnings notes.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `pptx-author` or related concepts

**Use Case 🤖:** PowerPoint creation and editing

---

### pretext

**Category:** Browser | **Path:** `hermes-agent\skills\creative\pretext/`

**Description:** Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art. Produces single-file HTML demos by default.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `pretext` or related concepts

**Use Case 🤖:** Browser automation and testing

---

### python-debugpy

**Category:** Debugging | **Path:** `hermes-agent\skills\software-development\python-debugpy/`

**Description:** Debug Python: pdb REPL + debugpy remote (DAP).

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `python-debugpy` or related concepts

**Use Case 🤖:** Systematically debug issues

---

### pytorch-fsdp

**Category:** Data | **Path:** `hermes-agent\optional-skills\mlops\pytorch-fsdp/`

**Description:** Expert guidance for Fully Sharded Data Parallel training with PyTorch FSDP - parameter sharding, mixed precision, CPU offloading, FSDP2

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `pytorch-fsdp` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### pytorch-lightning

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\pytorch-lightning/`

**Description:** High-level PyTorch framework with Trainer class, automatic distributed training (DDP/FSDP/DeepSpeed), callbacks system, and minimal boilerplate. Scales from laptop to supercomputer with same code. Use when you want clean training loops with built-in best practices.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `pytorch-lightning` or related concepts

**Use Case 🤖:** Use for tasks involving pytorch lightning (see description).

---

### qdrant-vector-search

**Category:** Research | **Path:** `hermes-agent\optional-skills\mlops\qdrant/`

**Description:** High-performance vector similarity search engine for RAG and semantic search. Use when building production RAG systems requiring fast nearest neighbor search, hybrid search with filtering, or scalable vector storage with Rust-powered performance.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `qdrant-vector-search` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### qmd

**Category:** Integration | **Path:** `hermes-agent\optional-skills\research\qmd/`

**Description:** Search personal knowledge bases, notes, docs, and meeting transcripts locally using qmd — a hybrid retrieval engine with BM25, vector search, and LLM reranking. Supports CLI and MCP integration.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `qmd` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### rest-graphql-debug

**Category:** Debugging | **Path:** `hermes-agent\optional-skills\software-development\rest-graphql-debug/`

**Description:** Debug REST/GraphQL APIs: status codes, auth, schemas, repro.

**Version:** 1.2.0  
**Trigger Words 🤖:** When user mentions `rest-graphql-debug` or related concepts

**Use Case 🤖:** Systematically debug issues

---

### scrapling

**Category:** Browser | **Path:** `hermes-agent\optional-skills\research\scrapling/`

**Description:** Web scraping with Scrapling - HTTP fetching, stealth browser automation, Cloudflare bypass, and spider crawling via CLI and Python.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `scrapling` or related concepts

**Use Case 🤖:** Browser automation and testing

---

### searxng-search

**Category:** Research | **Path:** `hermes-agent\optional-skills\research\searxng-search/`

**Description:** Free meta-search via SearXNG — aggregates results from 70+ search engines. Self-hosted or use a public instance. No API key needed. Falls back automatically when the web search toolset is unavailable.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `searxng-search` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### segment-anything-model

**Category:** General | **Path:** `hermes-agent\skills\mlops\models\segment-anything/`

**Description:** SAM: zero-shot image segmentation via points, boxes, masks.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `segment-anything-model` or related concepts

**Use Case 🤖:** Use for tasks involving segment anything model (see description).

---

### serving-llms-vllm

**Category:** API | **Path:** `hermes-agent\skills\mlops\inference\vllm/`

**Description:** vLLM: high-throughput LLM serving, OpenAI API, quantization.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `serving-llms-vllm` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### sherlock

**Category:** Research | **Path:** `hermes-agent\optional-skills\security\sherlock/`

**Description:** OSINT username search across 400+ social networks. Hunt down social media accounts by username.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `sherlock` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### shop-app

**Category:** Research | **Path:** `hermes-agent\optional-skills\productivity\shop-app/`

**Description:** Shop.app: product search, order tracking, returns, reorder.

**Version:** 0.0.28  
**Trigger Words 🤖:** When user mentions `shop-app` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### shopify

**Category:** General | **Path:** `hermes-agent\optional-skills\productivity\shopify/`

**Description:** Shopify Admin & Storefront GraphQL APIs via curl. Products, orders, customers, inventory, metafields.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `shopify` or related concepts

**Use Case 🤖:** Use for tasks involving shopify (see description).

---

### simpo-training

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\simpo/`

**Description:** Simple Preference Optimization for LLM alignment. Reference-free alternative to DPO with better performance (+6.4 points on AlpacaEval 2.0). No reference model needed, more efficient than DPO. Use for preference alignment when want simpler, faster training than DPO/PPO.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `simpo-training` or related concepts

**Use Case 🤖:** Use for tasks involving simpo training (see description).

---

### siyuan

**Category:** API | **Path:** `hermes-agent\optional-skills\productivity\siyuan/`

**Description:** SiYuan Note API for searching, reading, creating, and managing blocks and documents in a self-hosted knowledge base via curl.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `siyuan` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### sketch

**Category:** General | **Path:** `hermes-agent\skills\creative\sketch/`

**Description:** Throwaway HTML mockups: 2-3 design variants to compare.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `sketch` or related concepts

**Use Case 🤖:** Use for tasks involving sketch (see description).

---

### slime-rl-training

**Category:** Data | **Path:** `hermes-agent\optional-skills\mlops\slime/`

**Description:** Provides guidance for LLM post-training with RL using slime, a Megatron+SGLang framework. Use when training GLM models, implementing custom data generation workflows, or needing tight Megatron-LM integration for RL scaling.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `slime-rl-training` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### solana

**Category:** API | **Path:** `hermes-agent\optional-skills\blockchain\solana/`

**Description:** Query Solana blockchain data with USD pricing — wallet balances, token portfolios with values, transaction details, NFTs, whale detection, and live network stats. Uses Solana RPC + CoinGecko. No API key required.

**Version:** 0.2.0  
**Trigger Words 🤖:** When user mentions `solana` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### songsee

**Category:** General | **Path:** `hermes-agent\skills\media\songsee/`

**Description:** Audio spectrograms/features (mel, chroma, MFCC) via CLI.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `songsee` or related concepts

**Use Case 🤖:** Use for tasks involving songsee (see description).

---

### songwriting-and-ai-music

**Category:** General | **Path:** `hermes-agent\skills\creative\songwriting-and-ai-music/`

**Description:** Songwriting craft and Suno AI music prompts.

**Trigger Words 🤖:** When user mentions `songwriting-and-ai-music` or related concepts

**Use Case 🤖:** Use for tasks involving songwriting and ai music (see description).

---

### sparse-autoencoder-training

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\saelens/`

**Description:** Provides guidance for training and analyzing Sparse Autoencoders (SAEs) using SAELens to decompose neural network activations into interpretable features. Use when discovering interpretable features, analyzing superposition, or studying monosemantic representations in language models.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `sparse-autoencoder-training` or related concepts

**Use Case 🤖:** Use for tasks involving sparse autoencoder training (see description).

---

### spike

**Category:** General | **Path:** `hermes-agent\skills\software-development\spike/`

**Description:** Throwaway experiments to validate an idea before build.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `spike` or related concepts

**Use Case 🤖:** Use for tasks involving spike (see description).

---

### spotify

**Category:** Research | **Path:** `hermes-agent\skills\media\spotify/`

**Description:** Spotify: play, search, queue, manage playlists and devices.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `spotify` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### stable-diffusion-image-generation

**Category:** Creative | **Path:** `hermes-agent\optional-skills\mlops\stable-diffusion/`

**Description:** State-of-the-art text-to-image generation with Stable Diffusion models via HuggingFace Diffusers. Use when generating images from text prompts, performing image-to-image translation, inpainting, or building custom diffusion pipelines.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `stable-diffusion-image-generation` or related concepts

**Use Case 🤖:** Algorithmic art generation

---

### stocks

**Category:** Research | **Path:** `hermes-agent\optional-skills\finance\stocks/`

**Description:** Stock quotes, history, search, compare, crypto via Yahoo.

**Version:** 0.1.0  
**Trigger Words 🤖:** When user mentions `stocks` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### teams-meeting-pipeline

**Category:** Orchestration | **Path:** `hermes-agent\skills\productivity\teams-meeting-pipeline/`

**Description:** Operate the Teams meeting summary pipeline via Hermes CLI — summarize meetings, inspect pipeline status, replay jobs, manage Microsoft Graph subscriptions.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `teams-meeting-pipeline` or related concepts

**Use Case 🤖:** Master orchestrator for multi-stage workflows

---

### telephony

**Category:** General | **Path:** `hermes-agent\optional-skills\productivity\telephony/`

**Description:** Give Hermes phone capabilities without core tool changes. Provision and persist a Twilio number, send and receive SMS/MMS, make direct calls, and place AI-driven outbound calls through Bland.ai or Vapi.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `telephony` or related concepts

**Use Case 🤖:** Use for tasks involving telephony (see description).

---

### tensorrt-llm

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\tensorrt-llm/`

**Description:** Optimizes LLM inference with NVIDIA TensorRT for maximum throughput and lowest latency. Use for production deployment on NVIDIA GPUs (A100/H100), when you need 10-100x faster inference than PyTorch, or for serving models with quantization (FP8/INT4), in-flight batching, and multi-GPU scaling.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `tensorrt-llm` or related concepts

**Use Case 🤖:** Use for tasks involving tensorrt llm (see description).

---

### touchdesigner-mcp

**Category:** Integration | **Path:** `hermes-agent\skills\creative\touchdesigner-mcp/`

**Description:** Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 native tools.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `touchdesigner-mcp` or related concepts

**Use Case 🤖:** Manage MCP server connections

---

### unsloth

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\training\unsloth/`

**Description:** Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `unsloth` or related concepts

**Use Case 🤖:** Use for tasks involving unsloth (see description).

---

### watchers

**Category:** General | **Path:** `hermes-agent\optional-skills\devops\watchers/`

**Description:** Poll RSS, JSON APIs, and GitHub with watermark dedup.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `watchers` or related concepts

**Use Case 🤖:** Use for tasks involving watchers (see description).

---

### webhook-subscriptions

**Category:** Agent | **Path:** `hermes-agent\skills\devops\webhook-subscriptions/`

**Description:** Webhook subscriptions: event-driven agent runs.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `webhook-subscriptions` or related concepts

**Use Case 🤖:** Configure and manage AI agents

---

### weights-and-biases

**Category:** General | **Path:** `hermes-agent\skills\mlops\evaluation\weights-and-biases/`

**Description:** W&B: log ML experiments, sweeps, model registry, dashboards.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `weights-and-biases` or related concepts

**Use Case 🤖:** Use for tasks involving weights and biases (see description).

---

### whisper

**Category:** General | **Path:** `hermes-agent\optional-skills\mlops\whisper/`

**Description:** OpenAI's general-purpose speech recognition model. Supports 99 languages, transcription, translation to English, and language identification. Six model sizes from tiny (39M params) to large (1550M params). Use for speech-to-text, podcast transcription, or multilingual audio processing. Best for robust, multilingual ASR.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `whisper` or related concepts

**Use Case 🤖:** Use for tasks involving whisper (see description).

---

### xurl

**Category:** API | **Path:** `hermes-agent\skills\social-media\xurl/`

**Description:** X/Twitter via xurl CLI: post, search, DM, media, v2 API.

**Version:** 1.1.1  
**Trigger Words 🤖:** When user mentions `xurl` or related concepts

**Use Case 🤖:** Design and implement APIs

---

### youtube-content

**Category:** Content | **Path:** `hermes-agent\skills\media\youtube-content/`

**Description:** YouTube transcripts to summaries, threads, blogs.

**Trigger Words 🤖:** When user mentions `youtube-content` or related concepts

**Use Case 🤖:** Content generation and management

---

### yuanbao

**Category:** General | **Path:** `hermes-agent\skills\yuanbao/`

**Description:** Yuanbao (元宝) groups: @mention users, query info/members.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `yuanbao` or related concepts

**Use Case 🤖:** Use for tasks involving yuanbao (see description).


## Lark (飞书) Integration {{lark--integration}}

### lark-approval

**Category:** Feishu | **Path:** `lark-approval/`

**Description:** 飞书审批 API：审批实例、审批任务管理。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-approval` or related concepts

**Use Case 🤖:** Manage Feishu approval instances and tasks (飞书审批)

---

### lark-attendance

**Category:** Feishu | **Path:** `lark-attendance/`

**Description:** 飞书考勤打卡：查询自己的考勤打卡记录

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-attendance` or related concepts

**Use Case 🤖:** Query Feishu attendance and clock-in records (飞书考勤)

---

### lark-base

**Category:** Feishu | **Path:** `lark-base/`

**Description:** 当需要用 lark-cli 操作飞书多维表格（Base）时调用：搜索 Base、建表、字段管理、记录读写、记录分享链接、视图配置、历史查询，以及角色/表单/仪表盘管理/工作流；也适用于把旧的 +table / +field / +record 写法改成当前命令写法。涉及字段设计、公式字段、查找引用、跨表计算、行级派生指标、数据分析需求时也必须使用本 skill。

**Version:** 1.2.0  
**Trigger Words 🤖:** When user mentions `lark-base` or related concepts

**Use Case 🤖:** Manage Feishu Base: tables, fields, records, views (飞书多维表格)

---

### lark-calendar

**Category:** Feishu | **Path:** `lark-calendar/`

**Description:** 飞书日历（calendar）：提供日历与日程（会议）的全面管理能力。核心场景包括：查看/搜索日程、创建/更新日程、管理参会人、查询忙闲状态及推荐空闲时段、查询/搜索与预定会议室。注意：涉及【预约日程/会议】或【查询/预定会议室】时，必须先读取 references/lark-calendar-schedule-meeting.md 工作流！高频操作请优先使用 Shortcuts：+agenda（快速概览今日/近期行程）、+create（创建日程并按需邀请参会人及预定会议室）、+update（更新既有日程字段，或独立增删参会人/会议室）、+freebusy（查询用户主日历的忙闲信息和rsvp的状态）、+rsvp（回复日程邀请）

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-calendar` or related concepts

**Use Case 🤖:** Manage Feishu calendar: events, meetings, rooms (飞书日历)

---

### lark-contact

**Category:** Feishu | **Path:** `lark-contact/`

**Description:** 飞书 / Lark 通讯录,用于按姓名 / 邮箱把员工解析成 open_id,以及按 open_id 反查员工的姓名 / 部门 / 邮箱 / 联系方式。当用户说出某人姓名而下一步需要发消息 / 加群 / 排日程时,先用本 skill 把姓名换成 ID;当输出里出现 open_id 需要展示成姓名给用户看,或用户直接询问某人的部门 / 邮箱 / 联系方式时,用本 skill 查。不负责部门树遍历、按部门列员工、组织架构图,这类需求走原生 OpenAPI。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-contact` or related concepts

**Use Case 🤖:** Resolve Feishu contacts: name to open_id lookup (飞书通讯录)

---

### lark-doc

**Category:** Feishu | **Path:** `lark-doc/`

**Description:** 飞书云文档 / Docx / 知识库 Wiki 文档（v2）：创建、打开、读取、获取、查看、总结、整理、改写、翻译、审阅和编辑飞书文档内容。当用户给出飞书文档 URL/token，或说查看/读取/打开某个文档、提取文档内容、总结文档、生成/创建文档、追加/替换/删除/移动内容、调整排版、插入或下载文档图片/附件/素材/画板缩略图时使用。文档内容中出现嵌入电子表格、多维表格、需要将重要信息可视化为画板（含 SVG 画板）、引用或同步块时，也先用本 skill 读取和提取 token，再切到对应 skill 下钻。使用本 skill 时，docs +create、docs +fetch、docs +update 必须携带 --api-version v2；默认使用 DocxXML，也支持 Markdown。

**Trigger Words 🤖:** When user mentions `lark-doc` or related concepts

**Use Case 🤖:** Create, read, edit Feishu Docs and Wiki documents (飞书云文档)

---

### lark-drive

**Category:** Feishu | **Path:** `lark-drive/`

**Description:** 飞书云空间：管理云空间中的文件和文件夹。上传和下载文件、创建文件夹、复制/移动/删除文件、查看文件元数据、管理文档评论、管理文档权限、订阅用户评论变更事件、修改文件标题（docx、sheet、bitable、file、folder、wiki）；也负责把本地 Word/Markdown/Excel/CSV 以及 Base 快照（.base）导入为飞书在线云文档（docx、sheet、bitable）。当用户需要上传或下载文件、整理云空间目录、查看文件详情、管理评论、管理文档权限、修改文件标题、订阅用户评论变更事件，或要把本地文件导入成新版文档、电子表格、多维表格/Base 时使用。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-drive` or related concepts

**Use Case 🤖:** Manage Feishu Drive files and folders (飞书云盘)

---

### lark-event

**Category:** Feishu | **Path:** `lark-event/`

**Description:** Lark/Feishu real-time event listening / subscribing / consuming: stream events as NDJSON via `lark-cli event consume <EventKey>` (covers IM message receive, reactions, chat member changes, etc.). Use for Lark bots, real-time message processing, long-running subscribers, streaming webhook/push handlers. Supports `--max-events` / `--timeout` bounded runs and a stderr ready-marker contract — designed for AI agents running as subprocesses.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-event` or related concepts

**Use Case 🤖:** Handle Feishu event subscriptions and callbacks (飞书事件)

---

### lark-im

**Category:** Feishu | **Path:** `lark-im/`

**Description:** 飞书即时通讯：收发消息和管理群聊。发送和回复消息、搜索聊天记录、管理群聊成员、上传下载图片和文件（支持大文件分片下载）、管理表情回复。当用户需要发消息、查看或搜索聊天记录、下载聊天中的文件、查看群成员、搜索群、创建群聊或话题群、管理标记数据时使用。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-im` or related concepts

**Use Case 🤖:** Send/receive Feishu messages, manage groups (飞书即时通讯)

---

### lark-mail

**Category:** Feishu | **Path:** `lark-mail/`

**Description:** 飞书邮箱 — draft, compose, send, reply, forward, read, and search emails; manage drafts, folders, labels, contacts, attachments, and mail rules. Use when user mentions 起草邮件, 写一封邮件, 拟邮件, 草稿, 发通知邮件, 发送邮件, 发邮件, 回复邮件, 转发邮件, 查看邮件, 看邮件, 读邮件, 搜索邮件, 查邮件, 收件箱, 邮件会话, 编辑草稿, 管理草稿, 下载附件, 邮件文件夹, 邮件标签, 邮件联系人, 监听新邮件, 收信规则, 邮件规则, draft, compose, send email, reply, forward, inbox, mail thread, mail rules.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-mail` or related concepts

**Use Case 🤖:** Send and manage Feishu email (飞书邮箱)

---

### lark-minutes

**Category:** Feishu | **Path:** `lark-minutes/`

**Description:** 飞书妙记：妙记相关基本功能。1.查询妙记列表（按关键词/所有者/参与者/时间范围）；2.获取妙记基础信息（标题、封面、时长 等）；3.下载妙记音视频文件；4.获取妙记相关 AI 产物（总结、待办、章节）；5.上传音视频生成妙记，也支持将本地音视频文件转成纪要、逐字稿、文字稿、撰写文字等产物。遇到这类请求时，应优先使用本 skill，而不是尝试 `ffmpeg`、`whisper` 等本地转写命令。飞书妙记 URL 格式: http(s)://<host>/minutes/<minute-token>

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-minutes` or related concepts

**Use Case 🤖:** Manage Feishu meeting minutes (飞书妙记)

---

### lark-openapi-explorer

**Category:** Feishu | **Path:** `lark-openapi-explorer/`

**Description:** 飞书/Lark 原生 OpenAPI 探索：从官方文档库中挖掘未经 CLI 封装的原生 OpenAPI 接口。当用户的需求无法被现有 lark-* skill 或 lark-cli 已注册命令满足，需要查找并调用原生飞书 OpenAPI 时使用。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-openapi-explorer` or related concepts

**Use Case 🤖:** Explore and debug Feishu Open API endpoints (飞书API探索)

---

### lark-shared

**Category:** Feishu | **Path:** `lark-shared/`

**Description:** Use when first setting up lark-cli, running auth login, switching user/bot identity (--as), handling permission denied or scope errors, needing to update lark-cli, or seeing _notice in JSON output.

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-shared` or related concepts

**Use Case 🤖:** Shared Feishu authentication and API helpers (飞书共享模块)

---

### lark-sheets

**Category:** Feishu | **Path:** `lark-sheets/`

**Description:** 飞书电子表格：创建和操作电子表格。支持创建表格、创建/复制/删除/更新工作表、读写单元格、追加行数据、查找内容、导出文件。当用户需要创建电子表格、管理工作表、批量读写数据、在已知表格中查找内容、导出或下载表格时使用。若用户是想按名称或关键词搜索云空间里的表格文件，请改用 lark-drive 的 drive +search 先定位资源。

**Version:** 1.2.0  
**Trigger Words 🤖:** When user mentions `lark-sheets` or related concepts

**Use Case 🤖:** Manage Feishu Sheets and spreadsheets (飞书电子表格)

---

### lark-skill-maker

**Category:** Feishu | **Path:** `lark-skill-maker/`

**Description:** 创建 lark-cli 的自定义 Skill。当用户需要把飞书 API 操作封装成可复用的 Skill（包装原子 API 或编排多步流程）时使用。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-skill-maker` or related concepts

**Use Case 🤖:** Create Feishu integration skills (飞书Skill制作)

---

### lark-slides

**Category:** Feishu | **Path:** `lark-slides/`

**Description:** 飞书幻灯片：创建和编辑幻灯片，接口通过 XML 协议通信。创建演示文稿、读取幻灯片内容、管理幻灯片页面（创建、删除、读取、局部替换）。当用户需要创建或编辑幻灯片、读取或修改单个页面时使用。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-slides` or related concepts

**Use Case 🤖:** Create and edit Feishu presentation slides (飞书演示)

---

### lark-task

**Category:** Feishu | **Path:** `lark-task/`

**Description:** 飞书任务：管理任务、清单和任务智能体。创建待办任务、查看和更新任务状态、拆分子任务、组织任务清单、分配协作成员、上传任务附件、注册或注销任务智能体、更新任务智能体的主页数据、写入智能体任务记录。当用户需要创建待办事项、查看任务列表、跟踪任务进度、管理项目清单或给他人分配任务、为任务上传附件文件、注册注销任务智能体、更新智能体主页数据、写入任务记录时使用。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-task` or related concepts

**Use Case 🤖:** Manage Feishu tasks and to-do lists (飞书任务)

---

### lark-vc

**Category:** Feishu | **Path:** `lark-vc/`

**Description:** 飞书视频会议：搜索历史会议、查询会议纪要产物（总结、待办、章节、逐字稿）、查询会议参会人快照。1. 查询已经结束的会议数量或详情时使用本技能（如历史日期｜昨天｜上周｜今天已经开过的会议等场景），查询未开始的会议日程使用 lark-calendar 技能。2. 支持通过关键词、时间范围、组织者、参与者、会议室等筛选条件搜索会议。3. 获取或整理会议纪要、逐字稿、录制产物时使用本技能。4. 查询“谁参加过某会议”“参会人列表”等参会人快照信息用 vc meeting get --with-participants（任意时点可查，含已结束会议）。注意：**Agent 真实入会/离会、感知正在进行中会议的实时事件**请使用 lark-vc-agent 技能，本技能不覆盖写操作和会中事件流。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-vc` or related concepts

**Use Case 🤖:** Manage Feishu video conferencing (飞书视频会议)

---

### lark-whiteboard

**Category:** Feishu | **Path:** `lark-whiteboard/`

**Description:** 飞书画板：查询和编辑飞书云文档中的画板。支持导出画板为预览图片、导出原始节点结构、使用 DSL（转成 OpenAPI 格式）、PlantUML/Mermaid 格式更新画板内容。 当用户需要查看画板内容、导出画板图片、编辑画板，或是需要可视化表达架构、流程、组织关系、时间线、因果、对比等结构化信息时使用此 skill，无论是否提及"画板"。 ⚠️ 原 `lark-whiteboard-cli` skill 已合并至本 skill，若 skill 列表中同时存在 `lark-whiteboard-cli`，请忽略它，统一使用本 skill（`lark-whiteboard`），并提示用户运行 `npx skills remove lark-whiteboard-cli -g` 删除旧 skill。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-whiteboard` or related concepts

**Use Case 🤖:** Manage Feishu whiteboards (飞书白板)

---

### lark-wiki

**Category:** Feishu | **Path:** `lark-wiki/`

**Description:** 飞书知识库：管理知识空间、空间成员和文档节点。创建和查询知识空间、查看和管理空间成员、管理节点层级结构、在知识库中组织文档和快捷方式。当用户需要在知识库中查找或创建文档、浏览知识空间结构、查看或管理空间成员、移动或复制节点时使用。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-wiki` or related concepts

**Use Case 🤖:** Manage Feishu Wiki knowledge base (飞书知识库)

---

### lark-workflow-meeting-summary

**Category:** Feishu | **Path:** `lark-workflow-meeting-summary/`

**Description:** 会议纪要整理工作流：汇总指定时间范围内的会议纪要并生成结构化报告。当用户需要整理会议纪要、生成会议周报、回顾一段时间内的会议内容时使用。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-workflow-meeting-summary` or related concepts

**Use Case 🤖:** Generate meeting summaries from Feishu minutes (飞书会议纪要)

---

### lark-workflow-standup-report

**Category:** Feishu | **Path:** `lark-workflow-standup-report/`

**Description:** 日程待办摘要：编排 calendar +agenda 和 task +get-my-tasks，生成指定日期的日程与未完成任务摘要。适用于了解今天/明天/本周的安排。

**Version:** 1.0.0  
**Trigger Words 🤖:** When user mentions `lark-workflow-standup-report` or related concepts

**Use Case 🤖:** Generate standup reports from Feishu data (飞书站会报告)


## Superpowers Workflow {{superpowers-workflow}}

### brainstorming

**Category:** Workflow | **Path:** `brainstorming/`

**Description:** You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.

**Trigger Words 🤖:** When user mentions `brainstorming` or related concepts

**Use Case 🤖:** Explore user intent and design before implementation

---

### dispatching-parallel-agents

**Category:** Workflow | **Path:** `dispatching-parallel-agents/`

**Description:** Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies

**Trigger Words 🤖:** When user mentions `dispatching-parallel-agents` or related concepts

**Use Case 🤖:** Dispatch multiple independent tasks to parallel subagents

---

### executing-plans

**Category:** Workflow | **Path:** `executing-plans/`

**Description:** Use when you have a written implementation plan to execute in a separate session with review checkpoints

**Trigger Words 🤖:** When user mentions `executing-plans` or related concepts

**Use Case 🤖:** Execute a written implementation plan with review checkpoints

---

### find-skills

**Category:** Workflow | **Path:** `find-skills/`

**Description:** Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

**Trigger Words 🤖:** When user mentions `find-skills` or related concepts

**Use Case 🤖:** Discover and install agent skills from the marketplace

---

### finishing-a-development-branch

**Category:** Workflow | **Path:** `finishing-a-development-branch/`

**Description:** Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup

**Trigger Words 🤖:** When user mentions `finishing-a-development-branch` or related concepts

**Use Case 🤖:** Clean up, commit, and create PR for a finished dev branch

---

### humanizer-zh

**Category:** Writing | **Path:** `humanizer-zh/`

**Description:** 去除文本中的 AI 生成痕迹。适用于编辑或审阅文本，使其听起来更自然、更像人类书写。 基于维基百科的"AI 写作特征"综合指南。检测并修复以下模式：夸大的象征意义、 宣传性语言、以 -ing 结尾的肤浅分析、模糊的归因、破折号过度使用、三段式法则、 AI 词汇、否定式排比、过多的连接性短语。

**Trigger Words 🤖:** When user mentions `humanizer-zh` or related concepts

**Use Case 🤖:** Remove AI writing traces from Chinese text (AI痕迹去除)

---

### notebooklm

**Category:** Research | **Path:** `notebooklm/`

**Description:** Use this skill to query your Google NotebookLM notebooks directly from Claude Code for source-grounded, citation-backed answers from Gemini. Browser automation, library management, persistent auth. Drastically reduced hallucinations through document-only responses.

**Trigger Words 🤖:** When user mentions `notebooklm` or related concepts

**Use Case 🤖:** Generate structured research from Google NotebookLM sources

---

### receiving-code-review

**Category:** Quality | **Path:** `receiving-code-review/`

**Description:** Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation

**Trigger Words 🤖:** When user mentions `receiving-code-review` or related concepts

**Use Case 🤖:** Review code for quality and correctness

---

### requesting-code-review

**Category:** Quality | **Path:** `hermes-agent\skills\software-development\requesting-code-review/`

**Description:** Pre-commit review: security scan, quality gates, auto-fix.

**Version:** 2.0.0  
**Trigger Words 🤖:** When user mentions `requesting-code-review` or related concepts

**Use Case 🤖:** Review code for quality and correctness

---

### skill-creator

**Category:** Meta | **Path:** `skill-creator/`

**Description:** Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.

**Trigger Words 🤖:** When user mentions `skill-creator` or related concepts

**Use Case 🤖:** Create new Claude Code skills following best practices

---

### subagent-driven-development

**Category:** Workflow | **Path:** `hermes-agent\skills\software-development\subagent-driven-development/`

**Description:** Execute plans via delegate_task subagents (2-stage review).

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `subagent-driven-development` or related concepts

**Use Case 🤖:** Break work into parallel subagent tasks

---

### systematic-debugging

**Category:** Workflow | **Path:** `hermes-agent\skills\software-development\systematic-debugging/`

**Description:** 4-phase root cause debugging: understand bugs before fixing.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `systematic-debugging` or related concepts

**Use Case 🤖:** Debug issues using structured root-cause analysis

---

### test-driven-development

**Category:** Workflow | **Path:** `hermes-agent\skills\software-development\test-driven-development/`

**Description:** TDD: enforce RED-GREEN-REFACTOR, tests before code.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `test-driven-development` or related concepts

**Use Case 🤖:** Write tests first, then implement to make them pass

---

### ui-ux-pro-max

**Category:** Design | **Path:** `ui-ux-pro-max/`

**Description:** UI/UX design intelligence for web and mobile. Includes 50+ styles, 161 color palettes, 57 font pairings, 161 product types, 99 UX guidelines, and 25 chart types across 10 stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui, and HTML/CSS). Actions: plan, build, create, design, implement, review, fix, improve, optimize, enhance, refactor, and check UI/UX code. Projects: website, landing page, dashboard, admin panel, e-commerce, SaaS, portfolio, blog, and mobile app. Elements: button, modal, navbar, sidebar, card, table, form, and chart. Styles: glassmorphism, claymorphism, minimalism, brutalism, neumorphism, bento grid, dark mode, responsive, skeuomorphism, and flat design. Topics: color systems, accessibility, animation, layout, typography, font pairing, spacing, interaction states, shadow, and gradient. Integrations: shadcn/ui MCP for component search and examples.

**Trigger Words 🤖:** When user mentions `ui-ux-pro-max` or related concepts

**Use Case 🤖:** Apply premium UI/UX design patterns and best practices

---

### using-git-worktrees

**Category:** Workflow | **Path:** `using-git-worktrees/`

**Description:** Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback

**Trigger Words 🤖:** When user mentions `using-git-worktrees` or related concepts

**Use Case 🤖:** Manage isolated git worktrees for parallel work

---

### using-superpowers

**Category:** Workflow | **Path:** `using-superpowers/`

**Description:** Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions

**Trigger Words 🤖:** When user mentions `using-superpowers` or related concepts

**Use Case 🤖:** Entry point: establish how to find and use skills

---

### verification-before-completion

**Category:** Workflow | **Path:** `verification-before-completion/`

**Description:** Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always

**Trigger Words 🤖:** When user mentions `verification-before-completion` or related concepts

**Use Case 🤖:** Verify changes work before marking tasks complete

---

### writing-plans

**Category:** Workflow | **Path:** `hermes-agent\skills\software-development\writing-plans/`

**Description:** Write implementation plans: bite-sized tasks, paths, code.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `writing-plans` or related concepts

**Use Case 🤖:** Create detailed implementation plans from designs

---

### writing-skills

**Category:** Meta | **Path:** `writing-skills/`

**Description:** Use when creating new skills, editing existing skills, or verifying skills work before deployment

**Trigger Words 🤖:** When user mentions `writing-skills` or related concepts

**Use Case 🤖:** Write and publish new Claude Code skills


## nature-skills {{nature-skills}}

**Version:** 1.0.0  
**Author:** Yuan1z0825  
**Repo:** <https://github.com/Yuan1z0825/nature-skills>  

### nature-academic-search

**Category:** Research | **Path:** `nature-skills\skills\nature-academic-search/`

**Description:** Multi-source literature search, citation verification, MeSH search strategy, citation file management (.nbib/.ris/.bib conversion), and reference management (BibTeX, related articles, ID conversion) via MCP tools (PubMed, CrossRef, arXiv). Use when the user needs coordinated multi-step literature workflows beyond a single MCP call.

**Trigger Words 🤖:** When user mentions `nature-academic-search` or related concepts

**Use Case 🤖:** Search for papers, content, or references

---

### nature-citation

**Category:** References | **Path:** `nature-skills\skills\nature-citation/`

**Description:** Add strict Nature/CNS citations to manuscript text by splitting long passages into citable segments, searching only accepted flagship and subjournal titles from Nature Portfolio, the AAAS Science family, and Cell Press, filtering by publication time range, and exporting one reference-manager-ready output by default. Use this skill whenever the user asks to input text and automatically get references, add citations to a paragraph/manuscript, find Nature-series or CNS support for statements, create text-to-reference correspondence, "分段引用", "自动给出引用", "Nature系列引用", "CNS及子刊", "支撑文献", "补引用", "找引用", or export EndNote/RIS/ENW/Zotero RDF.

**Trigger Words 🤖:** When user mentions `nature-citation` or related concepts

**Use Case 🤖:** Manage, format, or check citations

---

### nature-data

**Category:** Data | **Path:** `nature-skills\skills\nature-data/`

**Description:** Prepare, audit, or revise Nature-ready Data Availability statements, data repository plans, dataset citations, and FAIR metadata checklists for manuscripts. Use when the user asks about Nature data availability, research data sharing, repository selection, accession numbers, restricted or sensitive data, source data, supplementary datasets, DataCite-style dataset references, FAIR metadata for academic publication, or Chinese-to-English data availability wording for Chinese-speaking authors preparing Nature-family submissions.

**Trigger Words 🤖:** When user mentions `nature-data` or related concepts

**Use Case 🤖:** Handle data-related tasks

---

### nature-figure

**Category:** Figures | **Path:** `nature-skills\skills\nature-figure/`

**Description:** Submission-grade Nature/high-impact journal figure workflow for Python or R. Use whenever the user asks to create, revise, audit, or polish manuscript figures, multi-panel scientific plots, figures4papers-style matplotlib plots, or journal-ready SVG/PDF/TIFF outputs, especially for Nature-family or other high-impact journals. Before plotting, define the figure's conclusion, evidence logic, export needs, and review risks. If the user has not chosen Python or R, ask "Python or R?" and stop. Use only the selected backend for figure generation, previewing, exporting, and QA. Supports matplotlib/seaborn and ggplot2/patchwork/ComplexHeatmap. Not for dashboards or Illustrator/Figma-first infographics.

**Trigger Words 🤖:** When user mentions `nature-figure` or related concepts

**Use Case 🤖:** Create or refine scientific figures and diagrams

---

### nature-paper2ppt

**Category:** Conversion | **Path:** `nature-skills\skills\nature-paper2ppt/`

**Description:** Build a complete but efficient Nature-style Chinese PPTX presentation from a scientific paper, preprint, PDF, article text, abstract, figure legends, or reading notes. Use this skill whenever the user asks to make slides/PPT/PPTX for journal club, group meeting, paper sharing, thesis seminar, lab meeting, department report, or academic presentation from a research paper, not only medical papers. It identifies the paper type and argument, selects only the figures needed for the story, writes Chinese slide content and speaker notes, creates the actual .pptx deck, and performs lightweight verification with cross-platform Python tooling by default.

**Trigger Words 🤖:** When user mentions `nature-paper2ppt` or related concepts

**Use Case 🤖:** Convert papers into presentation slides

---

### nature-polishing

**Category:** Text Refinement | **Path:** `nature-skills\skills\nature-polishing/`

**Description:** Polish, restructure, or translate academic prose into Nature-leaning English using writing-strategy principles, curated Nature/Nature Communications article patterns, and phrase-level support from Academic Phrasebank. Use whenever the user asks to polish a manuscript paragraph, abstract, introduction, results, discussion, conclusion, title, methods section, or Chinese academic draft for publication-quality English.

**Version:** 5.0.2  
**Trigger Words 🤖:** When user mentions `nature-polishing` or related concepts

**Use Case 🤖:** Polish/refine English academic text for submission

---

### nature-reader

**Category:** Reading | **Path:** `nature-skills\skills\nature-reader/`

**Description:** Build full-paper Chinese-English side-by-side, figure/table-aware, source-grounded Markdown readers for journal or conference papers from PDF, DOI, arXiv, publisher HTML, or pasted text. Use whenever the user asks to translate or read a paper, make 中英文对照/原文对照/全文翻译解读, extract figures or tables into the right positions, preserve figure/table placement near relevant prose, or keep exact source anchors for every block. This skill must not degrade into a summary-only output unless the user explicitly asks for a summary.

**Trigger Words 🤖:** When user mentions `nature-reader` or related concepts

**Use Case 🤖:** Read and analyze papers in depth

---

### nature-response

**Category:** Review | **Path:** `nature-skills\skills\nature-response/`

**Description:** Draft, audit, or revise point-by-point reviewer response letters for Nature-family manuscript revisions. Use when the user provides reviewer comments, editor decision letters, revision notes, response drafts, or asks how to respond to major/minor revision requests, rebuttal letters, response to reviewers, peer-review reports, 审稿意见回复, 逐点回复, 修回信, 大修回复, 小修回复, or 如何回复 reviewer.

**Version:** 0.1.0  
**Trigger Words 🤖:** When user mentions `nature-response` or related concepts

**Use Case 🤖:** Draft responses to peer review comments

---

### nature-writing

**Category:** Text Refinement | **Path:** `nature-skills\skills\nature-writing/`

**Description:** Draft, restructure, or plan Nature-style manuscript sections from author-provided claims, results, figures, notes, or Chinese drafts. Use when the user wants to write or rebuild an abstract, introduction, results narrative, discussion, conclusion, title, or full manuscript argument rather than only polish finished prose.

**Version:** 0.2.0  
**Trigger Words 🤖:** When user mentions `nature-writing` or related concepts

**Use Case 🤖:** Polish/refine English academic text for submission


## Custom Skills {{custom-skills}}

### research-paper-writing

**Category:** Writing | **Path:** `hermes-agent\skills\research\research-paper-writing/`

**Description:** Write ML papers for NeurIPS/ICML/ICLR: design→submit.

**Version:** 1.1.0  
**Trigger Words 🤖:** When user mentions `research-paper-writing` or related concepts

**Use Case 🤖:** Draft or plan content

---

### weekly-github-trending

**Category:** Meta | **Path:** `weekly-github-trending/`

**Description:** 每周GitHub热门项目推荐 - 调研本周热门项目，选出AI编程/研究/学习三大领域TOP5，生成飞书文档风格推荐文章，经Humanizer Zh去AI痕迹，定时发送到飞书

**Trigger Words 🤖:** When user mentions `weekly-github-trending` or related concepts

**Use Case 🤖:** Generate weekly GitHub trending projects report (每周GitHub热门)


---

## Appendix

### A. How Claude Code Skills Are Triggered

Skills in Claude Code use **progressive disclosure**. The system loads skill metadata
(name + description) at session start, then loads the full SKILL.md only when relevant.
A skill activates when:

1. **Name match:** Your prompt mentions the skill name or key terms from its description
2. **Intent match:** Your request aligns with the skill's `primary_intent` or trigger examples
3. **Explicit invoke:** You type `/<skill-name>` or use the Skill tool

| Trigger Method | Example | When It Works |
|---------------|---------|---------------|
| Keyword in prompt | "润色这段英文" | `ppw:polish`, `nature-polishing` activate |
| Intent match | "帮我写论文" | `academic-paper` pipeline activates |
| Slash command | `/brainstorming` | Any skill with a slash command |
| Skill tool | Skill("brainstorming") | Any registered skill |

### B. Common Skill Workflows

#### Academic Paper Writing (完整论文工作流)

```

brainstorming → academic-paper → ppw:polish → ppw:reviewer-simulation
    → ppw:de-ai → nature-polishing → ppw:cover-letter → ppw:translation

```

#### Code Development (代码开发工作流)

```

brainstorming → writing-plans → test-driven-development
    → requesting-code-review → receiving-code-review → verification-before-completion

```

#### Weekly Report (每周报告自动化)

```

weekly-github-trending → humanizer-zh → lark-doc (publish)

```

#### Debugging (调试工作流)

```

systematic-debugging → verification-before-completion

```

### C. How to Install These Skills

#### Plugin-based skills (ECC, Hermes, Nature, Academic)

```bash

# Install from marketplace
/plugin marketplace add affaan-m/everything-claude-code
/plugin install everything-claude-code@everything-claude-code

# Or manual clone
git clone <repo-url> ~/.claude/skills/<skill-name>
```

#### Individual skills (Lark, Superpowers, Custom)

```bash

# Copy to skills directory
cp -r <skill-dir> ~/.claude/skills/<skill-name>
# Or symlink for development
ln -s /path/to/skill ~/.claude/skills/<skill-name>
```

### D. Source Comparison: When to Use Which

| Source | Best For | Scope | Maintenance |
|--------|----------|-------|-------------|
| **everything-claude-code** | General development, full-stack, DevOps | 234 skills | Community (140K+ stars), very active |
| **hermes-agent** | AI agent learning, memory, automation | 164 skills | Community (143K+ stars), active |
| **Lark Integration** | Feishu/Lark API operations | 22 skills | Personal/team maintained |
| **Superpowers Workflow** | Process discipline (plan, TDD, review) | 19 skills | Built-in, core to Claude Code |
| **Custom Skills** | Niche academic/research needs | 2 skills | Self-maintained |

### E. Maintenance Guide

- **Update skills:** Re-run plugin install or `git pull` in skill directories
- **Regenerate catalog:** `python generate_catalog.py`
- **Add new skills:** Install to `~/.claude/skills/`, then regenerate
- **Remove skills:** Delete from `~/.claude/skills/`, then regenerate
- **Version tracking:** Plugin-based skills auto-track versions via `plugin.json`

### F. Source Repositories

- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) — 140K+ stars, MIT license
- [hermes-agent](https://github.com/NousResearch/hermes-agent) — 143K+ stars
- [academic-research-skills](https://github.com/Imbad0202/academic-research-skills)
