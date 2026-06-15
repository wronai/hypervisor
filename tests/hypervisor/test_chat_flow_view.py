"""Tests for shared chat flow view batch handling."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from hypervisor_dashboard_agent.main import app
from urish.backends.ask import ask_prompt


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _planner_plans_from_ask(result: dict) -> list[dict]:
    """Mirror TaskinityFlowView.plannerTurnFromAsk (Python side)."""
    data = result.get("data") or {}
    batch_actions = data.get("actions") or data.get("commands") or []
    if data.get("batch") and batch_actions:
        return [
            {
                "kind": item.get("detected_kind") or item.get("kind"),
                "subtype": item.get("detected_subtype") or item.get("subtype"),
                "deployment": item.get("deployment_id"),
                "uris": item.get("planned_uris") or item.get("uris") or [],
            }
            for item in batch_actions
        ]
    return [
        {
            "kind": data.get("detected_kind"),
            "subtype": data.get("detected_subtype"),
            "deployment": data.get("deployment_id"),
            "uris": data.get("planned_uris") or data.get("uris") or [],
        }
    ]


def test_batch_ask_yields_three_flow_plans():
    prompt = (
        "pokaż proces agenta weather-map-agent.local\n"
        "zdiagnozuj agenta invoices-agent.local\n"
        "rob rzuty ekranów stron softreck.com prototypowanie.pl www "
        "co 5 minut do folderu usera ~/images/"
    )
    result = ask_prompt(prompt)
    data = result["data"]
    assert data["batch"] is True
    assert len(data["actions"]) == 3

    plans = _planner_plans_from_ask(result)
    assert len(plans) == 3
    assert plans[0]["uris"] == ["view://process/agent/weather-map-agent.local/latest"]
    assert plans[1]["uris"] == ["repair://agent/invoices-agent.local/diagnose"]
    assert plans[2]["uris"] == ["workflow://graph/website-screenshot-schedule/dry-run"]
    assert plans[0]["deployment"] == "weather-map-agent.local"
    assert plans[1]["deployment"] == "invoices-agent.local"


def test_workflow_dry_run_uri_call_returns_graph_steps(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "workflow://graph/website-screenshot-schedule/dry-run",
            "dry_run": True,
            "approved": False,
            "policy": "dev",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    plan = payload.get("data", {}).get("plan") or {}
    steps = plan.get("steps") or []
    assert len(steps) >= 2
    assert steps[0]["uri"] == "browser://chrome/page/capture"
    assert steps[1]["uri"] == "browser://chrome/page/capture"
    manifest = plan.get("manifest") or {}
    graph_nodes = (manifest.get("uri_graph") or {}).get("nodes") or []
    assert len(graph_nodes) >= 2
