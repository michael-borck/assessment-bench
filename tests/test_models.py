"""Config models: the experiment YAML is the bench's central contract."""

import pytest
from pydantic import ValidationError

from assessment_bench.models import ArmKind, ArmSpec, ExperimentConfig


def test_llm_arm_requires_provider():
    with pytest.raises((ValidationError, ValueError)):
        ArmSpec(id="bad", kind=ArmKind.LLM)


def test_signals_arm_needs_no_provider():
    arm = ArmSpec(id="signals", kind=ArmKind.SIGNALS)
    assert arm.repetitions == 1


def test_experiment_config_parses():
    config = ExperimentConfig.model_validate(
        {
            "name": "t",
            "rubric": "rubric.yaml",
            "submissions": "subs/",
            "arms": [
                {
                    "id": "llm",
                    "kind": "llm",
                    "repetitions": 3,
                    "provider": {"provider": "ollama", "model": "llama3.1"},
                },
                {"id": "signals", "kind": "signals"},
            ],
        }
    )
    assert config.max_score == 100.0
    assert config.arms[0].provider.base_url is None


def test_experiment_config_requires_an_arm():
    with pytest.raises(ValidationError):
        ExperimentConfig.model_validate(
            {"name": "t", "rubric": "r.yaml", "submissions": "s/", "arms": []}
        )
