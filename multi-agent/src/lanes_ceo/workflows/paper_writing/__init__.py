from lanes_ceo.contracts import Artifact, CriticReview, Job


class PaperWritingWorkflow:
    role_group = "paper_writing"
    actor_name = "paper-writing-actor"
    critic_name = "paper-writing-critic"
    # Paper writing group is exempt from monthly elimination scoring per V1 spec
    exempt_from_elimination = True

    def run_actor(self, job: Job) -> Artifact:
        section = job.input.get("message", "draft section")
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="paper_draft",
            summary=f"paper draft section: {section}",
            artifact_paths=[
                "drafts/current/",
                "figures/",
                "references.bib",
            ],
            sources=["literature-review", "experiment-data"],
            risks=[
                "factual accuracy requires author verification",
                "figure placement may need adjustment",
            ],
            user_confirmations=[
                "请确认技术内容准确性",
                "图表数据和格式是否需要调整",
            ],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues = []
        if artifact.artifact_type != "paper_draft":
            issues.append("wrong artifact type")
        if len(artifact.user_confirmations) < 2:
            issues.append("insufficient author checkpoints")
        if len(artifact.artifact_paths) < 2:
            issues.append("missing expected output paths")
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if not issues else "rejected",
            score=92 if not issues else 60,
            issues=issues,
            approved=not issues,
            return_to_actor=bool(issues),
            handoff_note="draft section ready" if not issues else "fix issues and resubmit",
        )
