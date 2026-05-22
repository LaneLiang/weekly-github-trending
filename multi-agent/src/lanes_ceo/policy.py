from dataclasses import dataclass, field


@dataclass(slots=True)
class CredentialRef:
    """Reference to a credential — never stores the secret itself."""

    key_id: str
    provider: str
    source: str = "secret.md"


class PolicyEngine:
    """Central policy decisions for the orchestrator.

    V1 rules:
    - Default auto-approve for low-sensitivity workflows
    - WAITING_USER for verification codes and high-risk actions
    - Paper writing group exempt from elimination scoring
    - Email mark-read requires paper keyword detection
    """

    ELIMINATION_EXEMPT_GROUPS = frozenset({"paper_writing"})
    HIGH_SENSITIVITY_ACTIONS = frozenset(
        {"mark_read", "send_external", "delete", "credential_access"}
    )

    def __init__(self) -> None:
        self._credential_refs: dict[str, CredentialRef] = {}

    def register_credential(self, ref: CredentialRef) -> None:
        self._credential_refs[ref.key_id] = ref

    def get_credential_ref(self, key_id: str) -> CredentialRef | None:
        return self._credential_refs.get(key_id)

    def requires_user_confirmation(self, action: str, role_group: str) -> bool:
        if action in self.HIGH_SENSITIVITY_ACTIONS:
            return True
        return False

    def is_elimination_exempt(self, role_group: str) -> bool:
        return role_group in self.ELIMINATION_EXEMPT_GROUPS
