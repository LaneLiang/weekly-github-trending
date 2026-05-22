from lanes_ceo.workflows.base import Workflow
from lanes_ceo.workflows.briefings import AINewsWorkflow, GitHubTrendingWorkflow
from lanes_ceo.workflows.daily_loop import DailyReportWorkflow, ReflectionWorkflow
from lanes_ceo.workflows.fake import FakeWorkflow
from lanes_ceo.workflows.mail_digest import MailDigestWorkflow
from lanes_ceo.workflows.paper_research import PaperResearchWorkflow
from lanes_ceo.workflows.paper_writing import PaperWritingWorkflow
from lanes_ceo.workflows.presentation import PresentationWorkflow
from lanes_ceo.workflows.weekly_report import WeeklyReportWorkflow


class WorkflowRegistry:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}
        for wf in [
            FakeWorkflow(),
            GitHubTrendingWorkflow(),
            AINewsWorkflow(),
            DailyReportWorkflow(),
            ReflectionWorkflow(),
            PaperResearchWorkflow(),
            PaperWritingWorkflow(),
            MailDigestWorkflow(),
            WeeklyReportWorkflow(),
            PresentationWorkflow(),
        ]:
            self._workflows[wf.role_group] = wf

    def get(self, role_group: str) -> Workflow:
        try:
            return self._workflows[role_group]
        except KeyError as exc:
            raise KeyError(f"unknown role group: {role_group}") from exc
