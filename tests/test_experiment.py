"""Runner integration: all three arm kinds over a tmp cohort, engine edges stubbed.

providers.complete and run_signals_arm are the network/analyser boundaries —
everything else (discovery, prompts, repetitions, stats, sharing one signal
pass across arms, agreement) runs for real.
"""

import pytest

from assessment_bench import arms
from assessment_bench.experiment import run_experiment
from assessment_bench.models import ExperimentConfig, SignalReading


@pytest.fixture()
def cohort(tmp_path):
    rubric = tmp_path / "rubric.yaml"
    rubric.write_text("assignment: t\nrubric:\n  - id: c1\n    description: d\n")
    marks = tmp_path / "marks.csv"
    marks.write_text("submission_id,mark\nalice,85\nbob,45\n")
    for name, text in [("alice", "long thoughtful report"), ("bob", "short")]:
        folder = tmp_path / "subs" / name
        folder.mkdir(parents=True)
        (folder / "report.md").write_text(text)
    return tmp_path


@pytest.fixture()
def stubbed_engine(monkeypatch):
    prompts: list[str] = []

    def fake_complete(prompt, *, system, spec):
        prompts.append(prompt)
        # Distinguishable scores: alice's text is longer; hybrids land higher.
        base = 80 if "thoughtful" in prompt else 50
        return f"Decent work.\nSCORE: {base + (5 if 'DETERMINISTIC' in prompt else 0)}/100"

    def fake_signals(rubric_path, submissions_dir):
        return [
            SignalReading(submission_id=s, criterion_id="c1", signal="document.word_count", value=v)
            for s, v in [("alice", 440), ("bob", 133)]
        ]

    monkeypatch.setattr(arms.providers, "complete", fake_complete)
    monkeypatch.setattr(arms, "run_signals_arm", fake_signals)
    return prompts


def _config(cohort):
    return ExperimentConfig.model_validate(
        {
            "name": "t",
            "rubric": cohort / "rubric.yaml",
            "submissions": cohort / "subs",
            "human_marks": cohort / "marks.csv",
            "arms": [
                {"id": "llm", "kind": "llm", "repetitions": 2,
                 "provider": {"provider": "ollama", "model": "m"}},
                {"id": "hybrid", "kind": "hybrid", "repetitions": 2,
                 "provider": {"provider": "ollama", "model": "m"}},
                {"id": "signals", "kind": "signals"},
            ],
        }
    )


def test_all_three_arms_end_to_end(cohort, stubbed_engine):
    result = run_experiment(_config(cohort))

    assert result.submissions == ["alice", "bob"]
    by_key = {(o.arm_id, o.submission_id): o for o in result.outcomes}
    assert len(by_key) == 6  # 3 arms x 2 submissions

    # LLM arm: 2 runs each, clean prompts, real stats.
    llm_alice = by_key[("llm", "alice")]
    assert [r.score for r in llm_alice.runs] == [80.0, 80.0]
    assert llm_alice.stats.n == 2 and llm_alice.stats.reliability == 1.0
    assert llm_alice.signals == []

    # Hybrid arm: signals raised the score and ride along on the outcome.
    hybrid_bob = by_key[("hybrid", "bob")]
    assert [r.score for r in hybrid_bob.runs] == [55.0, 55.0]
    assert hybrid_bob.signals[0].signal == "document.word_count"

    # Signals arm: readings only, no runs/stats.
    signals_alice = by_key[("signals", "alice")]
    assert signals_alice.runs == [] and signals_alice.stats is None
    assert signals_alice.signals[0].value == 440

    # Agreement: both LLM arms' means and the numeric signal vs marks.
    measures = {a.measure for a in result.agreements}
    assert measures == {"llm", "hybrid", "document.word_count"}
    assert all(a.pearson == pytest.approx(1.0) for a in result.agreements)

    # Hybrid prompts carried the evidence; pure-LLM prompts stayed clean.
    hybrid_prompts = [p for p in stubbed_engine if "DETERMINISTIC" in p]
    assert len(hybrid_prompts) == 4  # 2 submissions x 2 repetitions
    assert len(stubbed_engine) == 8


def test_signal_pass_shared_across_arms(cohort, monkeypatch):
    calls = []

    def counting_signals(rubric_path, submissions_dir):
        calls.append(1)
        return []

    monkeypatch.setattr(arms, "run_signals_arm", counting_signals)
    monkeypatch.setattr(arms.providers, "complete", lambda p, *, system, spec: "SCORE: 1/100")
    run_experiment(_config(cohort))
    assert len(calls) == 1  # hybrid + signals arms share one assessment-lens pass