#!/usr/bin/env python3
"""Extract metadata from Claude Code SKILL.md files and generate a catalog.

Scans ~/.claude/skills/ recursively, parses YAML frontmatter from every
SKILL.md, reads plugin.json for context, and writes a single organized
SKILLS_CATALOG.md with detailed entries.

Usage:
    python generate_catalog.py [--output SKILLS_CATALOG.md]
"""

import os
import json
import re

SKILLS_ROOT = os.path.expanduser("~/.claude/skills")

# Paths to skip
SKIP_PATTERNS = [
    '/docs/ja-JP/',
    '/docs/zh-CN/',
]

# Grouping for standalone directories (no plugin.json)
STANDALONE_GROUPS = {
    'lark-': 'Lark (飞书) Integration',
    'brainstorming': 'Superpowers Workflow',
    'dispatching-parallel-agents': 'Superpowers Workflow',
    'executing-plans': 'Superpowers Workflow',
    'find-skills': 'Superpowers Workflow',
    'finishing-a-development-branch': 'Superpowers Workflow',
    'humanizer-zh': 'Superpowers Workflow',
    'notebooklm': 'Superpowers Workflow',
    'receiving-code-review': 'Superpowers Workflow',
    'requesting-code-review': 'Superpowers Workflow',
    'skill-creator': 'Superpowers Workflow',
    'subagent-driven-development': 'Superpowers Workflow',
    'systematic-debugging': 'Superpowers Workflow',
    'test-driven-development': 'Superpowers Workflow',
    'ui-ux-pro-max': 'Superpowers Workflow',
    'using-git-worktrees': 'Superpowers Workflow',
    'using-superpowers': 'Superpowers Workflow',
    'verification-before-completion': 'Superpowers Workflow',
    'writing-plans': 'Superpowers Workflow',
    'writing-skills': 'Superpowers Workflow',
    'weekly-github-trending': 'Custom Skills',
    'karpathy-guidelines': 'Custom Skills',
    'claude-api': 'Claude API Tools',
    'update-config': 'Superpowers Workflow',
    'keybindings-help': 'Superpowers Workflow',
    'verify': 'Superpowers Workflow',
    'simplify': 'Superpowers Workflow',
    'fewer-permission-prompts': 'Superpowers Workflow',
    'loop': 'Superpowers Workflow',
    'run': 'Superpowers Workflow',
    'init': 'Superpowers Workflow',
    'review': 'Superpowers Workflow',
    'security-review': 'Superpowers Workflow',
    'agent-reach': 'Projects (Non-Skill)',
    'research-paper-writing': 'Custom Skills',
    'AI-Research-SKILLs': 'AI Research Skills',
    'ai-research-skills': 'AI Research Skills',
    'nature-skills': 'Nature Skills',
}

SOURCE_DESCRIPTIONS = {
    'everything-claude-code': 'ECC universal configuration (180+ skills, 47 agents, 79 commands)',
    'hermes-agent': 'Digital twin agent with learning loop and skill auto-generation',
    'ai-research-skills': 'AI/ML research engineering toolkit (98 skills, 22 domains: model arch to paper writing)',
    'AI-Research-SKILLs': 'AI/ML research engineering toolkit (98 skills, 22 domains: model arch to paper writing)',
    'academic-research-skills': 'Production-grade academic research pipeline (4 skills, 35+ modes)',
    'nature-skills': 'Nature/Science journal writing toolkit (9 skills)',
    'paper-polish-workflow': 'Academic paper polishing workflow (16 skills)',
    'Superpowers Workflow': 'Built-in workflow discipline skills (plan, debug, review, verify)',
    'Lark (飞书) Integration': 'Feishu/Lark API integrations (docs, sheets, calendar, IM, etc.)',
    'Claude API Tools': 'Claude API / Anthropic SDK development tools',
    'Custom Skills': 'User-installed custom skills',
    'Projects (Non-Skill)': 'Project directories without SKILL.md',
}

# ── YAML frontmatter ──────────────────────────────────────────────────

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


def parse_frontmatter(text: str) -> dict:
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', text, re.DOTALL)
    if not m:
        return {}
    yaml_str = m.group(1)
    body = m.group(2).strip()
    result = {"_body_first_200": body[:200]}
    if _HAS_YAML:
        try:
            parsed = yaml.safe_load(yaml_str)
            if isinstance(parsed, dict):
                result.update(parsed)
        except yaml.YAMLError:
            pass
    desc = result.get('description', '')
    if isinstance(desc, str):
        result['description'] = ' '.join(desc.split())
    return result


# ── File discovery ────────────────────────────────────────────────────

