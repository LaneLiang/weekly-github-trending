from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.paper_research import PaperResearchWorkflow
from lanes_ceo.workflows.paper_writing import PaperWritingWorkflow


def _make_job(role_group: str, message: str = "test topic") -> Job:
    return Job(
        job_id=f"job-{role_group}",
        request_id="req-1",
        role_group=role_group,
        actor=f"{role_group}-actor",
        critic=f"{role_group}-critic",
        status=JobStatus.RECEIVED,
        input={"message": message},
        workspace="runtime/jobs/test",
    )


class TestPaperResearchWorkflow:
    def test_actor_produces_research_artifact(self) -> None:
        wf = PaperResearchWorkflow()
        job = _make_job("paper_research", "transformer architectures")
        artifact = wf.run_actor(job)
        assert artifact.artifact_type == "paper_research"
        assert len(artifact.sources) >= 2
        assert len(artifact.artifact_paths) >= 2
        assert len(artifact.user_confirmations) >= 1

    def test_critic_approves_rich_research(self) -> None:
        wf = PaperResearchWorkflow()
        job = _make_job("paper_research")
        artifact = Artifact(
            artifact_id="art-pr",
            job_id=job.job_id,
            artifact_type="paper_research",
            summary="文献调研: transformer architectures。推荐检索关键词: attention mechanism, sparse attention, linear transformer, efficient transformer。该领域前5篇重要论文: 1) Attention Is All You Need (NeurIPS 2017) 2) Sparse Transformer (NeurIPS 2019) 3) Linformer (ICML 2020) 4) Reformer (ICLR 2020) 5) FlashAttention (NeurIPS 2022)。研究缺口: 长序列场景下的计算效率仍有提升空间。",
            artifact_paths=["papers/downloaded/", "papers/notes/"],
            sources=["arxiv", "scholar", "semantic-scholar"],
            risks=[],
            user_confirmations=["请确认检索关键词是否准确"],
        )
        review = wf.run_critic(job, artifact)
        assert review.approved is True
        assert review.score >= 85

    def test_critic_rejects_insufficient_sources(self) -> None:
        wf = PaperResearchWorkflow()
        job = _make_job("paper_research")
        artifact = Artifact(
            artifact_id="art-pr2",
            job_id=job.job_id,
            artifact_type="paper_research",
            summary="文献调研: test topic。该领域研究活跃，有多篇相关论文。检索源: arxiv, scholar。推荐关键词: attention, transformer。前5篇重要论文包括经典和最新发表。",
            artifact_paths=["papers/downloaded/", "papers/notes/"],
            sources=[],
            risks=[],
            user_confirmations=[],
        )
        review = wf.run_critic(job, artifact)
        assert review.approved is False
        assert review.return_to_actor is True


class TestPaperWritingWorkflow:
    def test_writing_is_exempt_from_elimination(self) -> None:
        wf = PaperWritingWorkflow()
        assert wf.exempt_from_elimination is True

    def test_actor_produces_draft_artifact(self) -> None:
        wf = PaperWritingWorkflow()
        job = _make_job("paper_writing", "methods section")
        artifact = wf.run_actor(job)
        assert artifact.artifact_type == "paper_draft"
        assert len(artifact.user_confirmations) >= 2
        assert "references.bib" in artifact.artifact_paths

    def test_critic_approves_rich_draft(self) -> None:
        wf = PaperWritingWorkflow()
        job = _make_job("paper_writing")
        artifact = Artifact(
            artifact_id="art-pw",
            job_id=job.job_id,
            artifact_type="paper_draft",
            summary="引言部分：随着深度学习技术的快速发展，Transformer架构已成为自然语言处理领域的主流方法。方法部分：本文提出了一种改进的多头注意力机制，通过引入稀疏连接和线性近似，在保持模型精度的同时将计算复杂度从O(n²)降低到O(n log n)。结果部分：在WMT14英德翻译任务上，BLEU分数从基准的28.4提升到30.1。结论部分：实验表明所提出的方法在翻译质量和推理速度上均优于现有方案。",
            artifact_paths=["drafts/current/", "figures/", "references.bib"],
            sources=["literature-review", "experiment-data"],
            risks=[],
            user_confirmations=["请确认技术内容准确性", "图表数据和格式是否需要调整"],
        )
        review = wf.run_critic(job, artifact)
        assert review.approved is True
        assert review.score >= 90

    def test_critic_rejects_missing_checkpoints(self) -> None:
        wf = PaperWritingWorkflow()
        job = _make_job("paper_writing")
        artifact = Artifact(
            artifact_id="art-pw2",
            job_id=job.job_id,
            artifact_type="paper_draft",
            summary="引言部分：本文讨论了Transformer架构的改进方法及其在自然语言处理中的应用，实验结果显示了显著的性能提升，结论表明该方法有效。",
            artifact_paths=["drafts/current/", "figures/", "references.bib"],
            sources=[],
            risks=[],
            user_confirmations=[],
        )
        review = wf.run_critic(job, artifact)
        assert review.approved is False
