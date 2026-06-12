"""The assessment arms under test.

LLM arm — the approach the family deliberately moved away from (an LLM reading
a submission and emitting a mark), kept here as the benchmark baseline. Prompt
shape ports the original Rust prototype's Tier-1 design; the score comes from a
strict trailing ``SCORE: x/y`` line with a permissive regex fallback.

Signals arm — assessment-lens observations. Deterministic, so it runs once per
cohort regardless of repetitions; the bench consumes raw evidence values (not
the presence-based coverage column) and correlates each numeric signal with the
human marks.
"""

from __future__ import annotations

import re
from pathlib import Path

from assessment_lens.assess import assess
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
                parts.append(f"--- {path.name} --- (skipped: install the [analysers] extra to extract {suffix})")
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


def grade_prompt(rubric_text: str, submission_text: str, max_score: float) -> str:
    return (
        f"RUBRIC:\n{rubric_text}\n\n"
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
) -> list[GradeRun]:
    """All repetitions of one LLM arm for one submission. Failures are recorded, not raised."""
    assert arm.provider is not None  # validated by ArmSpec
    text = read_submission_text(submission_folder)
    prompt = grade_prompt(rubric_text, text, max_score)
    runs: list[GradeRun] = []
    for i in range(arm.repetitions):
        run = GradeRun(submission_id=submission_id, arm_id=arm.id, run_index=i, max_score=max_score)
        try:
            response = providers.complete(prompt, system=_GRADE_SYSTEM, spec=arm.provider)
            run.raw_response = response
            run.score, _ = extract_score(response, max_score)
            run.rationale = _SCORE_RE.sub("", response).strip()
            if run.score is None:
                run.error = "no SCORE line found in response"
        except Exception as exc:  # one bad call must not kill a cohort run
            run.error = str(exc)
        runs.append(run)
    return runs


def run_signals_arm(arm: ArmSpec, rubric_path: Path, submissions_dir: Path) -> list[SignalReading]:
    """One assessment-lens pass over the whole cohort -> flat evidence readings."""
    rubric = load_rubric(rubric_path)
    result = assess(rubric, submissions_dir)
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
