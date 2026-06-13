# assessment-bench

Part of the [lens family](https://github.com/michael-borck/lens-analysers).

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Benchmark assessment approaches.** Run one cohort through competing
assessment arms — pure-LLM marking (the baseline) and the family's
signal-based observations (`assessment-lens`) — with repeated runs,
consistency statistics, and agreement against human marks.
**The bench measures; it never marks.**

> `assessment-bench` is a *bench* (a measurement product), not an `-analyser`
> and not a marking tool. It exists to answer research questions like: *how
> consistent is LLM marking across repeated runs and providers?* and *which
> deterministic signals actually track human judgement?*

## What it does

```
experiment.yaml (rubric + cohort + arms)
  ├─ llm arm(s)    : submission + rubric → provider → score             × repetitions
  ├─ hybrid arm(s) : submission + rubric + signals → provider → score   × repetitions
  ├─ signals arm   : assessment-lens → evidence values                  (deterministic, once)
  └─ human marks   : optional ground-truth CSV
        ↓
result.json + runs.csv + signals.csv + agreement.csv
  • per-submission consistency: mean / median / std-dev / CV / reliability
  • agreement: Pearson & Spearman of every arm mean and every numeric signal
    against the human marks
```

## Install

```bash
# from source (family layout)
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# the signals arm needs the analyser stack (bundle-analyser CLI on PATH):
uv pip install -e ".[analysers]"

# LLM arms (Anthropic, OpenAI, Ollama, OpenRouter):
uv pip install -e ".[llm]"      # + export ANTHROPIC_API_KEY / OPENAI_API_KEY / ...
```

## Quick start

```bash
assessment-bench init experiment.yaml   # commented example config
# edit: point at your rubric.yaml + submissions/, choose arms
assessment-bench run experiment.yaml -o out/
```

LLM arms specify provider **and** model per arm — comparing
`claude-haiku-4-5` vs `gpt-4o-mini` vs a local `llama3.1` via Ollama is just
three arms in one config.

## Relationship to the family

- **Analysers** generate deterministic signals (assessment-agnostic).
- **assessment-lens** maps signals to a rubric as observations — never scores.
- **assessment-bench** measures both approaches against human judgement. The
  LLM arm produces scores *because that is the approach under test*; the bench
  treats them as data points, not grades for students.

## Status

**v0.3.0** (on PyPI). Working today:

- ✅ Experiment config (YAML) → cohort discovery → arms → structured results
- ✅ LLM arm: multi-provider (anthropic / openai / ollama / openrouter), repeated
  runs, strict `SCORE: x/y` extraction with scaled fallback
- ✅ Signals arm: one `assessment-lens` pass; raw evidence values consumed
  (not the presence-based coverage)
- ✅ Consistency stats (ported from the original Rust prototype) + Pearson/Spearman
  agreement vs human marks
- ✅ Hybrid arm — LLM marking with the deterministic signals in context (one
  assessment-lens pass per cohort, shared across signals/hybrid arms)
- ✅ HTTP API (`assessment-bench serve`, the `[serve]` extra) — health/manifest
  contract routes plus background experiment runs for UIs
- 📋 Desktop shell for non-technical researchers — planned

## Development

```bash
pytest -v
```

## License

MIT — see [LICENSE](LICENSE).
