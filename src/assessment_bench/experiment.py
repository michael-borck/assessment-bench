"""Experiment runner — the bench's orchestration spine.

One experiment = one rubric + one cohort + N arms. Each LLM arm runs per
submission x repetitions; the signals arm runs once per cohort (deterministic).
Afterwards, every arm's mean score and every numeric signal is correlated
against the human marks (when provided). The bench measures; it never marks.
"""

from __future__ import annotations

import csv
from pathlib import Path

import yaml

from . import arms, stats
from .exceptions import AssessmentBenchError
from .models import (
    Agreement,
    ArmKind,
    ArmOutcome,
    ExperimentConfig,
    ExperimentResult,
)


def load_config(path: Path) -> ExperimentConfig:
    """Load an experiment YAML; relative paths resolve against the config's folder."""
    raw = yaml.safe_load(Path(path).read_text())
    config = ExperimentConfig.model_validate(raw)
    base = Path(path).resolve().parent
    config.rubric = (base / config.rubric).resolve()
    config.submissions = (base / config.submissions).resolve()
    if config.human_marks is not None:
        config.human_marks = (base / config.human_marks).resolve()
    return config


def discover_submissions(submissions_dir: Path) -> list[Path]:
    """One subfolder = one submission, mirroring assessment-lens's discovery."""
    if not submissions_dir.is_dir():
        raise AssessmentBenchError(f"submissions folder not found: {submissions_dir}")
    folders = sorted(p for p in submissions_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not folders:
        raise AssessmentBenchError(f"no submission subfolders in {submissions_dir}")
    return folders


def load_human_marks(path: Path) -> dict[str, float]:
    """CSV with a header row: submission_id,mark."""
    marks: dict[str, float] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            marks[row["submission_id"].strip()] = float(row["mark"])
    return marks


def _agreements(
    result: ExperimentResult, marks: dict[str, float]
) -> list[Agreement]:
    """Correlate every arm mean and every numeric signal with the human marks."""
    agreements: list[Agreement] = []

    # Arm means (LLM arms): pair each submission's mean score with its mark.
    by_arm: dict[str, dict[str, float]] = {}
    for outcome in result.outcomes:
        if outcome.stats is not None:
            by_arm.setdefault(outcome.arm_id, {})[outcome.submission_id] = outcome.stats.mean
    # Numeric signals (signals arm): one measure per dotted signal path.
    by_signal: dict[str, dict[str, float]] = {}
    for outcome in result.outcomes:
        for reading in outcome.signals:
            if isinstance(reading.value, bool):
                value = float(reading.value)
            elif isinstance(reading.value, (int, float)):
                value = float(reading.value)
            else:
                continue
            by_signal.setdefault(reading.signal, {})[reading.submission_id] = value

    for measure, values in {**by_arm, **by_signal}.items():
        paired = [(values[s], marks[s]) for s in values if s in marks]
        if len(paired) < 2:
            continue
        xs, ys = [p[0] for p in paired], [p[1] for p in paired]
        agreements.append(
            Agreement(
                measure=measure,
                n=len(paired),
                pearson=stats.pearson(xs, ys),
                spearman=stats.spearman(xs, ys),
            )
        )
    return agreements


def run_experiment(config: ExperimentConfig, *, progress=None) -> ExperimentResult:
    """Run every arm over the cohort and assemble the structured result.

    ``progress`` is an optional callable(str) for CLI/UI status lines.
    """
    say = progress or (lambda _msg: None)
    submissions = discover_submissions(config.submissions)
    rubric_text = config.rubric.read_text()
    result = ExperimentResult(
        name=config.name,
        max_score=config.max_score,
        submissions=[s.name for s in submissions],
    )

    for arm in config.arms:
        if arm.kind is ArmKind.SIGNALS:
            say(f"arm {arm.id}: assessment-lens over {len(submissions)} submissions")
            readings = arms.run_signals_arm(arm, config.rubric, config.submissions)
            for folder in submissions:
                result.outcomes.append(
                    ArmOutcome(
                        submission_id=folder.name,
                        arm_id=arm.id,
                        signals=[r for r in readings if r.submission_id == folder.name],
                    )
                )
        else:
            for folder in submissions:
                say(f"arm {arm.id}: {folder.name} x{arm.repetitions}")
                runs = arms.run_llm_arm(arm, folder.name, folder, rubric_text, config.max_score)
                scores = [r.score for r in runs if r.score is not None]
                result.outcomes.append(
                    ArmOutcome(
                        submission_id=folder.name,
                        arm_id=arm.id,
                        runs=runs,
                        stats=stats.run_stats(scores),
                    )
                )

    if config.human_marks is not None:
        marks = load_human_marks(config.human_marks)
        result.agreements = _agreements(result, marks)

    return result
