"""assessment-bench — benchmark assessment approaches for the lens family.

Runs one cohort through competing assessment arms (pure-LLM marking as the
baseline; assessment-lens signal observations as the approach under study),
with repeated runs, consistency statistics, and agreement against human marks.
**The bench measures; it never marks.**
"""

from .exceptions import AssessmentBenchError
from .experiment import load_config, run_experiment
from .models import (
    Agreement,
    ArmKind,
    ArmOutcome,
    ArmSpec,
    ExperimentConfig,
    ExperimentResult,
    GradeRun,
    ProviderName,
    ProviderSpec,
    RunStats,
    SignalReading,
)
from .report import write_results

__version__ = "0.3.0"

__all__ = [
    "Agreement",
    "ArmKind",
    "ArmOutcome",
    "ArmSpec",
    "AssessmentBenchError",
    "ExperimentConfig",
    "ExperimentResult",
    "GradeRun",
    "ProviderName",
    "ProviderSpec",
    "RunStats",
    "SignalReading",
    "__version__",
    "load_config",
    "run_experiment",
    "write_results",
]