def find_skill_files(root: str) -> list[dict]:
    skills = []
    if not os.path.isdir(root):
        print(f"Skills directory not found: {root}")
        return skills
    for dirpath, dirnames, filenames in os.walk(root):
        for fname in filenames:
            if fname == 'SKILL.md':
                skill_path = os.path.join(dirpath, fname)
                rel_dir = os.path.relpath(os.path.dirname(skill_path), root)
                skills.append({
                    'path': skill_path,
                    'rel_dir': rel_dir,
                    'plugin': _find_plugin_context(dirpath, root),
                })
    return skills


def _find_plugin_context(skill_dir: str, root: str) -> dict | None:
    current = skill_dir
    for _ in range(6):
        # Try plugin.json first, then marketplace.json
        for fname in ('plugin.json', 'marketplace.json'):
            meta_path = os.path.join(current, '.claude-plugin', fname)
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # marketplace.json wraps metadata differently
                    if fname == 'marketplace.json':
                        return {
                            'name': data.get('name', ''),
                            'version': data.get('metadata', {}).get('version', ''),
                            'description': data.get('metadata', {}).get('description', ''),
                            'author': data.get('owner', {}),
                        }
                    return data
                except (json.JSONDecodeError, OSError):
                    break
        parent = os.path.dirname(current)
        if parent == current or os.path.normpath(parent) == os.path.normpath(root):
            break
        current = parent
    return None


def _should_skip(rel_dir: str) -> bool:
    normalized = rel_dir.replace('\\', '/')
    for pattern in SKIP_PATTERNS:
        if pattern in normalized:
            return True
    return False


# ── Grouping ──────────────────────────────────────────────────────────

def _get_source_group(rel_dir: str, plugin: dict | None, skill_name: str = '') -> str:
    parts = rel_dir.replace('\\', '/').split('/')
    top = parts[0] if parts else 'other'
    plugin_name = plugin.get('name', '') if plugin else ''
    if plugin_name:
        if 'everything' in plugin_name.lower() or 'ecc' in plugin_name.lower():
            return 'everything-claude-code'
        return plugin_name
    for prefix, group in STANDALONE_GROUPS.items():
        if top == prefix or top.startswith(prefix) or skill_name.startswith(prefix):
            return group
    return top


# ── Use case inference ────────────────────────────────────────────────

