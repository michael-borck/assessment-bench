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
from pydantic import ValidationError

from . import arms, stats
from .exceptions import AssessmentBenchError
from .models import (
    Agreement,
    ArmKind,
    ArmOutcome,
    CohortDistinctiveness,
    ExperimentConfig,
    ExperimentResult,
)

# Preference order when distilling distinctiveness to one comparable scalar per
# submission: combined carries both modalities, then text, then signal-only.
_DISTINCTIVENESS_SPACE_ORDER = ("combined", "text", "signal")


def load_config(path: Path) -> ExperimentConfig:
    """Load an experiment YAML; relative paths resolve against the config's folder."""
    path = Path(path)
    try:
        raw = yaml.safe_load(path.read_text())
    except OSError as exc:
        raise AssessmentBenchError(f"cannot read experiment config: {exc}") from exc
    except yaml.YAMLError as exc:
        raise AssessmentBenchError(f"invalid YAML in {path}: {exc}") from exc
    try:
        config = ExperimentConfig.model_validate(raw)
    except ValidationError as exc:
        raise AssessmentBenchError(f"invalid experiment config {path}: {exc}") from exc
    base = path.resolve().parent
    config.rubric = (base / config.rubric).resolve()
    config.submissions = (base / config.submissions).resolve()
    if config.human_marks is not None:
        config.human_marks = (base / config.human_marks).resolve()
    return config


def discover_submissions(submissions_dir: Path) -> list[Path]:
    """One subfolder = one submission, mirroring assessment-lens's discovery."""
    if not submissions_dir.is_dir():
        raise AssessmentBenchError(f"submissions folder not found: {submissions_dir}")
    folders = sorted(
        p
        for p in submissions_dir.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )
    if not folders:
        raise AssessmentBenchError(f"no submission subfolders in {submissions_dir}")
    return folders


def load_human_marks(path: Path) -> dict[str, float]:
    """CSV with a header row: submission_id,mark."""
    marks: dict[str, float] = {}
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            fields = set(reader.fieldnames or [])
            if not {"submission_id", "mark"} <= fields:
                raise AssessmentBenchError(
                    f"{path}: header must include submission_id,mark "
                    f"(got: {', '.join(sorted(fields)) or 'empty file'})"
                )
            for line_no, row in enumerate(reader, start=2):
                try:
                    marks[row["submission_id"].strip()] = float(row["mark"])
                except (AttributeError, TypeError, ValueError) as exc:
                    raise AssessmentBenchError(
                        f"{path} line {line_no}: expected 'submission_id,mark' with a "
                        f"numeric mark (got submission_id={row['submission_id']!r}, "
                        f"mark={row['mark']!r})"
                    ) from exc
    except OSError as exc:
        raise AssessmentBenchError(f"cannot read human marks: {exc}") from exc
    return marks


def _distinctiveness_scalar(entry: CohortDistinctiveness) -> float | None:
    """One comparable scalar (mean cohort similarity) for a submission.

    Picks the richest available space (combined > text > signal). Lower means more
    distinctive, so a positive correlation with marks reads as 'more typical
    submissions scored higher' — a prompt for the researcher, never a verdict.
    """
    for name in _DISTINCTIVENESS_SPACE_ORDER:
        space = entry.distinctiveness.space(name)
        if space is not None and space.mean_similarity is not None:
            return space.mean_similarity
    return None


def _agreements(result: ExperimentResult, marks: dict[str, float]) -> list[Agreement]:
    """Correlate every arm mean, every numeric signal, and distinctiveness with marks."""
    agreements: list[Agreement] = []

    # Arm means (LLM arms): pair each submission's mean score with its mark.
    by_arm: dict[str, dict[str, float]] = {}
    for outcome in result.outcomes:
        if outcome.stats is not None:
            by_arm.setdefault(outcome.arm_id, {})[outcome.submission_id] = (
                outcome.stats.mean
            )
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
    # Distinctiveness: one measure (mean cohort similarity per submission).
    by_distinctiveness: dict[str, dict[str, float]] = {}
    for entry in result.distinctiveness:
        scalar = _distinctiveness_scalar(entry)
        if scalar is not None:
            by_distinctiveness.setdefault("distinctiveness.mean_similarity", {})[
                entry.submission_id
            ] = scalar

    for measure, values in {**by_arm, **by_signal, **by_distinctiveness}.items():
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
    try:
        rubric_text = config.rubric.read_text()
    except OSError as exc:
        raise AssessmentBenchError(f"cannot read rubric: {exc}") from exc
    result = ExperimentResult(
        name=config.name,
        max_score=config.max_score,
        submissions=[s.name for s in submissions],
    )

    # The deterministic pass is shared: one assessment-lens run per cohort feeds
    # every signals/hybrid arm AND the cohort distinctiveness. Lazily run on first
    # need, so a pure-LLM experiment never pays for the analyser stack.
    cohort_result = None
    cohort_readings = None

    def cohort():
        nonlocal cohort_result, cohort_readings
        if cohort_result is None:
            say(f"signals: assessment-lens over {len(submissions)} submissions")
            cohort_result = arms.run_cohort_pass(config.rubric, config.submissions)
            cohort_readings = arms.signal_readings(cohort_result)
        return cohort_result

    def readings_for(submission_id: str):
        cohort()
        return [r for r in cohort_readings if r.submission_id == submission_id]

    for arm in config.arms:
        if arm.kind is ArmKind.SIGNALS:
            say(f"arm {arm.id}: deterministic observations")
            for folder in submissions:
                result.outcomes.append(
                    ArmOutcome(
                        submission_id=folder.name,
                        arm_id=arm.id,
                        signals=readings_for(folder.name),
                    )
                )
        else:
            for folder in submissions:
                say(f"arm {arm.id}: {folder.name} x{arm.repetitions}")
                readings = (
                    readings_for(folder.name) if arm.kind is ArmKind.HYBRID else None
                )
                runs = arms.run_llm_arm(
                    arm, folder.name, folder, rubric_text, config.max_score, readings
                )
                scores = [r.score for r in runs if r.score is not None]
                result.outcomes.append(
                    ArmOutcome(
                        submission_id=folder.name,
                        arm_id=arm.id,
                        runs=runs,
                        stats=stats.run_stats(scores),
                        signals=readings or [],
                    )
                )

    # Surface cohort distinctiveness if the deterministic pass ran (signals/hybrid
    # arm present) and assessment-lens was able to compute it (embeddings/signals).
    if cohort_result is not None:
        result.distinctiveness = [
            CohortDistinctiveness(
                submission_id=sub.submission_id, distinctiveness=sub.distinctiveness
            )
            for sub in cohort_result.submissions
            if sub.distinctiveness is not None
        ]

    if config.human_marks is not None:
        marks = load_human_marks(config.human_marks)
        result.agreements = _agreements(result, marks)

    return result
