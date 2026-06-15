from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from urish.backends.call import call_uri
from urish.policy import classify_uri

_SYSTEM_API_SCHEMES = {"health", "view", "repair", "runtime", "log"}
_ProofSpec = tuple[str, bool, str, str, bool]


@dataclass(frozen=True)
class _ProofFlags:
    scheme: str
    system_api: bool
    dashboard_ok: bool
    repair_available: bool
    ticket_available: bool
    hypervisor_uri: bool


def _check(
    name: str,
    *,
    ok: bool,
    status: str,
    detail: str = "",
    required: bool = True,
) -> dict[str, Any]:
    return {
        "name": name,
        "ok": bool(ok),
        "status": status,
        "detail": detail,
        "required": required,
    }


def _system_body(call_result: dict[str, Any]) -> dict[str, Any]:
    data = call_result.get("data")
    return data if isinstance(data, dict) else {}


def _view_payload(system_body: dict[str, Any]) -> dict[str, Any]:
    data = system_body.get("data")
    return data if isinstance(data, dict) else system_body


def _actions(system_body: dict[str, Any]) -> list[dict[str, Any]]:
    payload = _view_payload(system_body)
    raw_actions = payload.get("actions") or system_body.get("actions") or []
    return [item for item in raw_actions if isinstance(item, dict)]


def _has_action(actions: list[dict[str, Any]], *, kind: str, scheme: str) -> bool:
    for action in actions:
        uri = str(action.get("uri") or "")
        if action.get("kind") == kind or uri.startswith(f"{scheme}://"):
            return True
    return False


def _call_proof_context(
    target: str,
    *,
    payload: dict[str, Any] | None,
    dry_run: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]], str, bool]:
    parsed = urlparse(target)
    action = classify_uri(target)
    proof_dry_run = dry_run or action != "read"
    call_result = call_uri(target, payload or {}, dry_run=proof_dry_run)
    system_body = _system_body(call_result)
    view_payload = _view_payload(system_body)
    actions = _actions(system_body)
    return call_result, system_body, view_payload, actions, action, proof_dry_run


def _evaluate_chat_check(call_result: dict[str, Any]) -> tuple[bool, str]:
    try:
        from hypervisor_dashboard_agent.chat_format import format_uri_result_markdown

        chat_markdown = format_uri_result_markdown(call_result)
        chat_ok = bool(chat_markdown.strip())
        return chat_ok, "markdown summary available" if chat_ok else "empty markdown"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _target_status(view_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in {
            "service": view_payload.get("service_status"),
            "process": view_payload.get("process_status"),
            "health": view_payload.get("health_status"),
            "recommended_action": view_payload.get("recommended_action"),
        }.items()
        if value not in {None, ""}
    }


def _dashboard_view_ok(system_body: dict[str, Any], result_type: str) -> bool:
    return bool(
        system_body.get("content_type") == "text/html"
        or system_body.get("html")
        or system_body.get("view_uri")
        or result_type == "view"
    )


def _proof_flags(
    *,
    target: str,
    parsed,
    system_body: dict[str, Any],
    result_type: str,
    actions: list[dict[str, Any]],
) -> _ProofFlags:
    scheme = parsed.scheme
    return _ProofFlags(
        scheme=scheme,
        system_api=scheme in _SYSTEM_API_SCHEMES or target.startswith("resource://dashboard"),
        dashboard_ok=_dashboard_view_ok(system_body, result_type),
        repair_available=_has_action(actions, kind="repair", scheme="repair"),
        ticket_available=_has_action(actions, kind="mutation", scheme="ticket"),
        hypervisor_uri=scheme in _SYSTEM_API_SCHEMES,
    )


def _shell_proof_specs(
    *,
    target: str,
    action: str,
    proof_dry_run: bool,
    chat_ok: bool,
    chat_detail: str,
    flags: _ProofFlags,
) -> list[_ProofSpec]:
    return [
        ("cli", True, "ok", "uri proof / taskinity proof", True),
        ("uri", bool(flags.scheme), flags.scheme or "missing", target, True),
        (
            "policy",
            True,
            "dry_run" if proof_dry_run else "readonly",
            f"{action} URI" + ("; mutation not executed" if action != "read" else ""),
            True,
        ),
        ("chat", chat_ok, "ok" if chat_ok else "failed", chat_detail, True),
    ]


def _runtime_proof_specs(
    *,
    call_result: dict[str, Any],
    flags: _ProofFlags,
    ctx: dict[str, Any],
) -> list[_ProofSpec]:
    transport = ctx.get("transport", "")
    workflow_status = ctx.get("workflow_status", "")
    service_status = ctx.get("service_status", "")
    result_type = ctx.get("result_type", "")
    return [
        (
            "web_api",
            flags.system_api,
            "ok" if flags.system_api else "skipped",
            "/api/uri/call compatible" if flags.system_api else "non-system URI",
            flags.system_api,
        ),
        (
            "runtime",
            bool(call_result.get("ok")),
            f"{workflow_status}/{service_status}".strip("/"),
            transport or result_type,
            True,
        ),
        (
            "hypervisor",
            transport == "hypervisor:system_uri" or flags.hypervisor_uri,
            "ok" if flags.hypervisor_uri else "skipped",
            result_type or "not a hypervisor system URI",
            flags.hypervisor_uri,
        ),
    ]


