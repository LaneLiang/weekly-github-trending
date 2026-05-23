"""Base classes for manuscript checker plugin architecture."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class CheckItem:
    """Single atomic check item result."""

    code: str  # e.g. "COMPILE_001"
    description: str  # Chinese description
    status: Literal["pass", "fail", "warn", "skip"]
    detail: str = ""
    fix_suggestion: str = ""


@dataclass
class CheckResult:
    """Aggregated result from a single checker."""

    checker_name: str
    status: Literal["pass", "fail", "warn", "skip"]
    items: list[CheckItem] = field(default_factory=list)
    summary: str = ""
    fix_suggestions: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status == "pass"

    @property
    def failed(self) -> bool:
        return self.status == "fail"


class BaseChecker(ABC):
    """Abstract base for all manuscript checkers.

    Each checker operates on a LaTeXProject and JournalProfile,
    returning a CheckResult. Checkers should never raise exceptions
    to the engine -- they should catch and report errors via CheckResult.
    """

    name: str = "base"

    @abstractmethod
    def check(self, project: "LaTeXProject", profile: "JournalProfile") -> CheckResult:  # noqa: F821
        ...

    def _pass(self, items: list[CheckItem] | None = None, summary: str = "") -> CheckResult:
        return CheckResult(
            checker_name=self.name,
            status="pass",
            items=items or [],
            summary=summary,
        )

    def _fail(self, items: list[CheckItem] | None = None, summary: str = "",
              fix_suggestions: list[str] | None = None) -> CheckResult:
        return CheckResult(
            checker_name=self.name,
            status="fail",
            items=items or [],
            summary=summary,
            fix_suggestions=fix_suggestions or [],
        )

    def _warn(self, items: list[CheckItem] | None = None, summary: str = "",
              fix_suggestions: list[str] | None = None) -> CheckResult:
        return CheckResult(
            checker_name=self.name,
            status="warn",
            items=items or [],
            summary=summary,
            fix_suggestions=fix_suggestions or [],
        )

    def _skip(self, reason: str = "") -> CheckResult:
        return CheckResult(
            checker_name=self.name,
            status="skip",
            items=[CheckItem(
                code=f"{self.name.upper()}_SKIP",
                description=f"跳过{self.name}检查",
                status="skip",
                detail=reason,
            )],
            summary=f"跳过: {reason}" if reason else "跳过",
        )
