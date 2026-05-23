from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("lanes_ceo.policy")


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


# ── secret.md reader ──

# Patterns to extract account identifiers from secret.md lines
# Each pattern: (regex, provider_label)
_IDENTIFIER_PATTERNS: list[tuple[str, str]] = [
    (r"qq[账号号]{1,2}[：:]\s*(\d+)", "qq"),
    (r"微信[账号号]{1,2}[：:]\s*(\d+)", "weixin"),
    (r"谷歌邮箱[账号号]{0,2}[：:]\s*([\w.+-]+@[\w.-]+\.\w+)", "gmail"),
    (r"网易邮箱[账号号]{0,2}[：:]\s*([\w.+-]+@[\w.-]+\.\w+)", "163mail"),
    (r"东南大学[账号号]{1,2}[：:]\s*(\d+)", "seu"),
]


def load_credential_refs(secret_path: str | Path | None = None) -> dict[str, CredentialRef]:
    """Parse secret.md and extract credential metadata (identifiers only, never passwords).

    Args:
        secret_path: Path to secret.md. Defaults to <project_root>/secret.md.

    Returns:
        Dict of key_id → CredentialRef. Passwords are never captured.
    """
    if secret_path is None:
        secret_path = Path(__file__).resolve().parents[2] / "secret.md"

    secret_path = Path(secret_path)
    if not secret_path.exists():
        logger.debug("secret.md not found at %s", secret_path)
        return {}

    refs: dict[str, CredentialRef] = {}
    try:
        text = secret_path.read_text(encoding="utf-8")
    except Exception as exc:
        logger.warning("Failed to read secret.md: %s", exc)
        return {}

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        for pattern, provider in _IDENTIFIER_PATTERNS:
            m = re.search(pattern, line, re.IGNORECASE)
            if m:
                key_id = m.group(1).strip()
                refs[key_id] = CredentialRef(key_id=key_id, provider=provider, source="secret.md")
                break

    logger.info("Loaded %d credential refs from %s", len(refs), secret_path)
    return refs
