from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.mail_digest import MailDigestWorkflow, PAPER_KEYWORDS


def test_mail_digest_actor_produces_artifact() -> None:
    wf = MailDigestWorkflow()
    job = Job(
        job_id="job-mail",
        request_id="req-1",
        role_group="mail_digest",
        actor="mail-digest-actor",
        critic="mail-digest-critic",
        status=JobStatus.RECEIVED,
        input={"message": "today"},
        workspace="runtime/jobs/test",
    )
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "mail_digest"
    assert len(artifact.user_confirmations) >= 1
    assert len(artifact.sources) >= 1


def test_mail_digest_critic_approves_rich_digest() -> None:
    wf = MailDigestWorkflow()
    job = Job(
        job_id="job-mail2",
        request_id="req-2",
        role_group="mail_digest",
        actor="mail-digest-actor",
        critic="mail-digest-critic",
        status=JobStatus.RECEIVED,
        input={"message": "today"},
        workspace="runtime/jobs/test",
    )
    artifact = Artifact(
        artifact_id="art-md",
        job_id=job.job_id,
        artifact_type="mail_digest",
        summary="今日邮件摘要（3封）：1) 导师张教授发来下周组会时间调整通知 2) 论文合作者发来修改意见 3) 学院通知下周五提交中期考核材料",
        artifact_paths=[],
        sources=["mail-inbox"],
        risks=[],
        user_confirmations=["是否有需要额外关注的紧急邮件"],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True


def test_mail_digest_critic_rejects_empty() -> None:
    wf = MailDigestWorkflow()
    job = Job(
        job_id="job-mail3",
        request_id="req-3",
        role_group="mail_digest",
        actor="mail-digest-actor",
        critic="mail-digest-critic",
        status=JobStatus.RECEIVED,
        input={"message": "today"},
        workspace="runtime/jobs/test",
    )
    artifact = Artifact(
        artifact_id="art-md2",
        job_id=job.job_id,
        artifact_type="mail_digest",
        summary="no mail",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_should_keep_unread_for_paper_emails() -> None:
    assert MailDigestWorkflow.should_keep_unread(
        "Decision on your manuscript #12345"
    )
    assert MailDigestWorkflow.should_keep_unread(
        "Minor revision required for your submission"
    )
    assert MailDigestWorkflow.should_keep_unread(
        "Your paper has been accepted"
    )


def test_should_not_keep_unread_for_regular_emails() -> None:
    assert not MailDigestWorkflow.should_keep_unread("Team lunch tomorrow")
    assert not MailDigestWorkflow.should_keep_unread("Weekly newsletter")
    assert not MailDigestWorkflow.should_keep_unread("Meeting reminder")


def test_paper_keywords_cover_decision_emails() -> None:
    assert "accept" in PAPER_KEYWORDS
    assert "reject" in PAPER_KEYWORDS
    assert "decision" in PAPER_KEYWORDS
    assert "revision" in PAPER_KEYWORDS
