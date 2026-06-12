"""Multi-provider LLM completion for the pure-LLM marking arm.

Provider registry adapted from image-analyser's caption providers: Anthropic via
its own SDK; OpenAI, OpenRouter, and Ollama through the openai SDK (the latter
two are OpenAI-compatible endpoints reached via base_url). Key resolution
follows the family pattern — env var first, then a minimal .env fallback.

Everything here is opt-in and degradable: callers catch ``LLMUnavailable`` and
the experiment records the failure instead of dying mid-cohort.
"""

from __future__ import annotations

import os
from pathlib import Path

from .exceptions import AssessmentBenchError
from .models import ProviderName, ProviderSpec

PROVIDER_KEYS = {
    ProviderName.ANTHROPIC: "ANTHROPIC_API_KEY",
    ProviderName.OPENAI: "OPENAI_API_KEY",
    ProviderName.OPENROUTER: "OPENROUTER_API_KEY",
    ProviderName.OLLAMA: None,  # local; no key
}

DEFAULT_BASE_URLS = {
    ProviderName.OPENROUTER: "https://openrouter.ai/api/v1",
    ProviderName.OLLAMA: "http://localhost:11434/v1",
}


class LLMUnavailable(AssessmentBenchError):
    """The [llm] extra is not installed or no API key is configured."""


def _load_env_file() -> None:
    """Minimal .env loader (cwd upward) — no python-dotenv dependency."""
    for parent in [Path.cwd(), *Path.cwd().parents]:
        env_file = parent / ".env"
        if env_file.exists():
            try:
                for line in env_file.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
            except OSError:
                pass
            return


def get_api_key(provider: ProviderName) -> str | None:
    env_var = PROVIDER_KEYS.get(provider)
    if env_var is None:
        return "unused"  # Ollama: openai SDK requires a non-empty key
    if key := os.getenv(env_var):
        return key
    _load_env_file()
    return os.getenv(env_var)


def complete(prompt: str, *, system: str, spec: ProviderSpec) -> str:
    """One marking-style completion against the arm's configured provider."""
    api_key = get_api_key(spec.provider)
    if not api_key:
        raise LLMUnavailable(
            f"No API key for {spec.provider.value} — set {PROVIDER_KEYS[spec.provider]} (env or .env)."
        )

    if spec.provider is ProviderName.ANTHROPIC:
        return _complete_anthropic(prompt, system=system, spec=spec, api_key=api_key)
    return _complete_openai_compatible(prompt, system=system, spec=spec, api_key=api_key)


def _complete_anthropic(prompt: str, *, system: str, spec: ProviderSpec, api_key: str) -> str:
    try:
        import anthropic
    except ImportError as exc:
        raise LLMUnavailable(
            "LLM arms need the [llm] extra: pip install 'assessment-bench[llm]'"
        ) from exc
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=spec.model,
        max_tokens=spec.max_tokens,
        temperature=spec.temperature,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text").strip()


def _complete_openai_compatible(
    prompt: str, *, system: str, spec: ProviderSpec, api_key: str
) -> str:
    try:
        import openai
    except ImportError as exc:
        raise LLMUnavailable(
            "LLM arms need the [llm] extra: pip install 'assessment-bench[llm]'"
        ) from exc
    base_url = spec.base_url or DEFAULT_BASE_URLS.get(spec.provider)
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=spec.model,
        max_tokens=spec.max_tokens,
        temperature=spec.temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return (response.choices[0].message.content or "").strip()
