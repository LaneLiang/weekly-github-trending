from lanes_ceo.contracts import Job
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
    assert len(artifact.user_confirmations) >= 2


def test_mail_digest_critic_approves() -> None:
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
    review = wf.run_critic(job, artifact)
    assert review.approved is True


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
