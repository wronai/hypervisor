from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from uri3.config.uri_yaml import load_uri_yaml
from uri3.resolvers.llm_resolver import resolve_llm


def _repo_root(root: Path | None = None) -> Path:
    if root is not None:
        return Path(root)
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "config" / "llm.uri.yaml").exists():
            return parent
    return Path.cwd()


def llm_config_path(root: Path | None = None) -> Path:
    return _repo_root(root) / "config" / "llm.uri.yaml"


def load_llm_config(root: Path | None = None) -> dict[str, Any]:
    path = llm_config_path(root)
    if not path.exists():
        return {"version": 1, "defaults": {"profile": "default"}, "profiles": {}}
    return load_uri_yaml(path)


def _parse_llm_query(model_uri: str) -> dict[str, Any]:
    parsed = urlparse(model_uri)
    query = parse_qs(parsed.query, keep_blank_values=True)
    result: dict[str, Any] = {}
    if "temp" in query or "temperature" in query:
        raw = (query.get("temp") or query.get("temperature") or ["0.1"])[0]
        result["temperature"] = float(raw)
    if "max_tokens" in query:
        result["max_tokens"] = int(query["max_tokens"][0])
    if "format" in query:
        result["format"] = query["format"][0]
    return result


@dataclass(frozen=True)
class LlmProfile:
    name: str
    model_uri: str
    model: str
    api_key: str | None
    provider: str | None
    base_url: str
    temperature: float = 0.1
    max_tokens: int = 8000
    response_format: str | None = None
    config_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "model_uri": self.model_uri,
            "model": self.model,
            "provider": self.provider,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": self.response_format,
            "config_path": self.config_path,
            "api_key_set": bool(self.api_key),
        }


def resolve_llm_profile(
    profile_name: str | None = None,
    *,
    root: Path | None = None,
    resolve_secrets: bool = True,
) -> LlmProfile:
    data = load_llm_config(root)
    profiles = data.get("profiles") or {}
    chosen = (
        profile_name
        or os.environ.get("DEFAULT_LLM_PROFILE")
        or (data.get("defaults") or {}).get("profile", "default")
    )
    profile = profiles.get(chosen) or profiles.get("default") or {}
    model_uri = str(profile.get("model") or "llm://openrouter/qwen/qwen3-coder-next")
    llm_data = resolve_llm(model_uri)
    query = _parse_llm_query(model_uri)
    model = str(llm_data.get("model") or "")
    if model.startswith("openrouter/"):
        model = model.removeprefix("openrouter/")
    api_key_uri = profile.get("api_key")
    api_key = None
    if resolve_secrets and isinstance(api_key_uri, str) and api_key_uri.startswith("env://"):
        from uri3.resolvers.env_resolver import resolve_env

        env = resolve_env(api_key_uri)
        api_key = env.get("value")
    return LlmProfile(
        name=chosen,
        model_uri=model_uri,
        model=model,
        api_key=api_key,
        provider=str(profile.get("provider") or llm_data.get("provider") or ""),
        base_url=str(llm_data.get("base_url") or os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")).rstrip("/"),
        temperature=float(query.get("temperature", os.getenv("LLM_TEMPERATURE", "0.1"))),
        max_tokens=int(query.get("max_tokens", os.getenv("LLM_MAX_TOKENS", "8000"))),
        response_format=query.get("format"),
        config_path=str(llm_config_path(root)),
    )
