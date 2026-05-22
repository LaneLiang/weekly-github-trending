from lanes_ceo.subagent.base import SubAgent
from lanes_ceo.subagent.manager import SubAgentManager
from lanes_ceo.workflows.registry import WorkflowRegistry


def test_manager_spawn_returns_subagent() -> None:
    registry = WorkflowRegistry()
    manager = SubAgentManager(registry)
    agent = manager.spawn("fake", "actor")
    assert agent.agent_id.startswith("fake-actor-")
    assert agent.agent_type == "actor"
    assert agent.role_group == "fake"


def test_manager_spawn_critic() -> None:
    registry = WorkflowRegistry()
    manager = SubAgentManager(registry)
    agent = manager.spawn("fake", "critic")
    assert agent.agent_type == "critic"


def test_manager_list_agents() -> None:
    registry = WorkflowRegistry()
    manager = SubAgentManager(registry)
    manager.spawn("fake", "actor")
    manager.spawn("fake", "critic")
    assert len(manager.list_agents()) == 2


def test_manager_get_agent() -> None:
    registry = WorkflowRegistry()
    manager = SubAgentManager(registry)
    agent = manager.spawn("fake", "actor")
    assert manager.get_agent(agent.agent_id) is agent


def test_manager_get_unknown_agent_returns_none() -> None:
    registry = WorkflowRegistry()
    manager = SubAgentManager(registry)
    assert manager.get_agent("nonexistent") is None


def test_manager_remove_agent() -> None:
    registry = WorkflowRegistry()
    manager = SubAgentManager(registry)
    agent = manager.spawn("fake", "actor")
    manager.remove_agent(agent.agent_id)
    assert manager.get_agent(agent.agent_id) is None


def test_actor_runs_and_returns_artifact() -> None:
    registry = WorkflowRegistry()
    manager = SubAgentManager(registry)
    from lanes_ceo.contracts import Job
    from lanes_ceo.enums import JobStatus

    job = Job(
        job_id="job-test",
        request_id="req-test",
        role_group="fake",
        actor="fake-actor",
        critic="fake-critic",
        status=JobStatus.RECEIVED,
        input={"message": "hello"},
        workspace="runtime/test",
    )
    agent = manager.spawn("fake", "actor")
    artifact = agent.run(job, {})
    assert artifact.artifact_type == "summary"
    assert artifact.job_id == "job-test"


def test_critic_runs_and_returns_review() -> None:
    registry = WorkflowRegistry()
    manager = SubAgentManager(registry)
    from lanes_ceo.contracts import Artifact, Job
    from lanes_ceo.enums import JobStatus

    job = Job(
        job_id="job-test2",
        request_id="req-test2",
        role_group="fake",
        actor="fake-actor",
        critic="fake-critic",
        status=JobStatus.WAITING_REVIEW,
        input={"message": "hello"},
        workspace="runtime/test",
    )
    artifact = Artifact(
        artifact_id="art-1",
        job_id="job-test2",
        artifact_type="fake",
        summary="test",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    agent = manager.spawn("fake", "critic")
    review = agent.run(job, {"artifact": artifact})
    assert review.approved is True


def test_critic_missing_artifact_raises() -> None:
    registry = WorkflowRegistry()
    manager = SubAgentManager(registry)
    from lanes_ceo.contracts import Job
    from lanes_ceo.enums import JobStatus

    job = Job(
        job_id="job-test3",
        request_id="req-test3",
        role_group="fake",
        actor="fake-actor",
        critic="fake-critic",
        status=JobStatus.WAITING_REVIEW,
        input={"message": "hello"},
        workspace="runtime/test",
    )
    agent = manager.spawn("fake", "critic")
    try:
        agent.run(job, {})
        assert False, "should have raised"
    except ValueError as e:
        assert "artifact" in str(e)
