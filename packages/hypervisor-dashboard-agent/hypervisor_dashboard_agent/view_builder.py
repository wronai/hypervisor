from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from hypervisor.deployment_registry.selector import resolve_deployment
from hypervisor.deployment_registry.supervisor import inspect_agent
from hypervisor.paths import find_repo_root

from hypervisor_dashboard_agent.models import ProcessViewModel, UriAction

_env = Environment(
    loader=PackageLoader("hypervisor_dashboard_agent", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def _human_title(agent_ref: str, agent_id: str) -> str:
    name = agent_ref.replace("agent://", "").replace("-", " ").title()
    return name or agent_id


def build_process_view(agent_id: str, *, root: Path | None = None) -> ProcessViewModel:
    repo = root or find_repo_root()
    deployment = resolve_deployment(agent_id, root=repo)
    inspection = inspect_agent(agent_id, root=repo)
    readiness = inspection.get("agent_readiness") or {}
    summary = inspection.get("readiness") or readiness.get("summary") or {}

    related = {
        "view": f"view://process/agent/{agent_id}/latest",
        "runtime": f"runtime://agent/{agent_id}/state",
        "health": f"health://agent/{agent_id}",
        "diagnose": f"repair://agent/{agent_id}/diagnose",
        "logs": str(inspection.get("log_uri") or f"log://hypervisor?grep={agent_id}"),
    }
    if inspection.get("effective_health_uri"):
        related["effective_health"] = str(inspection["effective_health_uri"])

    actions = [
        UriAction("Diagnose", related["diagnose"], requires_approval=False, kind="read"),
        UriAction("View runtime state", related["runtime"], requires_approval=False, kind="read"),
        UriAction("Read error logs", related["logs"], requires_approval=False, kind="read"),
        UriAction(
            "Apply safe repair",
            f"repair://agent/{agent_id}/apply",
            requires_approval=True,
            kind="repair",
        ),
        UriAction(
            "Create ticket from incident",
            f"ticket://bug/from-incident/{agent_id}",
            requires_approval=True,
            kind="mutation",
        ),
    ]

    return ProcessViewModel(
        agent_id=agent_id,
        agent_ref=deployment.agent_ref,
        title=_human_title(deployment.agent_ref, agent_id),
        service_status=str(inspection.get("service_status") or "unknown"),
        deployment_status=str(readiness.get("deployment_status") or inspection.get("service_status") or "unknown"),
        process_status=str(readiness.get("process_status") or summary.get("process") or "unknown"),
        health_status=str(readiness.get("health_status") or summary.get("health") or "unknown"),
        recommended_action=str(readiness.get("recommended_action") or "observe"),
        effective_health_uri=inspection.get("effective_health_uri"),
        effective_port=summary.get("effective_port") or readiness.get("effective_port"),
        incidents=list(inspection.get("incidents") or []),
        warnings=list(inspection.get("warnings") or []),
        readiness=readiness,
        related_uris=related,
        actions=actions,
        inspection=inspection,
    )


def render_process_html(model: ProcessViewModel) -> str:
    template = _env.get_template("process.html")
    return template.render(model=model, view=model.to_dict())