USE_CASE_PATTERNS = [
    # Specific multi-word / named patterns (matched by name priority)
    ('code-review', 'Quality', 'Review code for quality and correctness'),
    ('cover-letter', 'Submission', 'Write cover letters for journal submission'),
    ('deep-research', 'Research', 'Conduct in-depth literature research and analysis'),
    ('repo-to-paper', 'Conversion', 'Convert code repository documentation into a paper'),
    ('web-artifact', 'Web', 'Build web artifacts and single-page apps'),
    ('internal-comm', 'Communication', 'Internal communications content'),
    ('de-ai', 'Text Refinement', 'Remove AI-generated text patterns from academic writing'),
    ('get-paper', 'Research', 'Retrieve and download academic papers'),
    ('paper2ppt', 'Conversion', 'Convert papers into presentation slides'),
    ('accessibility', 'Accessibility', 'Design and audit accessible digital products (WCAG)'),
    # Lark / Feishu skills
    ('lark-approval', 'Feishu', 'Manage Feishu approval instances and tasks (飞书审批)'),
    ('lark-attendance', 'Feishu', 'Query Feishu attendance and clock-in records (飞书考勤)'),
    ('lark-base', 'Feishu', 'Manage Feishu Base: tables, fields, records, views (飞书多维表格)'),
    ('lark-calendar', 'Feishu', 'Manage Feishu calendar: events, meetings, rooms (飞书日历)'),
    ('lark-contact', 'Feishu', 'Resolve Feishu contacts: name to open_id lookup (飞书通讯录)'),
    ('lark-doc', 'Feishu', 'Create, read, edit Feishu Docs and Wiki documents (飞书云文档)'),
    ('lark-drive', 'Feishu', 'Manage Feishu Drive files and folders (飞书云盘)'),
    ('lark-event', 'Feishu', 'Handle Feishu event subscriptions and callbacks (飞书事件)'),
    ('lark-im', 'Feishu', 'Send/receive Feishu messages, manage groups (飞书即时通讯)'),
    ('lark-mail', 'Feishu', 'Send and manage Feishu email (飞书邮箱)'),
    ('lark-minutes', 'Feishu', 'Manage Feishu meeting minutes (飞书妙记)'),
    ('lark-openapi-explorer', 'Feishu', 'Explore and debug Feishu Open API endpoints (飞书API探索)'),
    ('lark-shared', 'Feishu', 'Shared Feishu authentication and API helpers (飞书共享模块)'),
    ('lark-sheets', 'Feishu', 'Manage Feishu Sheets and spreadsheets (飞书电子表格)'),
    ('lark-skill-maker', 'Feishu', 'Create Feishu integration skills (飞书Skill制作)'),
    ('lark-slides', 'Feishu', 'Create and edit Feishu presentation slides (飞书演示)'),
    ('lark-task', 'Feishu', 'Manage Feishu tasks and to-do lists (飞书任务)'),
    ('lark-vc', 'Feishu', 'Manage Feishu video conferencing (飞书视频会议)'),
    ('lark-whiteboard', 'Feishu', 'Manage Feishu whiteboards (飞书白板)'),
    ('lark-wiki', 'Feishu', 'Manage Feishu Wiki knowledge base (飞书知识库)'),
    ('lark-workflow-meeting-summary', 'Feishu', 'Generate meeting summaries from Feishu minutes (飞书会议纪要)'),
    ('lark-workflow-standup-report', 'Feishu', 'Generate standup reports from Feishu data (飞书站会报告)'),
    # Superpowers workflow skills
    ('brainstorming', 'Workflow', 'Explore user intent and design before implementation'),
    ('dispatching-parallel-agents', 'Workflow', 'Dispatch multiple independent tasks to parallel subagents'),
    ('executing-plans', 'Workflow', 'Execute a written implementation plan with review checkpoints'),
    ('find-skills', 'Workflow', 'Discover and install agent skills from the marketplace'),
    ('finishing-a-development-branch', 'Workflow', 'Clean up, commit, and create PR for a finished dev branch'),
    ('fewer-permission-prompts', 'Workflow', 'Reduce permission prompts by adding allowlists'),
    ('humanizer-zh', 'Writing', 'Remove AI writing traces from Chinese text (AI痕迹去除)'),
    ('init', 'Workflow', 'Initialize a new CLAUDE.md with codebase documentation'),
    ('keybindings-help', 'Workflow', 'Customize Claude Code keyboard shortcuts'),
    ('karpathy-guidelines', 'Meta', 'Apply Karpathy LLM coding best practices'),
    ('loop', 'Workflow', 'Run recurring tasks on a timer interval'),
    ('notebooklm', 'Research', 'Generate structured research from Google NotebookLM sources'),
    ('receiving-code-review', 'Workflow', 'Process and apply code review feedback systematically'),
    ('requesting-code-review', 'Workflow', 'Prepare and request code review for changes'),
    ('review', 'Workflow', 'Review code changes for quality and correctness'),
    ('run', 'Workflow', 'Launch and drive the project app to test changes'),
    ('security-review', 'Workflow', 'Security review of code changes and architecture'),
    ('simplify', 'Workflow', 'Review code for reuse, quality, and efficiency'),
    ('skill-creator', 'Meta', 'Create new Claude Code skills following best practices'),
    ('subagent-driven-development', 'Workflow', 'Break work into parallel subagent tasks'),
    ('systematic-debugging', 'Workflow', 'Debug issues using structured root-cause analysis'),
    ('test-driven-development', 'Workflow', 'Write tests first, then implement to make them pass'),
    ('ui-ux-pro-max', 'Design', 'Apply premium UI/UX design patterns and best practices'),
    ('update-config', 'Workflow', 'Configure Claude Code settings, hooks, and permissions'),
    ('using-git-worktrees', 'Workflow', 'Manage isolated git worktrees for parallel work'),
    ('using-superpowers', 'Workflow', 'Entry point: establish how to find and use skills'),
    ('verification-before-completion', 'Workflow', 'Verify changes work before marking tasks complete'),
    ('verify', 'Workflow', 'Verify code changes work by running the app'),
    ('weekly-github-trending', 'Meta', 'Generate weekly GitHub trending projects report (每周GitHub热门)'),
    ('writing-plans', 'Workflow', 'Create detailed implementation plans from designs'),
    ('writing-skills', 'Meta', 'Write and publish new Claude Code skills'),
    # AI-Research-SKILLs patterns (name-based, matched first)
    ('autoresearch', 'AI Research', 'Autonomous research orchestration with two-loop architecture'),
    ('model-architecture', 'AI Research', 'Implement and understand LLM architectures (GPT, Mamba, RWKV)'),
    ('tokenization', 'AI Research', 'Train custom tokenizers and handle multilingual text'),
    ('fine-tuning', 'AI Research', 'Fine-tune LLMs with LoRA, QLoRA, or full fine-tuning'),
    ('mechanistic-interpretability', 'AI Research', 'Analyze model internals and find neural circuits'),
    ('data-processing', 'AI Research', 'Curate and process training datasets at scale'),
    ('post-training', 'AI Research', 'RLHF and preference alignment for LLMs'),
    ('safety-alignment', 'AI Research', 'AI safety, content moderation, prompt injection detection'),
    ('distributed-training', 'AI Research', 'Multi-GPU and multi-node distributed training'),
    ('infrastructure', 'AI Research', 'GPU cloud compute orchestration and job deployment'),
    ('optimization', 'AI Research', 'Model optimization, quantization, and memory reduction'),
    ('evaluation', 'AI Research', 'LLM benchmarking and performance measurement'),
    ('inference-serving', 'AI Research', 'Production LLM inference deployment'),
    ('mlops', 'AI Research', 'ML experiment tracking and lifecycle management'),
    ('agents', 'AI Research', 'LLM agent frameworks and autonomous systems'),
    ('rag', 'AI Research', 'Retrieval-Augmented Generation and semantic search'),
    ('prompt-engineering', 'AI Research', 'Structured LLM outputs and constrained generation'),
    ('observability', 'AI Research', 'LLM application monitoring and debugging'),
    ('multimodal', 'AI Research', 'Vision, audio, and multimodal model development'),
    ('emerging-techniques', 'AI Research', 'Cutting-edge ML: MoE, merging, distillation, pruning'),
    ('ml-paper-writing', 'AI Research', 'Write publication-ready ML/AI papers for top conferences'),
    ('research-ideation', 'AI Research', 'Structured brainstorming for new research directions'),
    ('agent-native-research-artifact', 'AI Research', 'Compile research into falsifiable agent-traversable artifacts'),
    # Specific AI tools
    ('litgpt', 'AI Research', 'Implement and train LLMs with LitGPT framework'),
    ('mamba', 'AI Research', 'State space models for efficient sequence modeling'),
    ('nanogpt', 'AI Research', 'Minimal GPT implementation for learning and experimentation'),
    ('rwkv', 'AI Research', 'RNN-style LLM with linear attention'),
    ('torchtitan', 'AI Research', 'Large-scale LLM training with PyTorch native'),
    ('axolotl', 'AI Research', 'Fine-tune LLMs with Axolotl framework'),
    ('llama-factory', 'AI Research', 'Fine-tune LLaMA models with LLaMA-Factory'),
    ('peft', 'AI Research', 'Parameter-Efficient Fine-Tuning with HuggingFace PEFT'),
    ('unsloth', 'AI Research', 'Fast and memory-efficient LLM fine-tuning'),
    ('deepspeed', 'AI Research', 'DeepSpeed distributed training optimization'),
    ('megatron', 'AI Research', 'NVIDIA Megatron for large-scale model training'),
    ('flash-attention', 'AI Research', 'Fast and memory-efficient attention mechanism'),
    ('vllm', 'AI Research', 'High-throughput LLM inference with vLLM'),
    ('sglang', 'AI Research', 'Efficient LLM inference and serving with SGLang'),
    ('langchain', 'AI Research', 'Build LLM applications with LangChain'),
    ('llamaindex', 'AI Research', 'Data framework for LLM applications'),
    ('crewai', 'AI Research', 'Multi-agent orchestration framework'),
    ('dspy', 'AI Research', 'Programming framework for LM pipelines'),
    ('chroma', 'AI Research', 'Vector database for AI applications'),
    ('faiss', 'AI Research', 'Efficient similarity search and clustering'),
    ('clip', 'AI Research', 'Vision-language model for multimodal tasks'),
    ('whisper', 'AI Research', 'Speech recognition and transcription'),
    ('stable-diffusion', 'AI Research', 'Text-to-image generation model'),
    ('wandb', 'AI Research', 'Experiment tracking with Weights & Biases'),
    ('mlflow', 'AI Research', 'ML lifecycle management with MLflow'),
    ('tensorboard', 'AI Research', 'TensorBoard visualization toolkit'),
    ('openrlhf', 'AI Research', 'Ray-based RLHF training framework'),
    ('trl', 'AI Research', 'Transformer Reinforcement Learning'),
    ('verl', 'AI Research', 'Versatile RL training framework'),
    ('axolotl', 'AI Research', 'Multi-modal LLM fine-tuning toolkit'),
    ('modal', 'AI Research', 'Serverless GPU cloud for ML workloads'),
    ('skypilot', 'AI Research', 'Multi-cloud job runner for ML'),
    ('saelens', 'AI Research', 'Sparse autoencoder analysis for interpretability'),
    ('transformer-lens', 'AI Research', 'Mechanistic interpretability for GPT-style models'),
    ('nnsight', 'AI Research', 'Neural network interpretability framework'),
    ('pyvene', 'AI Research', 'Interventions on PyTorch models for interpretability'),
    ('huggingface-tokenizers', 'AI Research', 'Fast tokenization with HuggingFace Tokenizers'),
    ('sentencepiece', 'AI Research', 'Unsupervised text tokenizer and detokenizer'),
    ('nemo-curator', 'AI Research', 'Scalable data curation for LLM training'),
    ('ray-data', 'AI Research', 'Distributed data processing with Ray'),
    ('llamaguard', 'AI Research', 'LLM-based input-output safeguard model'),
    ('nemo-guardrails', 'AI Research', 'Programmable guardrails for LLMs'),
    ('constitutional-ai', 'AI Research', 'AI alignment through constitutional principles'),
    ('gptq', 'AI Research', 'Post-training quantization for LLMs'),
    ('awq', 'AI Research', 'Activation-aware weight quantization'),
    ('gguf', 'AI Research', 'Quantized model format for CPU inference'),
    ('bitsandbytes', 'AI Research', 'Quantization and optimizers for LLMs'),
    ('lm-evaluation-harness', 'AI Research', 'Comprehensive LLM evaluation framework'),
    ('tensorrt-llm', 'AI Research', 'NVIDIA TensorRT for LLM inference optimization'),
    ('llama-cpp', 'AI Research', 'LLM inference in C/C++ with llama.cpp'),
    ('accelerate', 'AI Research', 'HuggingFace Accelerate for distributed training'),
    ('pytorch-lightning', 'AI Research', 'Lightweight PyTorch training framework'),
    ('ray-train', 'AI Research', 'Distributed training with Ray Train'),
    ('pinecone', 'AI Research', 'Vector database for production AI'),
    ('qdrant', 'AI Research', 'Vector search engine for AI applications'),
    ('sentence-transformers', 'AI Research', 'Sentence embeddings and semantic search'),
    ('instructor', 'AI Research', 'Structured outputs from LLMs'),
    ('guidance', 'AI Research', 'Controlled generation from language models'),
    ('outlines', 'AI Research', 'Structured text generation'),
    ('langsmith', 'AI Research', 'LLM application observability platform'),
    ('phoenix', 'AI Research', 'AI observability and evaluation'),
    ('audiocraft', 'AI Research', 'Audio generation and processing'),
    ('blip-2', 'AI Research', 'Vision-language pre-training'),
    ('llava', 'AI Research', 'Large language and vision assistant'),
    ('segment-anything', 'AI Research', 'Promptable image segmentation'),
    ('knowledge-distillation', 'AI Research', 'Transfer knowledge from large to small models'),
    ('model-merging', 'AI Research', 'Merge multiple models into one'),
    ('model-pruning', 'AI Research', 'Reduce model size through pruning'),
    ('moe-training', 'AI Research', 'Mixture-of-Experts model training'),
    ('speculative-decoding', 'AI Research', 'Accelerate LLM inference with speculative decoding'),
    ('long-context', 'AI Research', 'Extend LLM context window length'),
    ('academic-plotting', 'AI Research', 'Publication-quality figures for ML papers'),
    ('systems-paper-writing', 'AI Research', 'Systems conference paper writing (OSDI, SOSP, ASPLOS)'),
    ('conference-talks', 'AI Research', 'Prepare conference presentation slides and talks'),
    # Hermes agent patterns
    ('hermes-', 'Agent', 'Digital twin agent with learning and memory capabilities'),
    # Single-word patterns (lower priority, matched against description too)
    ('polish', 'Text Refinement', 'Polish/refine English academic text for submission'),
    ('citation', 'References', 'Manage, format, or check citations'),
    ('figure', 'Figures', 'Create or refine scientific figures and diagrams'),
    ('abstract', 'Writing', 'Write or polish paper abstracts'),
    ('visualization', 'Visualization', 'Create data visualizations for papers'),
    ('logic', 'Quality', 'Check logical flow and argument coherence'),
    ('experiment', 'Methods', 'Describe experimental methods and results'),
    ('literature', 'Research', 'Write literature review sections'),
    ('caption', 'Writing', 'Write or polish figure/table captions'),
    ('pipeline', 'Orchestration', 'Master orchestrator for multi-stage workflows'),
    ('translat', 'Translation', 'Translate text between languages'),
    ('reader', 'Reading', 'Read and analyze papers in depth'),
    ('response', 'Review', 'Draft responses to peer review comments'),
    ('database', 'Database', 'Database design, migration, and optimization'),
    ('security', 'Security', 'Security review and vulnerability scanning'),
    ('frontend', 'Frontend', 'Build frontend UI components and patterns'),
    ('backend', 'Backend', 'Build backend services and APIs'),
    ('docker', 'DevOps', 'Container management and Docker configuration'),
    ('deploy', 'DevOps', 'Deployment and CI/CD configuration'),
    ('browser', 'Browser', 'Browser automation and testing'),
    ('slide', 'Presentation', 'Create presentation slides'),
    ('canvas', 'Design', 'Canvas-based visual design'),
    ('xlsx', 'Documents', 'Excel spreadsheet creation and editing'),
    ('docx', 'Documents', 'Word document creation and editing'),
    ('pptx', 'Documents', 'PowerPoint creation and editing'),
    ('slack', 'Communication', 'Slack integration and messaging'),
    ('keybind', 'Configuration', 'Customize keyboard shortcuts'),
    ('cron', 'Automation', 'Schedule recurring tasks'),
    ('hook', 'Integration', 'Configure and manage hooks'),
    ('mcp', 'Integration', 'Manage MCP server connections'),
    ('permission', 'Security', 'Manage permissions and access control'),
    ('eval', 'Quality', 'Evaluate and benchmark outputs'),
    ('debug', 'Debugging', 'Systematically debug issues'),
    ('content', 'Content', 'Content generation and management'),
    ('theme', 'Design', 'Theme and visual design'),
    ('brand', 'Design', 'Brand guidelines and visual identity'),
    ('memory', 'Context', 'Manage persistent memory and context'),
    ('api', 'API', 'Design and implement APIs'),
    ('learn', 'Learning', 'Continuous learning and skill evolution'),
    ('config', 'Configuration', 'Configure settings and preferences'),
    ('pattern', 'Architecture', 'Software design patterns'),
    ('plan', 'Planning', 'Create implementation plans'),
    ('execut', 'Execution', 'Execute implementation plans'),
    ('workflow', 'Workflow', 'Manage multi-step workflows'),
    ('guideline', 'Meta', 'Behavioral guide for coding best practices'),
    ('trending', 'Meta', 'Generate trending content reports'),
    ('test', 'Testing', 'Write and run tests'),
    ('git', 'Version Control', 'Git workflows and branch management'),
    ('search', 'Research', 'Search for papers, content, or references'),
    ('team', 'Collaboration', 'Coordinate multi-author workflows'),
    ('data', 'Data', 'Handle data-related tasks'),
    ('write', 'Writing', 'Draft or plan content'),
    ('update', 'Editing', 'Revise and update content'),
    ('art', 'Creative', 'Algorithmic art generation'),
    ('agent', 'Agent', 'Configure and manage AI agents'),
    ('skill', 'Meta', 'Create, manage, or discover skills'),
]


