"""Core data models for assessment-bench.

The bench is the family's *measurement* layer: it runs the same cohort through
competing assessment arms and reports consistency and agreement. The design
rule that shapes these models: **the bench measures; it never marks.** An LLM
arm produces scores because that is the approach under test — the bench treats
those scores as data points, not as grades for students. Human marks, when
provided, are the ground truth everything is compared against.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from assessment_lens.models import Distinctiveness
from pydantic import BaseModel, Field


# --- Experiment side (input) -------------------------------------------------
class ProviderName(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    GROK = "grok"  # xAI; OpenAI-compatible
    GEMINI = "gemini"  # Google; via its OpenAI-compat endpoint


class ProviderSpec(BaseModel):
    """Which LLM serves an arm. base_url covers Ollama / any OpenAI-compatible host."""

    provider: ProviderName
    model: str
    base_url: str | None = None
    temperature: float = 0.1
    max_tokens: int = 1500


class ArmKind(str, Enum):
    LLM = "llm"  # pure-LLM marking: submission + rubric -> score
    SIGNALS = "signals"  # assessment-lens observations: deterministic evidence values
    HYBRID = "hybrid"  # LLM marking with the deterministic signals in context


class ArmSpec(BaseModel):
    """One assessment approach under test."""

    id: str
    kind: ArmKind
    repetitions: int = Field(default=1, ge=1, le=50)
    provider: ProviderSpec | None = None  # required for kind=llm / kind=hybrid

    def model_post_init(self, __context: object) -> None:
        if self.kind in (ArmKind.LLM, ArmKind.HYBRID) and self.provider is None:
            raise ValueError(
                f"arm '{self.id}': kind={self.kind.value} requires a provider"
            )


class ExperimentConfig(BaseModel):
    """One experiment: a rubric, a cohort, the arms to compare.

    Paths are resolved relative to the config file's directory by ``load_config``.
    """

    name: str
    rubric: Path
    submissions: Path
    max_score: float = 100.0
    human_marks: Path | None = Field(
        default=None,
        description="Optional CSV (submission_id,mark) of human ground-truth marks.",
    )
    arms: list[ArmSpec] = Field(min_length=1)


# --- Result side (output) ----------------------------------------------------
class GradeRun(BaseModel):
    """One LLM grading call. score=None means extraction failed (kept, not hidden)."""

    submission_id: str
    arm_id: str
    run_index: int
    score: float | None = None
    max_score: float
    rationale: str = ""
    raw_response: str = ""
    error: str = ""


class RunStats(BaseModel):
    """Consistency statistics over one arm's repeated runs for one submission."""

    n: int
    mean: float
    median: float
    std_dev: float = Field(description="Sample standard deviation (n-1).")
    coefficient_of_variation: float
    min: float
    max: float
    reliability: float = Field(
        description="1 - CV, floored at 0. A rough 'how repeatable was this arm' index."
    )


class SignalReading(BaseModel):
    """One deterministic evidence value from the signals arm."""

    submission_id: str
    criterion_id: str
    signal: str
    value: object | None = None


class ArmOutcome(BaseModel):
    """Everything one arm produced for one submission."""

    submission_id: str
    arm_id: str
    runs: list[GradeRun] = Field(default_factory=list)
    stats: RunStats | None = None
    signals: list[SignalReading] = Field(default_factory=list)


class CohortDistinctiveness(BaseModel):
    """One submission's cohort-relative distinctiveness, surfaced from the bench's
    deterministic assessment-lens pass.

    Reuses assessment-lens's neutral, **direction-agnostic** model unchanged: it is
    never a collusion verdict and never a quality judgement — standing apart can
    mean an out-of-the-box answer *or* a thin one. The bench carries it so a
    researcher can ask whether the arms agree *less* (or diverge from the human
    marks) on the cohort's distinctive submissions. Present only when embeddings/
    signals were available (the analyser ``[embeddings]`` extras + lens-embed);
    otherwise the list is simply empty.
    """

    submission_id: str
    distinctiveness: Distinctiveness


class Agreement(BaseModel):
    """Correlation between one measure and the human marks."""

    measure: str = Field(
        description="An arm id (mean score), a dotted signal path, or a distinctiveness measure."
    )
    n: int
    pearson: float | None = None
    spearman: float | None = None


class ExperimentResult(BaseModel):
    """The source-of-truth structured result for one experiment run."""

    name: str
    max_score: float
    submissions: list[str] = Field(default_factory=list)
    outcomes: list[ArmOutcome] = Field(default_factory=list)
    # Per-submission cohort distinctiveness (once per cohort, arm-independent).
    # Empty unless the deterministic pass ran and embeddings/signals were present.
    distinctiveness: list[CohortDistinctiveness] = Field(default_factory=list)
    agreements: list[Agreement] = Field(default_factory=list)
