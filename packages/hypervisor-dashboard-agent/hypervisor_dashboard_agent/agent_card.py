from __future__ import annotations

import json

AGENT_CARD = json.loads(
    """
{
  "id": "hypervisor-dashboard",
  "name": "Hypervisor Dashboard",
  "version": "0.1.0",
  "description": "System observer/renderer agent — URI process dashboard with approval-gated actions.",
  "type": "system_agent",
  "role": ["observer", "renderer", "controller"],
  "capabilities": [
    {
      "id": "process.view",
      "name": "process_view",
      "type": "query",
      "uri": "view://process/agent/{agent_id}/latest",
      "operation": "render",
      "side_effects": false,
      "description": "Render latest process view for a deployed agent."
    },
    {
      "id": "workflow.timeline",
      "name": "workflow_timeline",
      "type": "query",
      "uri": "view://workflow/{workflow_id}/timeline",
      "operation": "render",
      "side_effects": false,
      "description": "Render workflow timeline view."
    },
    {
      "id": "incident.explain",
      "name": "incident_explain",
      "type": "query",
      "uri": "view://incident/{incident_id}/explain",
      "operation": "render",
      "side_effects": false,
      "description": "Explain an incident artifact."
    },
    {
      "id": "repair.diagnose",
      "name": "repair_diagnose",
      "type": "query",
      "uri": "repair://agent/{agent_id}/diagnose",
      "operation": "read",
      "side_effects": false,
      "description": "Diagnose agent health and build repair plan."
    },
    {
      "id": "repair.action",
      "name": "repair_action",
      "type": "command",
      "uri": "repair://agent/{agent_id}/apply",
      "operation": "command",
      "side_effects": true,
      "requires_approval": true,
      "description": "Apply safe repair playbooks (requires approval)."
    },
    {
      "id": "uri.call",
      "name": "uri_call",
      "type": "command",
      "uri": "hypervisor://dashboard/uri/call",
      "operation": "command",
      "side_effects": true,
      "requires_approval": true,
      "description": "Execute arbitrary URI through policy gate."
    }
  ]
}
"""
)