def infer_use_case(name: str, desc: str, triggers: dict | None) -> tuple[str, str]:
    if triggers and isinstance(triggers, dict):
        primary = triggers.get('primary_intent', '')
        if primary:
            return 'General', primary

    name_lower = name.lower()
    desc_lower = desc.lower()
    combined = name_lower + ' ' + desc_lower

    # Priority 1: match in name (higher signal)
    for keyword, category, use_case in USE_CASE_PATTERNS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', name_lower):
            return category, use_case

    # Priority 2: match in combined name+description
    for keyword, category, use_case in USE_CASE_PATTERNS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', combined):
            return category, use_case

    return 'General', f'Use for tasks involving {name.replace("-", " ")} (see description).'


# ── Markdown generation ───────────────────────────────────────────────

def generate_catalog(all_skills: list[dict], output_path: str):
    lines = []

    # Header
    lines.append("# Claude Code Skills Catalog\n")
    lines.append(f"**Total skills:** {len(all_skills)}  ")
    lines.append(f"**Generated:** 2026-05-20  ")
    lines.append(f"**Source:** `~/.claude/skills/`\n")
    lines.append("> **Legend:** 🤖 = AI-inferred trigger/use case. Review before relying.\n")

    # Summary by source
    lines.append("## Overview by Source\n")
    lines.append("| Source | Skills | Description |")
    lines.append("|--------|--------|-------------|")

    source_stats = {}
    for s in all_skills:
        src = _get_source_group(s['rel_dir'], s.get('plugin'), s['fm'].get('name', ''))
        source_stats[src] = source_stats.get(src, 0) + 1

    for src in sorted(source_stats.keys(), key=lambda x: source_stats[x], reverse=True):
        count = source_stats[src]
        desc = SOURCE_DESCRIPTIONS.get(src, 'Other')
        lines.append(f"| {src} | {count} | {desc} |")
    lines.append("")

    # Table of Contents
    lines.append("## Table of Contents\n")
    for src in sorted(source_stats.keys(), key=lambda x: source_stats[x], reverse=True):
        count = source_stats[src]
        anchor = re.sub(r'[^a-z0-9-]', '', src.lower().replace(' ', '-').replace('/', '-'))
        lines.append(f"- [{src}](#{anchor}) ({count} skills)")
    lines.append("")

    # Skill entries by source
    skills_by_source = {}
    for s in all_skills:
        src = _get_source_group(s['rel_dir'], s.get('plugin'), s['fm'].get('name', ''))
        skills_by_source.setdefault(src, []).append(s)

    for src in sorted(skills_by_source.keys(), key=lambda x: source_stats.get(x, 0), reverse=True):
        group_skills = skills_by_source[src]
        anchor = re.sub(r'[^a-z0-9-]', '', src.lower().replace(' ', '-').replace('/', '-'))
        lines.append(f"## {src} {{{{{anchor}}}}}\n")

        sample_plugin = group_skills[0].get('plugin')
        if sample_plugin:
            lines.append(f"**Version:** {sample_plugin.get('version', '?')}  ")
            author = sample_plugin.get('author', {})
            if isinstance(author, dict) and author.get('name'):
                lines.append(f"**Author:** {author['name']}  ")
            if sample_plugin.get('repository'):
                lines.append(f"**Repo:** <{sample_plugin['repository']}>  ")
            lines.append("")

        if len(group_skills) > 50:
            lines.append(f"> {len(group_skills)} skills — use Ctrl+F to search.\n")

        group_skills.sort(key=lambda x: x['fm'].get('name', 'zzz'))

        for idx, s in enumerate(group_skills):
            fm = s['fm']
            name = fm.get('name', 'unknown')
            desc = fm.get('description', 'No description.')
            if isinstance(desc, list):
                desc = ' '.join(str(d) for d in desc)
            desc = str(desc).strip()

            category, use_case = infer_use_case(name, desc, fm.get('triggers'))

            version = fm.get('version', '')
            if not version and isinstance(fm.get('metadata'), dict):
                version = fm.get('metadata', {}).get('version', '')
            related = []
            if isinstance(fm.get('metadata'), dict):
                related = fm.get('metadata', {}).get('related_skills', [])

            lines.append(f"### {name}\n")
            lines.append(f"**Category:** {category} | **Path:** `{s['rel_dir']}/`\n")
            lines.append(f"**Description:** {desc}\n")

            if version:
                lines.append(f"**Version:** {version}  ")

            triggers = fm.get('triggers')
            if triggers and isinstance(triggers, dict):
                lines.append("**Trigger Words 🤖:**\n")
                primary = triggers.get('primary_intent', '')
                examples = triggers.get('examples', [])
                if primary:
                    lines.append(f"- Primary: {primary}")
                if examples:
                    for ex in (examples if isinstance(examples, list) else [examples]):
                        lines.append(f"- `{ex}`")
            else:
                lines.append(f"**Trigger Words 🤖:** When user mentions `{name}` or related concepts")
            lines.append("")
            lines.append(f"**Use Case 🤖:** {use_case}\n")

            if related:
                links = ', '.join(f'`{r}`' for r in related)
                lines.append(f"**Related:** {links}\n")

            if idx < len(group_skills) - 1:
                lines.append("---\n")
            else:
                lines.append("")

    # ── Appendix ──
    lines.append("---\n")
    lines.append("## Appendix\n")

    # A. How skills are triggered
    lines.append("### A. How Claude Code Skills Are Triggered\n")
    lines.append("Skills in Claude Code use **progressive disclosure**. The system loads skill metadata")
    lines.append("(name + description) at session start, then loads the full SKILL.md only when relevant.")
    lines.append("A skill activates when:\n")
    lines.append("1. **Name match:** Your prompt mentions the skill name or key terms from its description")
    lines.append("2. **Intent match:** Your request aligns with the skill's `primary_intent` or trigger examples")
    lines.append("3. **Explicit invoke:** You type `/<skill-name>` or use the Skill tool\n")
    lines.append("| Trigger Method | Example | When It Works |")
    lines.append("|---------------|---------|---------------|")
    lines.append('| Keyword in prompt | "润色这段英文" | `ppw:polish`, `nature-polishing` activate |')
    lines.append('| Intent match | "帮我写论文" | `academic-paper` pipeline activates |')
    lines.append('| Slash command | `/brainstorming` | Any skill with a slash command |')
    lines.append('| Skill tool | Skill("brainstorming") | Any registered skill |')
    lines.append("")

    # B. Common workflows
    lines.append("### B. Common Skill Workflows\n")
    lines.append("#### Academic Paper Writing (完整论文工作流)\n")
    lines.append("```\n")
    lines.append("brainstorming → academic-paper → ppw:polish → ppw:reviewer-simulation")
    lines.append("    → ppw:de-ai → nature-polishing → ppw:cover-letter → ppw:translation\n")
    lines.append("```\n")
    lines.append("#### Code Development (代码开发工作流)\n")
    lines.append("```\n")
    lines.append("brainstorming → writing-plans → test-driven-development")
    lines.append("    → requesting-code-review → receiving-code-review → verification-before-completion\n")
    lines.append("```\n")
    lines.append("#### Weekly Report (每周报告自动化)\n")
    lines.append("```\n")
    lines.append("weekly-github-trending → humanizer-zh → lark-doc (publish)\n")
    lines.append("```\n")
    lines.append("#### Debugging (调试工作流)\n")
    lines.append("```\n")
    lines.append("systematic-debugging → verification-before-completion\n")
    lines.append("```\n")

    # C. Installation guide
    lines.append("### C. How to Install These Skills\n")
    lines.append("#### Plugin-based skills (ECC, Hermes, Nature, Academic)\n")
    lines.append("```bash\n")
    lines.append("# Install from marketplace")
    lines.append("/plugin marketplace add affaan-m/everything-claude-code")
    lines.append("/plugin install everything-claude-code@everything-claude-code\n")
    lines.append("# Or manual clone")
    lines.append("git clone <repo-url> ~/.claude/skills/<skill-name>")
    lines.append("```\n")
    lines.append("#### Individual skills (Lark, Superpowers, Custom)\n")
    lines.append("```bash\n")
    lines.append("# Copy to skills directory")
    lines.append("cp -r <skill-dir> ~/.claude/skills/<skill-name>")
    lines.append("# Or symlink for development")
    lines.append("ln -s /path/to/skill ~/.claude/skills/<skill-name>")
    lines.append("```\n")

    # D. Cross-source comparison
    lines.append("### D. Source Comparison: When to Use Which\n")
    lines.append("| Source | Best For | Scope | Maintenance |")
    lines.append("|--------|----------|-------|-------------|")
    lines.append("| **everything-claude-code** | General development, full-stack, DevOps | 234 skills | Community (140K+ stars), very active |")
    lines.append("| **hermes-agent** | AI agent learning, memory, automation | 164 skills | Community (143K+ stars), active |")
    lines.append("| **Lark Integration** | Feishu/Lark API operations | 22 skills | Personal/team maintained |")
    lines.append("| **Superpowers Workflow** | Process discipline (plan, TDD, review) | 19 skills | Built-in, core to Claude Code |")
    lines.append("| **Custom Skills** | Niche academic/research needs | 2 skills | Self-maintained |")
    lines.append("")

    # E. Maintenance
    lines.append("### E. Maintenance Guide\n")
    lines.append("- **Update skills:** Re-run plugin install or `git pull` in skill directories")
    lines.append("- **Regenerate catalog:** `python generate_catalog.py`")
    lines.append("- **Add new skills:** Install to `~/.claude/skills/`, then regenerate")
    lines.append("- **Remove skills:** Delete from `~/.claude/skills/`, then regenerate")
    lines.append("- **Version tracking:** Plugin-based skills auto-track versions via `plugin.json`\n")

    # F. Source repos
    lines.append("### F. Source Repositories\n")
    lines.append("- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) — 140K+ stars, MIT license")
    lines.append("- [hermes-agent](https://github.com/NousResearch/hermes-agent) — 143K+ stars")
    lines.append("- [academic-research-skills](https://github.com/Imbad0202/academic-research-skills)")
    lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Catalog written to {output_path} ({len(all_skills)} skills)")


# ── Main ──────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate Claude Code Skills Catalog')
    parser.add_argument('--output', default='SKILLS_CATALOG.md', help='Output markdown file')
    parser.add_argument('--root', default=SKILLS_ROOT, help='Skills directory root')
    args = parser.parse_args()

    raw_files = find_skill_files(args.root)
    print(f"Found {len(raw_files)} SKILL.md files")

    skill_files = [s for s in raw_files if not _should_skip(s['rel_dir'])]
    print(f"After filtering translations: {len(skill_files)}")

    for s in skill_files:
        try:
            with open(s['path'], 'r', encoding='utf-8') as f:
                s['fm'] = parse_frontmatter(f.read())
        except Exception as e:
            s['fm'] = {'name': os.path.basename(s['rel_dir']),
                       'description': f'[Parse error: {e}]'}

    valid = [s for s in skill_files if s['fm'].get('name')]

    seen = set()
    unique = []
    for s in valid:
        name = s['fm'].get('name', '')
        if name not in seen:
            seen.add(name)
            unique.append(s)
    print(f"After dedup: {len(unique)} unique skills")

    generate_catalog(unique, args.output)


if __name__ == '__main__':
    main()
