import os, json, httpx
from dotenv import load_dotenv
from nl2uri.planner import rule_based_plan, PlanResult
SYSTEM_PROMPT = """Translate natural language into URI Tree JSON. Return JSON only. Required top-level fields: domain, commands, resources, agent. Use URI schemes: domain://, input://, command://, event://, resource://, artifact://, agent://, a2a://, mcp://, llm://, env://, python://. Do not include secrets; use env://NAME."""

def llm_plan(prompt: str) -> PlanResult:
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_uri = os.getenv("LLM_MODEL", "llm://openrouter/qwen/qwen3-coder-next")
    model = model_uri.replace("llm://", "")
    if model.startswith("openrouter/"): model = model[len("openrouter/"):]
    if not api_key: return rule_based_plan(prompt)
    payload = {"model": model, "messages": [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}], "temperature": float(os.getenv("LLM_TEMPERATURE", "0.1"))}
    r = httpx.post(os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=60)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    try: return PlanResult(json.loads(content), used_llm=True)
    except Exception: return rule_based_plan(prompt)
