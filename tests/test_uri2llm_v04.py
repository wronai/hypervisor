from hypervisor.uri2llm import resolve


def test_env_uri_resolution(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret")
    r = resolve("env://OPENROUTER_API_KEY")
    assert r.kind == "env"
    assert r.target["exists"] is True


def test_llm_uri_resolution():
    r = resolve("llm://openrouter/qwen/qwen3-coder-next")
    assert r.kind == "llm"
    assert r.target["provider"] == "openrouter"


def test_pypi_uri_resolution():
    r = resolve("pypi://httpx")
    assert r.target["package"] == "httpx"
