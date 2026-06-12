"""Result writers: one JSON source of truth + flat CSVs for spreadsheet people."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import ExperimentResult


def write_results(result: ExperimentResult, out_dir: Path) -> list[Path]:
    """Write result.json, runs.csv, signals.csv, agreement.csv. Returns written paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    json_path = out_dir / "result.json"
    json_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2))
    written.append(json_path)

    runs_path = out_dir / "runs.csv"
    with open(runs_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["submission", "arm", "run", "score", "max_score", "error"])
        for outcome in result.outcomes:
            for run in outcome.runs:
                writer.writerow(
                    [run.submission_id, run.arm_id, run.run_index, run.score, run.max_score, run.error]
                )
    written.append(runs_path)

    signals_path = out_dir / "signals.csv"
    with open(signals_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["submission", "arm", "criterion", "signal", "value"])
        for outcome in result.outcomes:
            for reading in outcome.signals:
                writer.writerow(
                    [
                        reading.submission_id,
                        outcome.arm_id,
                        reading.criterion_id,
                        reading.signal,
                        json.dumps(reading.value, default=str),
                    ]
                )
    written.append(signals_path)

    if result.agreements:
        agreement_path = out_dir / "agreement.csv"
        with open(agreement_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["measure", "n", "pearson", "spearman"])
            for a in result.agreements:
                writer.writerow([a.measure, a.n, a.pearson, a.spearman])
        written.append(agreement_path)

    return written
