from __future__ import annotations

import re

OUTPUT_KINDS = (
    "single_uri",
    "uri_list",
    "resource_tree",
    "uri_flow",
    "task_graph",
    "workflow_graph",
)

DOMAIN_WORDS = re.compile(
    r"\b(wygeneruj|generuj|stw[oó]rz|zbuduj|utw[oó]rz|dodaj|domain|domen[aę]|agenta|system)\b",
    re.I,
)
ACTION_WORDS = re.compile(
    r"\b(otw[oó]rz|sprawd[zź]|uruchom|kliknij|pobierz|zr[oó]b|screenshot|przejd[zź]|"
    r"je[sś]li|potem|nast[eę]pnie|po czym|verify|open|check|run|click|screenshot|restart)\b",
    re.I,
)
BROWSER_WORDS = re.compile(r"\b(chrome|przegl[aą]dark|browser|dom://|localhost)\b", re.I)
SEQUENTIAL_WORKFLOW = re.compile(
    r"\b(wygeneruj|generuj|stw[oó]rz).*(uruchom|run).*(sprawd[zź]|health|browser|chrome)\b",
    re.I | re.S,
)
CONDITION_WORDS = re.compile(r"\b(je[sś]li|if|gdy|restart|zrestartuj|nie dzia[lł]a)\b", re.I)
PARALLEL_WORDS = re.compile(r"\b(r[oó]wnoleg|parallel|jednocze[sś]nie|oraz.*oraz)\b", re.I)
READ_TARGETS = re.compile(r"\b(health|card|status|log|agent card)\b", re.I)


def classify_output_kind(prompt: str) -> str:
    text = prompt.strip()
    if not text:
        return "single_uri"

    has_domain = bool(DOMAIN_WORDS.search(text))
    has_actions = bool(ACTION_WORDS.search(text))
    has_browser = bool(BROWSER_WORDS.search(text))
    has_condition = bool(CONDITION_WORDS.search(text))
    has_parallel = bool(PARALLEL_WORDS.search(text))
    read_targets = len(READ_TARGETS.findall(text))

    if has_parallel and has_actions:
        return "workflow_graph"

    if has_condition and has_actions and not SEQUENTIAL_WORKFLOW.search(text):
        return "workflow_graph"

    if SEQUENTIAL_WORKFLOW.search(text):
        return "uri_flow"

    if has_domain and not has_actions:
        return "resource_tree"

    if has_domain and has_actions:
        return "uri_flow"

    if read_targets >= 2 and not has_browser and not has_condition:
        return "uri_list"

    if has_browser and has_actions:
        return "uri_flow"

    if has_actions and not has_domain:
        return "uri_flow" if not has_condition else "workflow_graph"

    if read_targets >= 2:
        return "uri_list"

    if re.search(r"\b(poka[zż]|status|health|card|agent)\b", text, re.I):
        return "single_uri"

    if has_domain:
        return "resource_tree"

    return "single_uri"
