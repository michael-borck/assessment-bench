"""assessment-bench CLI.

  assessment-bench run experiment.yaml -o out/
  assessment-bench init my-experiment.yaml
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from rich.console import Console

from .exceptions import AssessmentBenchError
from .experiment import load_config, run_experiment
from .report import write_results

console = Console()

_EXAMPLE = Path(__file__).parent / "data" / "example-experiment.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="assessment-bench",
        description="Benchmark assessment approaches over one cohort: pure-LLM marking vs signal-based observation.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run an experiment config over its cohort.")
    run_p.add_argument("config", type=Path, help="Experiment YAML.")
    run_p.add_argument("-o", "--out", type=Path, default=Path("bench-out"), help="Output folder.")

    init_p = sub.add_parser("init", help="Write a commented example experiment config.")
    init_p.add_argument("path", type=Path, nargs="?", default=Path("experiment.yaml"))

    serve_p = sub.add_parser("serve", help="Run the HTTP API (for the desktop shell / UIs).")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8020)

    args = parser.parse_args(argv)

    if args.command == "serve":
        try:
            import uvicorn
        except ImportError:
            console.print("[red]serve needs the [serve] extra:[/red] pip install 'assessment-bench[serve]'")
            return 1
        uvicorn.run("assessment_bench.api:app", host=args.host, port=args.port)
        return 0

    try:
        if args.command == "init":
            if args.path.exists():
                console.print(f"[red]refusing to overwrite {args.path}[/red]")
                return 1
            shutil.copy(_EXAMPLE, args.path)
            console.print(f"✓ wrote {args.path} — edit it, then: assessment-bench run {args.path}")
            return 0

        config = load_config(args.config)
        console.print(
            f"[bold]{config.name}[/bold] — {len(config.arms)} arms, max score {config.max_score:g}"
        )
        result = run_experiment(config, progress=lambda msg: console.print(f"  {msg}"))
        written = write_results(result, args.out)
        console.print(f"✓ {len(result.submissions)} submissions → " + ", ".join(str(p) for p in written))
        if result.agreements:
            console.print("[bold]Agreement with human marks:[/bold]")
            # Undefined correlations sort last; r=0.0 is a real result, not undefined.
            for a in sorted(
                result.agreements,
                key=lambda a: -a.pearson if a.pearson is not None else 2.0,
            ):
                console.print(f"  {a.measure}: r={a.pearson:.3f} rho={a.spearman:.3f} (n={a.n})"
                              if a.pearson is not None and a.spearman is not None
                              else f"  {a.measure}: undefined (n={a.n})")
        return 0
    except AssessmentBenchError as exc:
        console.print(f"[red]error:[/red] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
