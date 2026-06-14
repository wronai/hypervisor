"""Catalog of hypervisor examples for integration tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ExampleSpec:
    id: str
    name: str
    kind: Literal["run_sh", "inline"]
    path: str = ""
    markers: tuple[str, ...] = ()
    timeout_s: int = 120


RUN_SH_EXAMPLES: tuple[ExampleSpec, ...] = (
    ExampleSpec(
        "04",
        "nl2a_weather_map",
        "run_sh",
        "examples/04_nl2a_weather_map/run.sh",
        timeout_s=180,
    ),
    ExampleSpec("09", "run_agent_hypervisor", "run_sh", "examples/09_run_agent_hypervisor/run.sh"),
    ExampleSpec("10", "browser_operator", "run_sh", "examples/10_browser_operator/run.sh"),
    ExampleSpec(
        "11",
        "playwright_browser",
        "run_sh",
        "examples/11_playwright_browser/run.sh",
        ("playwright",),
        180,
    ),
    ExampleSpec("12", "android_operator", "run_sh", "examples/12_android_operator/run.sh"),
    ExampleSpec("13op", "pcwin_operator", "run_sh", "examples/13_pcwin_operator/run.sh"),
    ExampleSpec(
        "13nl",
        "nl2uri_multi_uri_graph",
        "run_sh",
        "examples/13_nl2uri_multi_uri_graph/run.sh",
    ),
    ExampleSpec(
        "14wf",
        "workflow_executor_mock",
        "run_sh",
        "examples/14_workflow_executor_mock/run.sh",
    ),
    ExampleSpec("14srv", "uri2ops_serve", "run_sh", "examples/14_uri2ops_serve/run.sh"),
    ExampleSpec("15cf", "compact_uri_flow", "run_sh", "examples/15_compact_uri_flow/run.sh"),
    ExampleSpec("16", "llm_graph_planner", "run_sh", "examples/16_llm_graph_planner/run.sh"),
    ExampleSpec("17", "flow_vs_graph", "run_sh", "examples/17_flow_vs_graph/run.sh"),
    ExampleSpec("18", "llm_flow_planner", "run_sh", "examples/18_llm_flow_planner/run.sh"),
    ExampleSpec("20", "touri_capabilities", "run_sh", "examples/20_touri_capabilities/run.sh"),
    ExampleSpec("21", "touri_voice", "run_sh", "examples/21_touri_voice/run.sh"),
    ExampleSpec("22", "markpact_weather", "run_sh", "examples/22_markpact_weather/run.sh"),
    ExampleSpec(
        "23",
        "nl_to_agent_tutorial",
        "run_sh",
        "examples/23_nl_to_agent_tutorial/run.sh",
        ("slow",),
        300,
    ),
    ExampleSpec("30", "golden_path", "run_sh", "examples/30_golden_path/run.sh", timeout_s=180),
    ExampleSpec(
        "01",
        "quickstart_local",
        "run_sh",
        "examples/01_quickstart_local/run.sh",
        timeout_s=180,
    ),
)

INLINE_EXAMPLES: tuple[ExampleSpec, ...] = (
    ExampleSpec("02", "uri3_scan_http", "inline"),
    ExampleSpec("03", "ssh_remote_agent", "inline", markers=("docker",), timeout_s=300),
    ExampleSpec("05", "meta_repair", "inline"),
    ExampleSpec("06", "orders_agent", "inline"),
    ExampleSpec("07", "invoices_agent", "inline"),
    ExampleSpec("08", "evolution", "inline"),
    ExampleSpec("15pw", "playwright_via_uri3_mock", "inline"),
)

ALL_EXAMPLES = RUN_SH_EXAMPLES + INLINE_EXAMPLES
