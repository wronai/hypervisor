from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from uri3.config.uri_yaml import load_uri_yaml, resolve_uri_values


def _repo_config_dir(root: Path | None = None) -> Path:
    if root is not None:
        return Path(root) / "config"
    from hypervisor.paths import find_repo_root

    return find_repo_root() / "config"


def load_deployments_uri_config(root: Path | None = None) -> dict[str, Any]:
    path = _repo_config_dir(root) / "deployments.uri.yaml"
    if not path.exists():
        return {"version": 1, "defaults": {}, "deployments": {}}
    return load_uri_yaml(path)


def load_runtime_uri_config(root: Path | None = None) -> dict[str, Any]:
    path = _repo_config_dir(root) / "runtime.uri.yaml"
    if not path.exists():
        return {"version": 1, "defaults": {}, "agents": {}}
    return load_uri_yaml(path)


def resolve_deployment_env(
    deployment_id: str,
    agent_ref: str,
    deployment_env: dict[str, Any] | None = None,
    *,
    root: Path | None = None,
    resolve_secrets: bool = True,
) -> dict[str, str]:
    deployments_cfg = load_deployments_uri_config(root)
    runtime_cfg = load_runtime_uri_config(root)
    merged: dict[str, Any] = {}
    merged.update(deployments_cfg.get("defaults", {}).get("env") or {})
    agent_id = agent_ref.removeprefix("agent://")
    agent_runtime = (runtime_cfg.get("agents") or {}).get(agent_id) or {}
    if agent_runtime.get("resource_runtime_url"):
        merged.setdefault("RESOURCE_RUNTIME_URL", agent_runtime["resource_runtime_url"])
    elif runtime_cfg.get("defaults", {}).get("resource_runtime_url"):
        merged.setdefault("RESOURCE_RUNTIME_URL", runtime_cfg["defaults"]["resource_runtime_url"])
    per_deployment = (deployments_cfg.get("deployments") or {}).get(deployment_id) or {}
    merged.update(per_deployment.get("env") or {})
    merged.update(deployment_env or {})
    env: dict[str, str] = {}
    for key, value in merged.items():
        if value is None:
            continue
        if isinstance(value, str) and value.startswith(("env://", "secret://")):
            resolved = resolve_uri_values(value, resolve_secrets=resolve_secrets)
            if resolved is not None:
                env[str(key)] = str(resolved)
            continue
        env[str(key)] = str(value)
    return env


def default_log_uri(deployment_id: str, agent_ref: str, *, root: Path | None = None) -> str:
    runtime_cfg = load_runtime_uri_config(root)
    agent_id = agent_ref.removeprefix("agent://")
    agent_runtime = (runtime_cfg.get("agents") or {}).get(agent_id) or {}
    stream = agent_runtime.get("log_stream") or runtime_cfg.get("defaults", {}).get("log_stream") or "hypervisor"
    return f"log://{stream}?grep={deployment_id}"
