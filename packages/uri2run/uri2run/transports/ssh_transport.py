from __future__ import annotations

from typing import Any

from uri3.results import ServiceResult, service_result

from uri2run.result import error_result


def run_ssh(target: str, payload: dict[str, Any], context: dict[str, Any]) -> ServiceResult:
    from uri3.resolvers.ssh_resolver import (
        build_ssh_command,
        parse_ssh_uri,
        resolve_ssh,
    )
    from uri3.resolvers.ssh_resolver import (
        run_ssh as exec_ssh,
    )

    try:
        ref = parse_ssh_uri(target)
    except ValueError as exc:
        return error_result("SSH_URI_INVALID", str(exc), result_type="ssh")

    remote_command = payload.get("command") or payload.get("remote_command")
    if not remote_command:
        return service_result(
            ok=True,
            result_type="ssh",
            data=resolve_ssh(target),
            meta={"transport": "ssh", "target": target, "mode": "resolve"},
        )

    try:
        completed = exec_ssh(ref, str(remote_command), check=False)
    except RuntimeError as exc:
        return error_result("SSH_TRANSPORT_FAILED", str(exc), result_type="ssh")

    command = build_ssh_command(ref, str(remote_command))
    return service_result(
        ok=completed.returncode == 0,
        result_type="ssh",
        data={
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "returncode": completed.returncode,
            "command": command,
            "command_string": " ".join(command),
        },
        meta={"transport": "ssh", "target": target, "mode": "exec"},
    )


def run_ssh_transport(
    backend: dict[str, Any],
    payload: dict[str, Any],
    context: dict[str, Any],
) -> ServiceResult:
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "ssh backend missing target/url")
    return run_ssh(str(target), payload, context)