def _view_proof_specs(*, flags: _ProofFlags, system_body: dict[str, Any]) -> list[_ProofSpec]:
    return [
        (
            "dashboard_view",
            flags.dashboard_ok,
            "ok" if flags.dashboard_ok else "skipped",
            str(system_body.get("view_uri") or system_body.get("content_type") or ""),
            flags.scheme == "view",
        ),
    ]


def _optional_action_specs(*, flags: _ProofFlags) -> list[_ProofSpec]:
    return [
        (
            "repair_action",
            flags.repair_available,
            "available" if flags.repair_available else "missing",
            "repair:// action" if flags.repair_available else "",
            False,
        ),
        (
            "ticket_action",
            flags.ticket_available,
            "available" if flags.ticket_available else "missing",
            "ticket:// action" if flags.ticket_available else "",
            False,
        ),
    ]


def _materialize_checks(specs: list[_ProofSpec]) -> list[dict[str, Any]]:
    return [_check(name, ok=ok, status=status, detail=detail, required=req) for name, ok, status, detail, req in specs]


def _build_proof_checks(
    *,
    target: str,
    parsed,
    action: str,
    proof_dry_run: bool,
    call_result: dict[str, Any],
    system_body: dict[str, Any],
    chat_ok: bool,
    chat_detail: str,
    ctx: dict[str, Any],
) -> list[dict[str, Any]]:
    actions = ctx.get("actions") or []
    flags = _proof_flags(
        target=target,
        parsed=parsed,
        system_body=system_body,
        result_type=str(ctx.get("result_type") or ""),
        actions=actions,
    )
    specs = [
        *_shell_proof_specs(
            target=target,
            action=action,
            proof_dry_run=proof_dry_run,
            chat_ok=chat_ok,
            chat_detail=chat_detail,
            flags=flags,
        ),
        *_runtime_proof_specs(call_result=call_result, flags=flags, ctx=ctx),
        *_view_proof_specs(flags=flags, system_body=system_body),
        *_optional_action_specs(flags=flags),
    ]
    return _materialize_checks(specs)


def _collect_proof_context(
    target: str,
    call_result: dict[str, Any],
    system_body: dict[str, Any],
    *,
    view_payload: dict[str, Any] | None = None,
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    transport = (call_result.get("meta") or {}).get("transport", "")
    workflow_status = str(call_result.get("workflow_status") or "")
    service_status = str(call_result.get("service_result_status") or "")
    result_type = str(call_result.get("result_type") or system_body.get("result_type") or "")
    ctx = {
        "transport": transport,
        "workflow_status": workflow_status,
        "service_status": service_status,
        "result_type": result_type,
    }
    if view_payload is not None:
        ctx["view_payload"] = view_payload
    if actions is not None:
        ctx["actions"] = actions
    return ctx


def proof_uri(
    target: str,
    *,
    payload: dict[str, Any] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Prove that one URI crosses the shell/API/runtime/view boundary."""
    started = time.perf_counter()
    parsed = urlparse(target)
    call_result, system_body, view_payload, actions, action, proof_dry_run = _call_proof_context(
        target,
        payload=payload,
        dry_run=dry_run,
    )
    chat_ok, chat_detail = _evaluate_chat_check(call_result)
    ctx = _collect_proof_context(
        target,
        call_result,
        system_body,
        view_payload=view_payload,
        actions=actions,
    )
    checks = _build_proof_checks(
        target=target,
        parsed=parsed,
        action=action,
        proof_dry_run=proof_dry_run,
        call_result=call_result,
        system_body=system_body,
        chat_ok=chat_ok,
        chat_detail=chat_detail,
        ctx=ctx,
    )
    required_ok = all(item["ok"] for item in checks if item.get("required", True))
    duration_ms = int((time.perf_counter() - started) * 1000)

    return {
        "ok": required_ok,
        "workflow_status": "completed" if required_ok else "failed",
        "execution_status": "completed" if required_ok else "failed",
        "service_result_status": "succeeded" if required_ok else "failed",
        "result_type": "proof",
        "data": {
            "uri": target,
            "action": action,
            "proof_dry_run": proof_dry_run,
            "target_status": _target_status(view_payload),
            "checks": checks,
            "call": call_result,
        },
        "meta": {"runtime": "urish", "transport": "proof", "duration_ms": duration_ms},
    }


def _format_proof_check_line(check: dict[str, Any]) -> str:
    marker = "OK" if check.get("ok") else ("-" if not check.get("required", True) else "FAIL")
    detail = f" · {check['detail']}" if check.get("detail") else ""
    return f"{check.get('name')}: {marker} ({check.get('status')}){detail}"


def render_proof_text(result: dict[str, Any]) -> str:
    try:
        from uri3.results.envelope import unwrap_data

        data = unwrap_data(result)
    except Exception:  # noqa: BLE001
        data = result.get("data") if isinstance(result.get("data"), dict) else {}
    if not isinstance(data, dict):
        data = {}
    lines = [
        f"Taskinity proof: {data.get('uri', '')}",
        f"Status: {'OK' if result.get('ok') else 'FAILED'}",
    ]
    target_status = data.get("target_status") or {}
    if isinstance(target_status, dict) and target_status:
        joined = ", ".join(f"{key}={value}" for key, value in target_status.items())
        lines.append(f"Target: {joined}")
    for check in data.get("checks") or []:
        if isinstance(check, dict):
            lines.append(_format_proof_check_line(check))
    return "\n".join(lines)
