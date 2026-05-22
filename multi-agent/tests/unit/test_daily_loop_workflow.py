from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.daily_loop import DailyReportWorkflow, ReflectionWorkflow


def _make_job(role_group: str) -> Job:
    return Job(
        job_id=f"job-{role_group}",
        request_id="req-1",
        role_group=role_group,
        actor=f"{role_group}-actor",
        critic=f"{role_group}-critic",
        status=JobStatus.RECEIVED,
        input={"message": "今日工作"},
        workspace="runtime/jobs/test",
    )


def test_daily_report_actor_requests_user_confirmation() -> None:
    wf = DailyReportWorkflow()
    job = _make_job("daily_report")
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "daily_report"
    assert len(artifact.user_confirmations) > 0


def test_daily_report_critic_approves_rich_report() -> None:
    wf = DailyReportWorkflow()
    job = _make_job("daily_report")
    artifact = Artifact(
        artifact_id="art-dr",
        job_id=job.job_id,
        artifact_type="daily_report",
        summary="今日工作总结：完成了3组对照实验并分析了数据，完成了论文引言部分的初稿撰写，参加了组会并记录反馈意见。明日计划继续实验并整理图表。",
        artifact_paths=[],
        sources=["user-conversation"],
        risks=[],
        user_confirmations=["请确认今日工作内容是否完整"],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True
    assert review.score >= 80


def test_daily_report_critic_rejects_short_report() -> None:
    wf = DailyReportWorkflow()
    job = _make_job("daily_report")
    artifact = Artifact(
        artifact_id="art-dr2",
        job_id=job.job_id,
        artifact_type="daily_report",
        summary="完成了工作",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_reflection_actor_requests_user_confirmation() -> None:
    wf = ReflectionWorkflow()
    job = _make_job("reflection")
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "reflection"
    assert len(artifact.user_confirmations) > 0


def test_reflection_critic_approves_rich_reflection() -> None:
    wf = ReflectionWorkflow()
    job = _make_job("reflection")
    artifact = Artifact(
        artifact_id="art-re",
        job_id=job.job_id,
        artifact_type="reflection",
        summary="今日反思：最大的收获是通过对照实验发现方案A比方案B效果好15%，也意识到自己对统计显著性检验的方法不够熟练。做得不够好的地方是上午花了太多时间在调参而不是集中精力写论文。明天要早起到实验室先完成论文部分的修改再开始实验。",
        artifact_paths=[],
        sources=["user-conversation"],
        risks=[],
        user_confirmations=["反思内容是否需要调整方向"],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True


def test_reflection_critic_rejects_short_reflection() -> None:
    wf = ReflectionWorkflow()
    job = _make_job("reflection")
    artifact = Artifact(
        artifact_id="art-re2",
        job_id=job.job_id,
        artifact_type="reflection",
        summary="今天表现不错",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False
