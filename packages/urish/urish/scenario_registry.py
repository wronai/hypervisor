from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


def _repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / "agents").exists():
            return candidate
    return current


def _registry_paths() -> tuple[Path, ...]:
    configured = os.environ.get("URISH_SCENARIO_REGISTRY", "").strip()
    if configured:
        paths: list[Path] = []
        for raw in configured.split(os.pathsep):
            if raw.strip():
                paths.append(Path(raw).expanduser())
        return tuple(paths)
    root = _repo_root()
    domain_paths = sorted(
        path for path in (root / "domains").glob("*") if path.is_dir()
    )
    paths: list[Path] = [root / "agents" / "scenarios", *domain_paths]
    return tuple(paths)


def _markpact_domain_readmes(root: Path) -> list[Path]:
    domains = root / "domains"
    if not domains.is_dir():
        return []
    return sorted(path for path in domains.glob("*/README.md") if path.is_file())


def _load_markpact_registries(root: Path) -> list[dict[str, Any]]:
    try:
        from uri2pact.scenarios import load_markpact_scenario_registry_dicts
    except ImportError:
        return []
    registries: list[dict[str, Any]] = []
    for readme in _markpact_domain_readmes(root):
        try:
            rel = readme.relative_to(root).as_posix()
            # Prefer file:// for absolute references to generated markpact READMEs
            ref = f"file://{readme.as_posix()}" if readme.is_absolute() else f"markpact://{rel}"
            registries.extend(load_markpact_scenario_registry_dicts(ref, root=root))
        except (OSError, ValueError, yaml.YAMLError):
            continue
    return registries


def _registry_key(registry: dict[str, Any]) -> str:
    metadata = registry.get("metadata") or {}
    return str(metadata.get("id") or metadata.get("source") or registry.get("intent_kind") or "")


def _load_exported_scenarios(readme: Path, root: Path) -> list[dict[str, Any]]:
    """Load scenarios from markpact README (file:// or markpact:// ref)."""
    try:
        from uri2pact.scenarios import load_markpact_scenario_dicts

        rel = readme.relative_to(root).as_posix()
        ref = f"file://{readme.as_posix()}" if readme.is_absolute() else f"markpact://{rel}"
        exported = load_markpact_scenario_dicts(ref, root=root)
        return [item for item in (exported or []) if isinstance(item, dict)]
    except (ImportError, OSError, ValueError, yaml.YAMLError):
        return []

