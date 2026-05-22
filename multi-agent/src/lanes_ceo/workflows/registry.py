from lanes_ceo.workflows.base import Workflow
from lanes_ceo.workflows.briefings import AINewsWorkflow, GitHubTrendingWorkflow
from lanes_ceo.workflows.daily_loop import DailyReportWorkflow, ReflectionWorkflow
from lanes_ceo.workflows.fake import FakeWorkflow


class WorkflowRegistry:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}
        for wf in [
            FakeWorkflow(),
            GitHubTrendingWorkflow(),
            AINewsWorkflow(),
            DailyReportWorkflow(),
            ReflectionWorkflow(),
        ]:
            self._workflows[wf.role_group] = wf

    def get(self, role_group: str) -> Workflow:
        try:
            return self._workflows[role_group]
        except KeyError as exc:
            raise KeyError(f"unknown role group: {role_group}") from exc
