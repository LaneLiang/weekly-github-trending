from typing import Protocol

from lanes_ceo.contracts import TaskRequest


class IngressAdapter(Protocol):
    source_channel: str

    def receive(self, raw_event: dict) -> TaskRequest: ...
