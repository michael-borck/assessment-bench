"""HTTP API plumbing — the engine is stubbed; these test the contract a UI relies on."""

import time

import pytest

fastapi = pytest.importorskip("fastapi", reason="needs the [serve] extra")

from fastapi.testclient import TestClient  # noqa: E402  (guarded by importorskip above)

from assessment_bench import api  # noqa: E402
from assessment_bench.models import ExperimentResult  # noqa: E402

CONFIG = {
    "name": "api-test",
    "rubric": "/tmp/rubric.yaml",
    "submissions": "/tmp/subs",
    "arms": [{"id": "signals", "kind": "signals"}],
}


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(api, "_runs", {})
    return TestClient(api.app)


def _wait_done(client, run_id, timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = client.get(f"/experiments/{run_id}").json()["status"]
        if status in ("done", "failed"):
            return status
        time.sleep(0.02)
    pytest.fail("experiment never finished")


def test_contract_routes(client):
    assert client.get("/health").json()["status"] == "ok"
    manifest = client.get("/manifest").json()
    assert manifest["name"] == "assessment-bench"
    assert manifest["role"] == "bench"


def test_run_lifecycle(client, monkeypatch):
    def fake_run(config, *, progress=None):
        progress("arm signals: working")
        return ExperimentResult(
            name=config.name, max_score=config.max_score, submissions=["a"]
        )

    monkeypatch.setattr(api, "run_experiment", fake_run)

    started = client.post("/experiments", json={"config": CONFIG})
    assert started.status_code == 202
    run_id = started.json()["id"]

    assert _wait_done(client, run_id) == "done"
    summary = client.get(f"/experiments/{run_id}").json()
    assert "arm signals: working" in summary["progress"]

    result = client.get(f"/experiments/{run_id}/result")
    assert result.status_code == 200
    assert result.json()["name"] == "api-test"

    listing = client.get("/experiments").json()
    assert [r["id"] for r in listing] == [run_id]


def test_failed_run_reports_error(client, monkeypatch):
    def boom(config, *, progress=None):
        raise RuntimeError("cohort folder missing")

    monkeypatch.setattr(api, "run_experiment", boom)
    run_id = client.post("/experiments", json={"config": CONFIG}).json()["id"]
    assert _wait_done(client, run_id) == "failed"
    assert (
        "cohort folder missing" in client.get(f"/experiments/{run_id}").json()["error"]
    )
    assert client.get(f"/experiments/{run_id}/result").status_code == 500


def test_unknown_id_404s(client):
    assert client.get("/experiments/nope").status_code == 404
    assert client.get("/experiments/nope/result").status_code == 404
