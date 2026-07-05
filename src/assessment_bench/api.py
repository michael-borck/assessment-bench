"""HTTP face of the bench — what a desktop shell (or any UI) talks to.

Experiments run in a background worker thread; the UI polls progress. The
registry is in-memory and process-local: this server fronts one researcher's
desktop app, not a multi-tenant service. Restarting the server forgets runs —
the durable record is whatever `write_results` put on disk.

  POST /experiments              -> {id}            (starts a run)
  GET  /experiments              -> [{id, name, status, ...}]
  GET  /experiments/{id}         -> status + progress lines
  GET  /experiments/{id}/result  -> ExperimentResult (202 while running)
  GET  /health, GET /manifest    -> the family contract routes
"""

from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from lens_contract import add_contract_routes, add_cors
from pydantic import BaseModel, Field

from .experiment import run_experiment
from .manifest import MANIFEST
from .models import ExperimentConfig, ExperimentResult
from .report import write_results

app = FastAPI(title=MANIFEST["name"], version=MANIFEST["version"])
add_contract_routes(app, MANIFEST)
add_cors(app, env_prefix="ASSESSMENT_BENCH")

# One experiment at a time: arms hammer LLM APIs and the analyser stack; a
# researcher's desktop doesn't want two cohorts interleaving.
_executor = ThreadPoolExecutor(max_workers=1)


class _Run:
    def __init__(self, config: ExperimentConfig) -> None:
        self.id = uuid.uuid4().hex[:12]
        self.config = config
        self.status = "queued"  # queued | running | done | failed
        self.progress: list[str] = []
        self.result: ExperimentResult | None = None
        self.error: str = ""
        self.lock = threading.Lock()

    def say(self, msg: str) -> None:
        with self.lock:
            self.progress.append(msg)

    def summary(self) -> dict:
        with self.lock:
            return {
                "id": self.id,
                "name": self.config.name,
                "status": self.status,
                "progress": list(self.progress),
                "error": self.error,
            }


_runs: dict[str, _Run] = {}


class StartExperiment(BaseModel):
    """POST /experiments body: a full experiment config with absolute paths.

    The server resolves nothing relative — the UI owns the filesystem dialogue
    and sends absolute paths. ``out`` is where results land on disk.
    """

    config: ExperimentConfig
    out: Path | None = Field(default=None, description="Folder for result files; omit to skip writing.")


def _execute(run: _Run, out: Path | None) -> None:
    with run.lock:
        run.status = "running"
    try:
        result = run_experiment(run.config, progress=run.say)
        if out is not None:
            written = write_results(result, out)
            run.say("wrote " + ", ".join(str(p) for p in written))
        with run.lock:
            run.result = result
            run.status = "done"
    except Exception as exc:
        with run.lock:
            run.error = str(exc)
            run.status = "failed"


@app.post("/experiments", status_code=202)
def start_experiment(body: StartExperiment) -> dict:
    run = _Run(body.config)
    _runs[run.id] = run
    _executor.submit(_execute, run, body.out)
    return {"id": run.id}


@app.get("/experiments")
def list_experiments() -> list[dict]:
    return [run.summary() for run in _runs.values()]


@app.get("/experiments/{run_id}")
def get_experiment(run_id: str) -> dict:
    run = _runs.get(run_id)
    if run is None:
        raise HTTPException(404, f"no experiment {run_id}")
    return run.summary()


@app.get("/experiments/{run_id}/result")
def get_result(run_id: str):
    run = _runs.get(run_id)
    if run is None:
        raise HTTPException(404, f"no experiment {run_id}")
    with run.lock:
        if run.status == "failed":
            raise HTTPException(500, run.error)
        if run.result is None:
            return JSONResponse({"status": run.status}, status_code=202)
        return run.result.model_dump(mode="json")
