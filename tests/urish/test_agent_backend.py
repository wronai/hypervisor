"""Tests for urish agent backend dispatch."""

from __future__ import annotations

from unittest.mock import patch

from urish.backends.agent import agent_action


def test_agent_action_run_forwards_detach_once():
    with patch("hypervisor.deployment_registry.runner.run_agent") as mocked:
        mocked.return_value = {"ok": True}
        result = agent_action(
            "run",
            "weather-map-agent.local",
            detach=True,
            wait_healthy=True,
            supervise_repair="auto",
        )
        assert result == {"ok": True}
        mocked.assert_called_once_with(
            "weather-map-agent.local",
            detach=True,
            wait_healthy=True,
            supervise_repair="auto",
        )
