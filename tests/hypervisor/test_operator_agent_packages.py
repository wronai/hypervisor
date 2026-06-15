"""Operator agent packages expose scheme-filtered registries."""

from __future__ import annotations

from pathlib import Path

from uri2ops.remote_registry.loader import resolve_operation_registry


def test_browser_operator_registry_is_browser_only(repo_root: Path):
    registry = resolve_operation_registry(
        repo_root / "agents/operators/browser_operator/operation_registry.yaml",
        root=repo_root,
    )
    schemes = {spec.scheme for spec in registry.list()}
    assert schemes == {"browser", "assertion"}


def test_desktop_operator_registry_excludes_browser(repo_root: Path):
    registry = resolve_operation_registry(
        repo_root / "agents/operators/desktop_operator/operation_registry.yaml",
        root=repo_root,
    )
    schemes = {spec.scheme for spec in registry.list()}
    assert "browser" not in schemes
    assert {"screen", "input", "pcwin", "android", "assertion"} <= schemes


def test_device_robot_operator_registry_is_physical_only(repo_root: Path):
    registry = resolve_operation_registry(
        repo_root / "agents/operators/device_robot_operator/operation_registry.yaml",
        root=repo_root,
    )
    schemes = {spec.scheme for spec in registry.list()}
    assert schemes == {"robot", "device", "assertion"}


def test_browser_operator_app_loads(repo_root: Path):
    from agents.operators.browser_operator.main import app

    assert app.title == "browser-operator"


def test_common_assertion_handler(repo_root: Path):
    from agents.operators.common.assertion import check

    assert check({"expected": "ok", "actual": "it is ok"})["ok"] is True
    assert check({"expected": "fail", "actual": "nope"})["ok"] is False
