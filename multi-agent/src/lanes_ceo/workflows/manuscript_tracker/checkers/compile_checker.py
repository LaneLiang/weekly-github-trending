"""CompileChecker — compile LaTeX project with latexmk and parse log for errors/warnings."""

from __future__ import annotations

import logging
import re
import subprocess
import shutil
from pathlib import Path

from lanes_ceo.workflows.manuscript_tracker.checkers.base import BaseChecker, CheckItem, CheckResult
from lanes_ceo.workflows.manuscript_tracker.config import DEFAULT_CONFIG

logger = logging.getLogger("lanes_ceo.manuscript_tracker.compile")


class CompileChecker(BaseChecker):
    """Check that the LaTeX project compiles without errors.

    Uses latexmk for compilation, then parses the .log file for errors,
    warnings, and overfull hbox issues.
    """

    name = "compile"

    def check(self, project: "LaTeXProject", profile: "JournalProfile") -> CheckResult:  # noqa: F821
        # Tool check
        if shutil.which("latexmk") is None:
            return self._skip("latexmk not found in PATH")

        config = DEFAULT_CONFIG
        main_tex = project.main_tex
        project_dir = project.project_dir

        # Run latexmk in the project directory
        timeout = config.compile_timeout_seconds
        cmd = [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-silent",
            str(main_tex.name),
        ]

        logger.info("Compiling %s with latexmk...", main_tex.name)
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(project_dir),
            )
        except subprocess.TimeoutExpired:
            return self._fail(
                items=[CheckItem(
                    code="COMPILE_TIMEOUT",
                    description=f"latexmk 编译超时 (>{timeout}s)",
                    status="fail",
                    detail=f"编译超过 {timeout} 秒未完成，请检查 LaTeX 源码是否有死循环或巨量内容",
                    fix_suggestion="检查 \\usepackage 列表是否包含互相冲突的包，或使用 draft 模式分别编译各章节定位问题",
                )],
                summary=f"编译超时 (>{timeout}s)",
                fix_suggestions=["检查是否有循环引用或过大的表格"],
            )
        except FileNotFoundError:
            return self._skip("latexmk not found")

        returncode = proc.returncode

        # Parse .log file
        log_file = project_dir / f"{main_tex.stem}.log"
        log_errors: list[dict] = []
        log_warnings: list[dict] = []
        overfull_hbox: list[dict] = []

        if log_file.exists():
            log_text = log_file.read_text(encoding="utf-8", errors="replace")
            log_errors = self._parse_errors(log_text)
            log_warnings = self._parse_warnings(log_text)
            overfull_hbox = self._parse_overfull(log_text)
        elif returncode != 0:
            # No log file but compilation failed
            return self._fail(
                items=[CheckItem(
                    code="COMPILE_NO_LOG",
                    description="编译失败但未生成 .log 文件",
                    status="fail",
                    detail=f"latexmk 返回码: {returncode}\nstdout: {proc.stdout[:1000]}",
                    fix_suggestion="检查 latexmk 是否正确安装，或项目路径是否可写",
                )],
                summary="编译失败，无日志文件",
            )

        # Build check items
        items: list[CheckItem] = []

        for err in log_errors:
            items.append(CheckItem(
                code="COMPILE_ERROR",
                description=f"LaTeX 编译错误: {err.get('line', '?')}行 — {err.get('message', 'Unknown')}",
                status="fail",
                detail=f"Line {err.get('line', '?')}: {err.get('message', '')}",
                fix_suggestion=err.get('suggestion', '请根据 LaTeX 错误信息修改源码'),
            ))

        for warn in log_warnings:
            items.append(CheckItem(
                code="COMPILE_WARN",
                description=f"LaTeX 警告: {warn.get('message', '')[:120]}",
                status="warn",
                detail=warn.get('message', ''),
                fix_suggestion="一般不影响编译，但建议在投稿前解决所有警告",
            ))

        for oh in overfull_hbox:
            items.append(CheckItem(
                code="COMPILE_OVERFULL",
                description=f"Overfull hbox: {oh.get('line', '?')}行, 超出 {oh.get('amount', '?')}pt",
                status="warn",
                detail=f"Line {oh.get('line', '?')}: overfull by {oh.get('amount', '?')}pt",
                fix_suggestion="调整断词或重新排版该行，避免文字超出页面边界",
            ))

        # Determine overall status
        if returncode != 0 or any(e.get("level") == "error" for e in log_errors):
            status = "fail"
            summary = f"编译失败: {len(log_errors)} 错误, {len(log_warnings)} 警告, {len(overfull_hbox)} overfull"
        elif log_warnings or overfull_hbox:
            status = "warn"
            summary = f"编译通过但有 {len(log_warnings)} 警告, {len(overfull_hbox)} overfull"
        else:
            status = "pass"
            summary = "编译通过，无错误、无警告"

        return CheckResult(
            checker_name=self.name,
            status=status,
            items=items,
            summary=summary,
            fix_suggestions=[],  # Individual items carry their own suggestions
        )

    # ── log parsing ──

    def _parse_errors(self, log_text: str) -> list[dict]:
        """Parse LaTeX error messages from .log file."""
        errors: list[dict] = []

        # Pattern for standard LaTeX errors: "! Error message"
        error_blocks = re.split(r'(?=^!)', log_text, flags=re.MULTILINE)
        for block in error_blocks:
            if not block.startswith("!"):
                continue

            lines = block.strip().split("\n")
            first_line = lines[0]
            # Remove leading "! "
            message = first_line[2:].strip() if first_line.startswith("! ") else first_line

            # Try to find line number
            line_no = "?"
            for ln in lines:
                m = re.match(r'l\.(\d+)', ln.strip())
                if m:
                    line_no = m.group(1)
                    break

            suggestion = self._suggest_fix(message)

            errors.append({
                "level": "error",
                "message": message,
                "line": line_no,
                "suggestion": suggestion,
            })

        return errors

    def _parse_warnings(self, log_text: str) -> list[dict]:
        """Parse LaTeX warnings from .log file."""
        warnings: list[dict] = []

        # LaTeX Warning: ... on input line N
        pattern = r'LaTeX Warning:\s*(.+?)(?:\s*on input line\s*(\d+))?'
        for match in re.finditer(pattern, log_text):
            warnings.append({
                "level": "warning",
                "message": match.group(1).strip(),
                "line": match.group(2) or "?",
            })

        # Package ... Warning: ...
        pkg_pattern = r'(?:Package|Class)\s+(\S+)\s+Warning:\s*(.+?)(?:\s*on input line\s*(\d+))?'
        for match in re.finditer(pkg_pattern, log_text):
            warnings.append({
                "level": "warning",
                "message": f"[{match.group(1)}] {match.group(2).strip()}",
                "line": match.group(3) or "?",
            })

        return warnings

    def _parse_overfull(self, log_text: str) -> list[dict]:
        """Parse overfull/underfull hbox/vbox messages."""
        overfull: list[dict] = []

        pattern = r'(Overfull|Underfull)\s+\\[hv]box\s+\(([^)]+)\)'
        line_pattern = r'at lines?\s+(\d+--\d+)'

        for block in re.split(r'\n{2,}', log_text):
            m = re.search(pattern, block)
            if not m:
                continue
            kind = m.group(1)
            amount = m.group(2)

            line_match = re.search(line_pattern, block)
            line_no = line_match.group(1) if line_match else "?"

            overfull.append({
                "kind": kind,
                "line": line_no,
                "amount": amount,
            })

        return overfull

    def _suggest_fix(self, error_msg: str) -> str:
        """Generate fix suggestion based on error message pattern."""
        msg_lower = error_msg.lower()

        if "undefined control sequence" in msg_lower:
            return "检查是否拼错了命令名，或遗漏了 \\usepackage{...}"
        if "missing \\begin" in msg_lower or "missing \\end" in msg_lower:
            return "检查 \\begin 和 \\end 是否匹配"
        if "file" in msg_lower and "not found" in msg_lower:
            return "检查图片或外部文件路径是否正确"
        if "missing $" in msg_lower or "math" in msg_lower:
            return "数学环境内缺少 $ 符号"
        if "missing \\right" in msg_lower or "missing \\left" in msg_lower:
            return "\\left 和 \\right 必须配对使用"
        if "extra }" in msg_lower or "missing }" in msg_lower:
            return "大括号不匹配，检查 {} 对应关系"

        return "查阅 LaTeX 错误信息定位并修复问题"
