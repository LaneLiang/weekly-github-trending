from typing import Protocol

from lanes_ceo.contracts import Artifact, CriticReview, Job


class Workflow(Protocol):
    role_group: str
    actor_name: str
    critic_name: str

    def run_actor(self, job: Job) -> Artifact: ...

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview: ...
