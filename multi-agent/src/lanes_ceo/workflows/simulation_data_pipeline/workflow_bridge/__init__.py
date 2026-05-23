"""Workflow bridges connecting simulation pipeline to downstream consumers."""

from .paper_research import PaperResearchBridge
from .weekly_report import WeeklyReportBridge

__all__ = ["PaperResearchBridge", "WeeklyReportBridge"]
