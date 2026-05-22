from lanes_ceo.contracts import Artifact, CriticReview, NotificationEvent, TaskRequest
from lanes_ceo.enums import JobStatus, NotificationType, SourceChannel


def test_task_request_keeps_ingress_context() -> None:
    request = TaskRequest(
        request_id="req-1",
        source_channel=SourceChannel.FEISHU,
        sender="lane",
        raw_message="summarize this",
        task_intent="briefing",
        priority="normal",
        attachments=["doc://draft"],
        authorization_context={"trusted_sender": True},
    )

    assert request.source_channel is SourceChannel.FEISHU
    assert request.authorization_context["trusted_sender"] is True


def test_review_and_notification_contracts_capture_gate_result() -> None:
    artifact = Artifact(
        artifact_id="art-1",
        job_id="job-1",
        artifact_type="summary",
        summary="draft result",
        artifact_paths=[],
        sources=["fake"],
        risks=[],
        user_confirmations=[],
    )
    review = CriticReview(
        review_id="review-1",
        job_id="job-1",
        review_result="approved",
        score=96,
        issues=[],
        approved=True,
        return_to_actor=False,
        handoff_note="ready",
    )
    notification = NotificationEvent(
        notification_id="note-1",
        job_id="job-1",
        target_channel=SourceChannel.FEISHU,
        target_recipient="secretary-group",
        message_type=NotificationType.JOB_COMPLETED,
        payload={"artifact_id": artifact.artifact_id},
        receipt_required=False,
        retry_policy="default",
    )

    assert review.score == 96
    assert notification.message_type is NotificationType.JOB_COMPLETED
    assert JobStatus.APPROVED.value == "approved"