def _merge_scenarios(existing: list[dict[str, Any]], exported: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge exported scenarios into existing, dedup by id."""
    scenarios = list(existing or [])
    known = {str(item.get("id")) for item in scenarios if isinstance(item, dict)}
    for item in exported:
        sid = str(item.get("id") or "")
        if sid and sid not in known:
            scenarios.append(item)
            known.add(sid)
    return scenarios

def _merge_markpact_scenarios(registry: dict[str, Any], root: Path) -> dict[str, Any]:
    metadata = registry.get("metadata") or {}
    readme_rel = metadata.get("markpact_readme")
    if not readme_rel:
        return registry
    readme = root / str(readme_rel)
    if not readme.is_file():
        return registry
    exported = _load_exported_scenarios(readme, root)
    if not exported:
        return registry
    merged = dict(registry)
    existing = list(merged.get("scenarios") or [])
    merged["scenarios"] = _merge_scenarios(existing, exported)
    return merged


def _iter_yaml_files(path: Path) -> list[Path]:
    resolved = path if path.is_absolute() else (_repo_root() / path)
    if resolved.is_file():
        return [resolved]
    if resolved.is_dir():
        return sorted(
            item
            for item in resolved.glob("*.yaml")
            if item.name.lower() != "readme.yaml"
        )
    return []


@lru_cache(maxsize=1)
def load_scenario_registries() -> tuple[dict[str, Any], ...]:
    root = _repo_root()
    registries: dict[str, dict[str, Any]] = {}
    for reg in _load_markpact_registries(root):
        key = _registry_key(reg)
        if key:
            metadata = reg.setdefault("metadata", {})
            metadata.setdefault("source", metadata.get("markpact_readme") or key)
            registries[key] = _merge_markpact_scenarios(reg, root)
    for path_root in _registry_paths():
        for path in _iter_yaml_files(path_root):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if not isinstance(data, dict):
                continue
            if data.get("kind") != "urish.scenario_registry":
                continue
            metadata = data.setdefault("metadata", {})
            source = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
            metadata.setdefault("source", source)
            merged = _merge_markpact_scenarios(data, root)
            key = _registry_key(merged)
            registries[key or source] = merged
    return tuple(registries.values())


def clear_scenario_registry_cache() -> None:
    load_scenario_registries.cache_clear()


def _normalize_prompt(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r'^[„""\']+|[„""\']+$', "", cleaned)
    return cleaned.lower()


def _render_template(value: str, context: dict[str, Any]) -> str:
    rendered = value
    for key, item in context.items():
        rendered = rendered.replace("{" + key + "}", str(item))
    return rendered


def _render_list(values: list[Any] | tuple[Any, ...], context: dict[str, Any]) -> list[str]:
    return [_render_template(str(value), context) for value in values]


def _agent_id(deployment_id: str | None) -> str | None:
    if not deployment_id:
        return None
    return deployment_id.split(".")[0] if deployment_id.endswith(".local") else deployment_id


def _context_for(
    registry: dict[str, Any],
    *,
    subtype: str,
    deployment_id: str | None = None,
    scenario_id: str | None = None,
    prompt: str = "",
) -> dict[str, Any]:
    deployment = deployment_id or registry.get("default_deployment_id") or ""
    agent_id = _agent_id(deployment) or ""
    return {
        "deployment_id": deployment,
        "agent_id": agent_id,
        "subtype": subtype,
        "scenario_id": scenario_id or "",
        "prompt": prompt,
    }


def _deployment_from_prompt(prompt: str) -> str | None:
    match = re.search(r"\b([\w][\w-]*-agent\.local)\b", prompt, re.I)
    if match:
        return match.group(1)
    return None


def scenario_registries_for_kind(kind: str) -> list[dict[str, Any]]:
    return [item for item in load_scenario_registries() if item.get("intent_kind") == kind]


def scenario_by_id(scenario_id: str, *, kind: str | None = None) -> dict[str, Any] | None:
    for registry in load_scenario_registries():
        if kind and registry.get("intent_kind") != kind:
            continue
        for scenario in registry.get("scenarios") or []:
            if scenario.get("id") == scenario_id:
                return _with_registry_meta(scenario, registry)
    return None


def scenarios_for_kind(kind: str) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for registry in scenario_registries_for_kind(kind):
        scenarios.extend(
            _with_registry_meta(scenario, registry)
            for scenario in registry.get("scenarios") or []
        )
    return scenarios


def _with_registry_meta(scenario: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    metadata = registry.get("metadata") or {}
    return {
        **scenario,
        "_registry_id": metadata.get("id"),
        "_registry_source": metadata.get("source"),
        "_registry_profile": registry.get("profile"),
        "_registry_kind": registry.get("intent_kind"),
        "_registry_default_deployment_id": registry.get("default_deployment_id"),
        "_registry_markpact_readme": metadata.get("markpact_readme"),
        "_registry_artifacts": registry.get("artifacts") or {},
    }


def _score_scenario_against(scenario: dict[str, Any], lower: str) -> int:
    """Pure scoring helper. Extracted to keep match_scenario low CC."""
    score = 0
    for pattern in scenario.get("needles") or []:
        if re.search(str(pattern), lower, re.I):
            score += 1
    chat_prompt = str(scenario.get("chat_prompt") or "")
    chat_norm = _normalize_prompt(chat_prompt)
    if chat_norm and (lower == chat_norm or lower in chat_norm or chat_norm in lower):
        score += 3
    return score


def match_scenario(prompt: str, *, kind: str | None = None) -> dict[str, Any] | None:
    lower = _normalize_prompt(prompt)
    if not lower:
        return None

    best: dict[str, Any] | None = None
    best_score = 0
    for registry in load_scenario_registries():
        if kind and registry.get("intent_kind") != kind:
            continue
        for raw_scenario in registry.get("scenarios") or []:
            scenario = _with_registry_meta(raw_scenario, registry)
            score = _score_scenario_against(scenario, lower)
            if score > best_score:
                best_score = score
                best = scenario

    if best_score == 0:
        return None
    return best


def _matches_any(patterns: list[Any] | tuple[Any, ...], text: str) -> bool:
    return any(re.search(str(pattern), text, re.I) for pattern in patterns)


def _infer_subtype(registry: dict[str, Any], prompt: str) -> str:
    lower = _normalize_prompt(prompt)
    for rule in registry.get("subtype_rules") or []:
        if _matches_any(rule.get("patterns") or [], lower):
            return str(rule.get("subtype"))
    return str(registry.get("fallback_subtype") or "general")


def _planned_uris_for(
    registry: dict[str, Any],
    subtype: str,
    context: dict[str, Any],
) -> list[str]:
    templates = (registry.get("uri_templates") or {}).get(subtype)
    if templates is None:
        templates = (registry.get("uri_templates") or {}).get(registry.get("fallback_subtype"))
    return _render_list(list(templates or []), context)


def next_steps_for_subtype(
    kind: str,
    subtype: str,
    *,
    deployment_id: str | None = None,
    scenario_id: str | None = None,
) -> list[str]:
    registries = scenario_registries_for_kind(kind)
    if not registries:
        return []
    registry = registries[0]
    context = _context_for(
        registry,
        subtype=subtype,
        deployment_id=deployment_id,
        scenario_id=scenario_id,
    )
    templates = (registry.get("next_step_templates") or {}).get(subtype)
    if templates is None:
        templates = (registry.get("next_step_templates") or {}).get(
            registry.get("fallback_subtype")
        )
    return _render_list(list(templates or []), context)


def next_steps_for_intent(intent: dict[str, Any]) -> list[str]:
    values = intent.get("next_steps")
    if isinstance(values, list):
        return [str(value) for value in values]
    kind = str(intent.get("kind") or "")
    subtype = str(intent.get("subtype") or "")
    return next_steps_for_subtype(
        kind,
        subtype,
        deployment_id=intent.get("deployment_id"),
        scenario_id=intent.get("scenario_id"),
    )


def scenario_to_intent(scenario: dict[str, Any]) -> dict[str, Any]:
    deployment_id = (
        scenario.get("deployment_id")
        or scenario.get("_registry_default_deployment_id")
        or "agent.local"
    )
    subtype = str(scenario["subtype"])
    agent_id = _agent_id(str(deployment_id))
    planned_uris = [str(item) for item in scenario.get("planned_uris") or []]
    next_steps = [str(item) for item in scenario.get("next_steps") or []]
    return {
        "kind": scenario.get("_registry_kind"),
        "subtype": subtype,
        "profile": scenario.get("_registry_profile"),
        "scenario_id": scenario.get("id"),
        "agent_id": agent_id,
        "deployment_id": deployment_id,
        "ecosystem_id": None,
        "dashboard_port": None,
        "uri": planned_uris[0] if planned_uris else None,
        "planned_uris": planned_uris,
        "next_steps": next_steps,
        "human_in_the_loop": bool(scenario.get("human_in_the_loop", False)),
        "registry_id": scenario.get("_registry_id"),
        "registry_source": scenario.get("_registry_source"),
        "markpact_readme": scenario.get("_registry_markpact_readme"),
        "artifacts": scenario.get("_registry_artifacts") or {},
    }


def try_scenario_intent(prompt: str, *, kind: str | None = None) -> dict[str, Any] | None:
    text = prompt.strip()
    if not text:
        return None

    scenario = match_scenario(text, kind=kind)
    if scenario:
        return scenario_to_intent(scenario)

    lower = _normalize_prompt(text)
    for registry in load_scenario_registries():
        if kind and registry.get("intent_kind") != kind:
            continue
        if not _matches_any(registry.get("context_patterns") or [], lower):
            continue
        subtype = _infer_subtype(registry, text)
        deployment_id = _deployment_from_prompt(lower) or registry.get("default_deployment_id")
        context = _context_for(
            registry,
            subtype=subtype,
            deployment_id=str(deployment_id) if deployment_id else None,
            prompt=text,
        )
        uris = _planned_uris_for(registry, subtype, context)
        next_steps = next_steps_for_subtype(
            str(registry.get("intent_kind")),
            subtype,
            deployment_id=context["deployment_id"],
        )
        metadata = registry.get("metadata") or {}
        return {
            "kind": registry.get("intent_kind"),
            "subtype": subtype,
            "profile": registry.get("profile"),
            "scenario_id": None,
            "agent_id": context["agent_id"],
            "deployment_id": context["deployment_id"],
            "ecosystem_id": None,
            "dashboard_port": None,
            "uri": uris[0] if uris else None,
            "planned_uris": uris,
            "next_steps": next_steps,
            "human_in_the_loop": subtype in set(registry.get("human_in_the_loop_subtypes") or []),
            "registry_id": metadata.get("id"),
            "registry_source": metadata.get("source"),
            "markpact_readme": metadata.get("markpact_readme"),
            "artifacts": registry.get("artifacts") or {},
        }
    return None
