from lanes_ceo.policy import CredentialRef, PolicyEngine


def test_policy_marks_key_actions_for_user_confirmation() -> None:
    engine = PolicyEngine()
    assert engine.requires_user_confirmation("mark_read", "mail_digest") is True
    assert engine.requires_user_confirmation("send_external", "briefings") is True
    assert engine.requires_user_confirmation("delete", "any") is True


def test_policy_paper_writing_is_elimination_exempt() -> None:
    engine = PolicyEngine()
    assert engine.is_elimination_exempt("paper_writing") is True
    assert engine.is_elimination_exempt("github_trending") is False
    assert engine.is_elimination_exempt("mail_digest") is False


def test_credential_ref_no_secrets() -> None:
    ref = CredentialRef(key_id="deepseek-api", provider="deepseek")
    assert ref.key_id == "deepseek-api"
    assert ref.provider == "deepseek"
    assert ref.source == "secret.md"
    assert "api_key" not in dir(ref)


def test_policy_registers_and_retrieves_credential_refs() -> None:
    engine = PolicyEngine()
    ref = CredentialRef(key_id="openai-key", provider="openai")
    engine.register_credential(ref)
    retrieved = engine.get_credential_ref("openai-key")
    assert retrieved is ref
    assert engine.get_credential_ref("unknown") is None
