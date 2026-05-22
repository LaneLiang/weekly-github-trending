from lanes_ceo.ingress.cli import run_local_request


def test_local_cli_request_completes_fake_workflow(tmp_path) -> None:
    job = run_local_request(
        message="hello from cli",
        role_group="fake",
        db_path=tmp_path / "lanes.sqlite3",
    )

    assert job.role_group == "fake"
    assert job.status.value == "notified"
