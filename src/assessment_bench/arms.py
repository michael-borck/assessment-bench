"""The assessment arms under test.

LLM arm — the approach the family deliberately moved away from (an LLM reading
a submission and emitting a mark), kept here as the benchmark baseline. Prompt
shape ports the original Rust prototype's Tier-1 design; the score comes from a
strict trailing ``SCORE: x/y`` line with a permissive regex fallback.

Signals arm — assessment-lens observations. Deterministic, so it runs once per
cohort regardless of repetitions; the bench consumes raw evidence values (not
the presence-based coverage column) and correlates each numeric signal with the
human marks.

Hybrid arm — the LLM arm with the submission's deterministic signal readings
rendered into the marking prompt. The bench's central research question lives
in the contrast between these three.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from assessment_lens.assess import assess
from assessment_lens.models import AssessmentResult
from assessment_lens.rubric import load_rubric

from . import providers
from .models import ArmSpec, GradeRun, SignalReading

# Submission text for the LLM arm. Plain-text formats are read directly;
# .pdf/.docx go through the family's canonical extractor when installed.
_PLAIN_TEXT_SUFFIXES = {".md", ".txt", ".py", ".js", ".ts", ".r", ".sql", ".csv"}
_EXTRACTOR_SUFFIXES = {".pdf", ".docx", ".pptx"}

_GRADE_SYSTEM = (
    "You are an experienced university marker. Grade the submission against the "
    "rubric. Be consistent and justify briefly. End your response with exactly "
    "one line in the form 'SCORE: <number>/<max>' and nothing after it."
)

_SCORE_RE = re.compile(r"SCORE:\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_FALLBACK_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:/|out of)\s*(\d+(?:\.\d+)?)")


def read_submission_text(folder: Path) -> str:
    """Concatenate the readable artefacts in one submission folder."""
    parts: list[str] = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in _PLAIN_TEXT_SUFFIXES:
            parts.append(f"--- {path.name} ---\n{path.read_text(errors='replace')}")
        elif suffix in _EXTRACTOR_SUFFIXES:
            try:
                from document_analyser import extract_text

                parts.append(f"--- {path.name} ---\n{extract_text(path)}")
            except ImportError:
                parts.append(
                    f"--- {path.name} --- (skipped: install the [analysers] extra to extract {suffix})"
                )
    return "\n\n".join(parts)


def extract_score(response: str, max_score: float) -> tuple[float | None, float]:
    """Pull (score, max) from a response; scale to max_score when the LLM used its own denominator."""
    matches = _SCORE_RE.findall(response) or _FALLBACK_RE.findall(response)
    if not matches:
        return None, max_score
    raw, denom = (float(v) for v in matches[-1])
    if denom and denom != max_score:
        raw = raw / denom * max_score
    return raw, max_score


def render_signals(readings: list[SignalReading]) -> str:
    """Flat evidence lines for the hybrid prompt, grouped under their criterion."""
    return "\n".join(
        f"- [{r.criterion_id}] {r.signal} = {json.dumps(r.value, default=str)}"
        for r in readings
    )


def grade_prompt(
    rubric_text: str, submission_text: str, max_score: float, signals_text: str = ""
) -> str:
    signals_block = (
        "DETERMINISTIC ANALYSER SIGNALS (objective measurements of this submission; "
        f"weigh them as evidence):\n{signals_text}\n\n"
        if signals_text
        else ""
    )
    return (
        f"RUBRIC:\n{rubric_text}\n\n"
        f"{signals_block}"
        f"SUBMISSION:\n{submission_text}\n\n"
        f"Grade the submission against the rubric out of {max_score:g}. "
        f"Give 2-3 sentences of rationale, then the final 'SCORE: x/{max_score:g}' line."
    )


def run_llm_arm(
    arm: ArmSpec,
    submission_id: str,
    submission_folder: Path,
    rubric_text: str,
    max_score: float,
    readings: list[SignalReading] | None = None,
) -> list[GradeRun]:
    """All repetitions of one LLM (or hybrid, when ``readings`` given) arm for one
    submission. Failures are recorded on the run, not raised."""
    assert arm.provider is not None  # validated by ArmSpec
    text = read_submission_text(submission_folder)
    prompt = grade_prompt(rubric_text, text, max_score, render_signals(readings or []))
    runs: list[GradeRun] = []
    for i in range(arm.repetitions):
        run = GradeRun(
            submission_id=submission_id, arm_id=arm.id, run_index=i, max_score=max_score
        )
        try:
            response = providers.complete(
                prompt, system=_GRADE_SYSTEM, spec=arm.provider
            )
            run.raw_response = response
            run.score, _ = extract_score(response, max_score)
            run.rationale = _SCORE_RE.sub("", response).strip()
            if run.score is None:
                run.error = "no SCORE line found in response"
        except Exception as exc:  # one bad call must not kill a cohort run
            run.error = str(exc)
        runs.append(run)
    return runs


def run_cohort_pass(rubric_path: Path, submissions_dir: Path) -> AssessmentResult:
    """The one deterministic assessment-lens pass over the whole cohort.

    Returns the full ``AssessmentResult`` (not just flat readings) so the bench
    can also surface the cohort-relative distinctiveness assessment-lens computes
    in the same pass — both the signals arm and distinctiveness ride on this one
    (expensive) shell-out to the analyser stack.
    """
    rubric = load_rubric(rubric_path)
    return assess(rubric, submissions_dir)


def signal_readings(result: AssessmentResult) -> list[SignalReading]:
    """Flatten an AssessmentResult's per-criterion evidence into flat readings."""
    readings: list[SignalReading] = []
    for submission in result.submissions:
        for observation in submission.observations:
            for evidence in observation.evidence:
                readings.append(
                    SignalReading(
                        submission_id=submission.submission_id,
                        criterion_id=observation.criterion_id,
                        signal=evidence.signal,
                        value=evidence.value,
                    )
                )
    return readings
