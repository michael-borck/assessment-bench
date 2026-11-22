"""CLI smoke tests for assessment-bench.

These exercise the argument wiring and the deterministic paths without any
provider keys or the analyser stack.
"""

from __future__ import annotations

import pytest
import yaml

from assessment_bench.cli import main


def test_cli_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "assessment-bench" in capsys.readouterr().out


def test_cli_requires_a_subcommand():
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_init_writes_a_runnable_example(tmp_path):
    out = tmp_path / "experiment.yaml"
    assert main(["init", str(out)]) == 0
    cfg = yaml.safe_load(out.read_text())
    assert cfg["name"] == "My experiment"
    assert cfg["rubric"] == "rubric.yaml"
    assert {a["kind"] for a in cfg["arms"]} == {"llm", "signals", "hybrid"}


def test_init_refuses_to_overwrite(tmp_path):
    out = tmp_path / "experiment.yaml"
    out.write_text("keep me")
    assert main(["init", str(out)]) == 1
    assert out.read_text() == "keep me"


def test_run_missing_config_returns_one(tmp_path, capsys):
    assert main(["run", str(tmp_path / "nope.yaml")]) == 1
    assert "cannot read experiment config" in capsys.readouterr().out


def test_run_invalid_config_returns_one(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("name: x\n")  # missing rubric/submissions/arms
    assert main(["run", str(bad)]) == 1
