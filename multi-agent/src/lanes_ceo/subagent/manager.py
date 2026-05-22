from uuid import uuid4

from lanes_ceo.subagent.base import SubAgent
from lanes_ceo.workflows.base import Workflow
from lanes_ceo.workflows.registry import WorkflowRegistry


class _AgentWrapper:
    """Wraps a single role (actor or critic) of a Workflow as a SubAgent."""

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        role_group: str,
        workflow: Workflow,
    ) -> None:
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.role_group = role_group
        self._workflow = workflow

    def run(self, job, context):
        if self.agent_type == "actor":
            return self._workflow.run_actor(job)
        else:
            artifact = context.get("artifact")
            if artifact is None:
                raise ValueError("critic sub-agent requires 'artifact' in context")
            return self._workflow.run_critic(job, artifact)


class SubAgentManager:
    def __init__(self, registry: WorkflowRegistry) -> None:
        self._registry = registry
        self._agents: dict[str, SubAgent] = {}

    def spawn(self, role_group: str, agent_type: str) -> SubAgent:
        workflow = self._registry.get(role_group)
        agent_id = f"{role_group}-{agent_type}-{uuid4().hex[:8]}"
        agent = _AgentWrapper(agent_id, agent_type, role_group, workflow)
        self._agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> SubAgent | None:
        return self._agents.get(agent_id)

    def list_agents(self) -> list[SubAgent]:
        return list(self._agents.values())

    def remove_agent(self, agent_id: str) -> None:
        self._agents.pop(agent_id, None)
