from typing import Protocol

from lanes_ceo.contracts import Artifact, CriticReview, Job


class SubAgent(Protocol):
    agent_id: str
    agent_type: str  # "actor" | "critic"
    role_group: str

    def run(self, job: Job, context: dict) -> Artifact | CriticReview: ...
