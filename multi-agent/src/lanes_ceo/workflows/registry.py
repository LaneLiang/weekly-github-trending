from lanes_ceo.workflows.base import Workflow
from lanes_ceo.workflows.briefings import AINewsWorkflow, GitHubTrendingWorkflow
from lanes_ceo.workflows.claude_task import ClaudeTaskWorkflow
from lanes_ceo.workflows.daily_loop import DailyReportWorkflow, ReflectionWorkflow
from lanes_ceo.workflows.fake import FakeWorkflow
from lanes_ceo.workflows.literature_survey import LiteratureSurveyWorkflow
from lanes_ceo.workflows.mail_digest import MailDigestWorkflow
from lanes_ceo.workflows.memory_curation import MemoryCurationWorkflow
from lanes_ceo.workflows.paper_research import PaperResearchWorkflow
from lanes_ceo.workflows.paper_writing import PaperWritingWorkflow
from lanes_ceo.workflows.presentation import PresentationWorkflow
from lanes_ceo.workflows.update_checker import UpdateCheckerWorkflow
from lanes_ceo.workflows.manuscript_tracker import ManuscriptTrackerWorkflow
from lanes_ceo.workflows.eda_testbench import EDATestbenchWorkflow
from lanes_ceo.workflows.deepseek_monitor import DeepSeekMonitorWorkflow
from lanes_ceo.workflows.simulation_data_pipeline import SimulationDataPipelineWorkflow
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
            ClaudeTaskWorkflow(),
            UpdateCheckerWorkflow(),
            MemoryCurationWorkflow(),
            LiteratureSurveyWorkflow(),
            ManuscriptTrackerWorkflow(),
            SimulationDataPipelineWorkflow(),
            EDATestbenchWorkflow(),
            DeepSeekMonitorWorkflow(),
        ]:
            self._workflows[wf.role_group] = wf

    def get(self, role_group: str) -> Workflow:
        try:
            return self._workflows[role_group]
        except KeyError as exc:
            raise KeyError(f"unknown role group: {role_group}") from exc

    def register(self, role_group: str, workflow: Workflow) -> None:
        """Register (or override) a workflow under a role group key."""
        self._workflows[role_group] = workflow
