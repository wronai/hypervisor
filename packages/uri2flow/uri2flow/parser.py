from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import FlowDocument, FlowStep
from .utils import slugify


class FlowParseError(ValueError):
    pass


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    raise FlowParseError(f"after/depends_on must be string or list, got {type(value).__name__}")


def _parse_step(raw: Any) -> FlowStep:
    if isinstance(raw, str):
        return FlowStep(id=None, uri=raw)

    if isinstance(raw, dict):
        # Compact mapping: - browser://chrome/page/open: {url: ...}
        if "uri" not in raw and len(raw) == 1:
            uri, payload = next(iter(raw.items()))
            if payload is None:
                payload = {}
            if not isinstance(payload, dict):
                raise FlowParseError(f"payload for {uri} must be a mapping")
            return FlowStep(id=None, uri=str(uri), payload=payload)

        if "uri" not in raw:
            raise FlowParseError("step mapping must contain 'uri' or be a single URI mapping")

        payload = raw.get("with", raw.get("payload", {})) or {}
        if not isinstance(payload, dict):
            raise FlowParseError(f"payload/with for {raw.get('uri')} must be a mapping")
        after = _as_list(raw.get("after", raw.get("depends_on")))
        return FlowStep(
            id=raw.get("id"),
            uri=str(raw["uri"]),
            payload=payload,
            after=after,
            condition=raw.get("if", raw.get("condition")),
            operation=raw.get("operation"),
            kind=raw.get("kind"),
        )

    raise FlowParseError(f"unsupported step type: {type(raw).__name__}")


def parse_flow(data: dict[str, Any]) -> FlowDocument:
    if "nl2uri" in data and "flow" in data:
        # Accept nl2uri-wrapped compact flow.
        source_prompt = data.get("nl2uri", {}).get("source_prompt")
    else:
        source_prompt = None

    flow_meta = data.get("flow", {})
    if flow_meta is None:
        flow_meta = {}
    if not isinstance(flow_meta, dict):
        raise FlowParseError("flow must be a mapping")

    do = data.get("do") or data.get("steps")
    if not isinstance(do, list) or not do:
        raise FlowParseError("flow must contain non-empty 'do' or 'steps' list")

    flow_id = str(flow_meta.get("id") or slugify(source_prompt or "uri-flow"))
    description = flow_meta.get("description")
    source_prompt = flow_meta.get("source_prompt") or source_prompt

    steps = [_parse_step(item) for item in do]
    return FlowDocument(id=flow_id, description=description, source_prompt=source_prompt, steps=steps)


def load_flow(path: str | Path) -> FlowDocument:
    with Path(path).open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise FlowParseError("flow document must be a YAML mapping")
    return parse_flow(data)
