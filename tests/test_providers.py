"""Provider plumbing: key resolution, .env fallback, and endpoint routing.

The network is never touched — the openai/anthropic SDK clients are replaced
with fakes that record how they were constructed and called.
"""

import sys
import types

import pytest

from assessment_bench import providers
from assessment_bench.models import ProviderName, ProviderSpec
from assessment_bench.providers import LLMUnavailable

_ALL_KEY_VARS = (
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "XAI_API_KEY",
    "GEMINI_API_KEY",
)


@pytest.fixture()
def clean_env(monkeypatch, tmp_path):
    """No provider keys in the environment; cwd moved away from any real .env."""
    for var in _ALL_KEY_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def fake_openai(monkeypatch):
    record = {}

    class Completions:
        def create(self, **kwargs):
            record["create"] = kwargs
            message = types.SimpleNamespace(content="ok. SCORE: 7/10\n")
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=message)]
            )

    class OpenAI:
        def __init__(self, *, api_key, base_url=None):
            record["api_key"] = api_key
            record["base_url"] = base_url
            self.chat = types.SimpleNamespace(completions=Completions())

    module = types.ModuleType("openai")
    module.OpenAI = OpenAI
    monkeypatch.setitem(sys.modules, "openai", module)
    return record


@pytest.fixture()
def fake_anthropic(monkeypatch):
    record = {}

    class Messages:
        def create(self, **kwargs):
            record["create"] = kwargs
            blocks = [
                types.SimpleNamespace(type="text", text="Good. "),
                types.SimpleNamespace(type="tool_use", text=None),
                types.SimpleNamespace(type="text", text="SCORE: 8/10"),
            ]
            return types.SimpleNamespace(content=blocks)

    class Anthropic:
        def __init__(self, *, api_key):
            record["api_key"] = api_key
            self.messages = Messages()

    module = types.ModuleType("anthropic")
    module.Anthropic = Anthropic
    monkeypatch.setitem(sys.modules, "anthropic", module)
    return record


def _spec(provider, **kw):
    return ProviderSpec(provider=provider, model="m", **kw)


# --- key resolution -----------------------------------------------------------
def test_env_var_wins_over_dotenv(clean_env, monkeypatch):
    (clean_env / ".env").write_text("XAI_API_KEY=file-key\n")
    monkeypatch.setenv("XAI_API_KEY", "env-key")
    assert providers.get_api_key(ProviderName.GROK) == "env-key"


def test_dotenv_fallback_strips_quotes_and_comments(clean_env):
    (clean_env / ".env").write_text('# keys\nGEMINI_API_KEY="dotenv-key"\n')
    assert providers.get_api_key(ProviderName.GEMINI) == "dotenv-key"


def test_ollama_needs_no_key(clean_env):
    assert providers.get_api_key(ProviderName.OLLAMA) == "unused"


def test_missing_key_raises_llm_unavailable_naming_the_var(clean_env):
    with pytest.raises(LLMUnavailable, match="XAI_API_KEY"):
        providers.complete("p", system="s", spec=_spec(ProviderName.GROK))


# --- endpoint routing -----------------------------------------------------------
def test_grok_defaults_to_xai_endpoint(clean_env, fake_openai, monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xk")
    out = providers.complete("p", system="s", spec=_spec(ProviderName.GROK))
    assert out == "ok. SCORE: 7/10"
    assert fake_openai["api_key"] == "xk"
    assert fake_openai["base_url"] == "https://api.x.ai/v1"


def test_gemini_defaults_to_openai_compat_shim(clean_env, fake_openai, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gk")
    providers.complete("p", system="s", spec=_spec(ProviderName.GEMINI))
    assert fake_openai["base_url"] == (
        "https://generativelanguage.googleapis.com/v1beta/openai"
    )


def test_openai_uses_sdk_default_endpoint(clean_env, fake_openai, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "ok")
    providers.complete("p", system="s", spec=_spec(ProviderName.OPENAI))
    assert fake_openai["base_url"] is None


def test_explicit_base_url_beats_the_default(clean_env, fake_openai, monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xk")
    spec = _spec(ProviderName.GROK, base_url="http://proxy.local/v1")
    providers.complete("p", system="s", spec=spec)
    assert fake_openai["base_url"] == "http://proxy.local/v1"


def test_ollama_runs_locally_without_a_key(clean_env, fake_openai):
    providers.complete("p", system="s", spec=_spec(ProviderName.OLLAMA))
    assert fake_openai["api_key"] == "unused"
    assert fake_openai["base_url"] == "http://localhost:11434/v1"


def test_openai_compatible_call_shape(clean_env, fake_openai, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "ok")
    spec = _spec(ProviderName.OPENAI, temperature=0.7, max_tokens=99)
    providers.complete("the prompt", system="the system", spec=spec)
    create = fake_openai["create"]
    assert create["model"] == "m"
    assert create["temperature"] == 0.7
    assert create["max_tokens"] == 99
    assert create["messages"] == [
        {"role": "system", "content": "the system"},
        {"role": "user", "content": "the prompt"},
    ]


def test_anthropic_joins_text_blocks_only(clean_env, fake_anthropic, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "ak")
    out = providers.complete("p", system="sys", spec=_spec(ProviderName.ANTHROPIC))
    assert out == "Good. SCORE: 8/10"
    assert fake_anthropic["api_key"] == "ak"
    assert fake_anthropic["create"]["system"] == "sys"
