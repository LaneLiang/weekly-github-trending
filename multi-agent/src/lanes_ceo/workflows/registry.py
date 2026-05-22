from lanes_ceo.workflows.base import Workflow
from lanes_ceo.workflows.fake import FakeWorkflow


class WorkflowRegistry:
    def __init__(self) -> None:
        fake = FakeWorkflow()
        self._workflows: dict[str, Workflow] = {fake.role_group: fake}

    def get(self, role_group: str) -> Workflow:
        try:
            return self._workflows[role_group]
        except KeyError as exc:
            raise KeyError(f"unknown role group: {role_group}") from exc
