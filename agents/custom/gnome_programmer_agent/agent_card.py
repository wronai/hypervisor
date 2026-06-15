from __future__ import annotations

AGENT_CARD = {
    "name": "gnome-programmer-agent",
    "version": "0.1.0",
    "description": "Observe and interact with Ubuntu GNOME desktop through desktop-operator.",
    "generated_from": {"contract": "contracts/agents/gnome_programmer_agent.yaml"},
    "capabilities": [
        {
            "name": "observe_desktop",
            "type": "command",
            "uri": "screen://desktop/observe",
            "command": "ObserveDesktop",
        },
        {
            "name": "type_on_desktop",
            "type": "command",
            "uri": "input://desktop/type",
            "command": "TypeOnDesktop",
        },
        {
            "name": "programmer_session",
            "type": "command",
            "uri": "workflow://desktop/programmer-session",
            "command": "RunProgrammerSession",
        },
    ],
}
