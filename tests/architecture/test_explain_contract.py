"""Architecture: uri3 explain completeness."""

from __future__ import annotations

from pathlib import Path

from uri3.resolvers.explain import explain_uri

REQUIRED_FIELDS = frozenset(
    {
        "uri",
        "matched_registry",
        "verification",
    }
)


def _assert_explain_contract(payload: dict) -> None:
    missing = REQUIRED_FIELDS - set(payload)
    assert not missing, f"missing explain fields: {sorted(missing)}"
    verification = payload["verification"]
    assert verification.get("source") == "uri2verify"
    assert "expected_status_fields" in verification
    assert "runtime_transport" in payload


def test_explain_weather_contract(repo_root: Path):
    payload = explain_uri("weather://forecast/Gdansk/14/html", root=repo_root)
    _assert_explain_contract(payload)
    assert payload["runtime_transport"] == "touri:python"


def test_explain_browser_contract(repo_root: Path):
    payload = explain_uri("browser://chrome/page/open", root=repo_root)
    _assert_explain_contract(payload)
    assert payload["runtime_transport"] == "uri2ops"


def test_explain_http_contract(repo_root: Path):
    payload = explain_uri("http://localhost:8101/health", root=repo_root)
    _assert_explain_contract(payload)
    assert payload["runtime_transport"] == "uri3:built-in"
