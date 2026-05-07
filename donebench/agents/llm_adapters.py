from __future__ import annotations

import os
import importlib.util
import time
from dataclasses import dataclass, field
from typing import Any, Mapping


class AdapterUnavailable(RuntimeError):
    """Raised when a live model is configured but cannot be called."""


@dataclass
class CompletionResult:
    text: str
    latency_s: float
    usage: dict[str, Any] = field(default_factory=dict)
    model: str = ""
    provider: str = ""
    attempts: int = 1


@dataclass(frozen=True)
class AdapterStatus:
    available: bool
    reason: str = ""
    env: str | None = None
    blocker: bool = False


@dataclass(frozen=True)
class ProviderDefaults:
    env: str | None = None
    base_url_env: str | None = None
    default_base_url: str | None = None
    litellm_prefix: str | None = None
    requires_key: bool = True


PROVIDERS: dict[str, ProviderDefaults] = {
    "mock": ProviderDefaults(requires_key=False),
    "openai_compatible": ProviderDefaults(env="OPENAI_API_KEY", litellm_prefix="openai"),
    "anthropic": ProviderDefaults(env="ANTHROPIC_API_KEY", litellm_prefix="anthropic"),
    "gemini": ProviderDefaults(env="GEMINI_API_KEY", litellm_prefix="gemini"),
    "openrouter": ProviderDefaults(
        env="OPENROUTER_API_KEY",
        default_base_url="https://openrouter.ai/api/v1",
        litellm_prefix="openrouter",
    ),
    "ollama": ProviderDefaults(
        base_url_env="OLLAMA_BASE_URL",
        default_base_url="http://localhost:11434",
        litellm_prefix="ollama",
        requires_key=False,
    ),
    "vllm": ProviderDefaults(
        base_url_env="VLLM_BASE_URL",
        litellm_prefix="openai",
        requires_key=False,
    ),
}


@dataclass
class MockLLM:
    model: str = "mock"
    provider: str = "mock"

    def complete(self, prompt: str) -> str:
        return "mock completion"

    def complete_with_metadata(self, prompt: str) -> CompletionResult:
        return CompletionResult(text=self.complete(prompt), latency_s=0.0, model=self.model, provider=self.provider)


@dataclass
class ProviderAdapter:
    provider: str
    model: str
    model_id: str | None = None
    base_url: str | None = None
    env: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def defaults(self) -> ProviderDefaults | None:
        return PROVIDERS.get(self.provider)

    @property
    def api_key_env(self) -> str | None:
        if self.env and not self.env.endswith("_BASE_URL"):
            return self.env
        return self.defaults.env if self.defaults else self.env

    @property
    def base_url_env(self) -> str | None:
        if self.env and self.env.endswith("_BASE_URL"):
            return self.env
        return self.defaults.base_url_env if self.defaults else None

    @property
    def resolved_base_url(self) -> str | None:
        if self.base_url_env and os.getenv(self.base_url_env):
            return os.getenv(self.base_url_env)
        if self.base_url:
            return self.base_url
        if self.defaults:
            return self.defaults.default_base_url
        return None

    @property
    def api_key(self) -> str | None:
        if self.api_key_env:
            return os.getenv(self.api_key_env)
        return None

    def status(self) -> AdapterStatus:
        defaults = self.defaults
        if not defaults:
            return AdapterStatus(False, f"unsupported_provider:{self.provider}", blocker=True)
        if self.provider == "mock":
            return AdapterStatus(True)
        if defaults.requires_key and not self.api_key:
            env = self.api_key_env or defaults.env
            return AdapterStatus(False, f"missing_credentials:{env or self.provider}", env=env, blocker=True)
        if not defaults.requires_key and self.provider == "vllm" and not self.resolved_base_url:
            env = self.base_url_env or defaults.base_url_env
            return AdapterStatus(False, f"missing_base_url:{env or self.provider}", env=env, blocker=True)
        if self.provider != "mock" and importlib.util.find_spec("litellm") is None:
            return AdapterStatus(False, "missing_dependency:litellm", blocker=True)
        return AdapterStatus(True)

    def available(self) -> bool:
        return self.status().available

    @property
    def litellm_model(self) -> str:
        prefix = self.defaults.litellm_prefix if self.defaults else None
        if not prefix or self.model.startswith(f"{prefix}/"):
            return self.model
        return f"{prefix}/{self.model}"

    def complete(self, prompt: str) -> str:
        return self.complete_with_metadata(prompt).text

    def complete_with_metadata(self, prompt: str) -> CompletionResult:
        status = self.status()
        if not status.available:
            raise AdapterUnavailable(status.reason)
        try:
            import litellm
        except ImportError as exc:
            raise AdapterUnavailable("Install the optional llm extra to call live providers: pip install -e .[llm]") from exc

        attempts = int(self.extra.get("attempts", 3))
        backoff = float(self.extra.get("retry_backoff_s", 2.0))
        call_extra = {key: value for key, value in self.extra.items() if key not in {"attempts", "retry_backoff_s"}}
        start = time.perf_counter()
        last_exc: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                response = litellm.completion(
                    model=self.litellm_model,
                    messages=[{"role": "user", "content": prompt}],
                    api_base=self.resolved_base_url,
                    api_key=self.api_key,
                    **call_extra,
                )
                raw_usage = getattr(response, "usage", None)
                usage = raw_usage.model_dump() if hasattr(raw_usage, "model_dump") else (dict(raw_usage) if raw_usage else {})
                return CompletionResult(
                    text=response.choices[0].message.content or "",
                    latency_s=time.perf_counter() - start,
                    usage=usage,
                    model=self.model,
                    provider=self.provider,
                    attempts=attempt,
                )
            except Exception as exc:
                last_exc = exc
                if attempt < attempts:
                    time.sleep(backoff * attempt)
        raise AdapterUnavailable(f"completion_failed:{last_exc}") from last_exc


def adapter_from_config(config: Any) -> MockLLM | ProviderAdapter:
    if isinstance(config, Mapping):
        provider = config.get("provider", "mock")
        model = config.get("model", "mock")
        model_id = config.get("id")
        base_url = config.get("base_url")
        env = config.get("env")
        extra = dict(config.get("extra") or {})
    else:
        provider = getattr(config, "provider", "mock")
        model = getattr(config, "model", "mock")
        model_id = getattr(config, "id", None)
        base_url = getattr(config, "base_url", None)
        env = getattr(config, "env", None)
        extra = dict(getattr(config, "extra", {}) or {})
    return make_llm(provider=provider, model=model, model_id=model_id, base_url=base_url, env=env, extra=extra)


def make_llm(
    provider: str = "mock",
    model: str = "mock",
    model_id: str | None = None,
    base_url: str | None = None,
    env: str | None = None,
    extra: dict[str, Any] | None = None,
) -> MockLLM | ProviderAdapter:
    if provider == "mock" or model == "mock":
        return MockLLM(model=model, provider=provider)
    return ProviderAdapter(provider=provider, model=model, model_id=model_id, base_url=base_url, env=env, extra=extra or {})
