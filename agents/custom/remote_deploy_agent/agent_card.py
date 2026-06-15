from __future__ import annotations

AGENT_CARD = {
    "name": "remote-deploy-agent",
    "version": "0.1.0",
    "description": "Deploy, verify and start generated agents on remote SSH hosts.",
    "generated_from": {"contract": "contracts/agents/remote_deploy_agent.yaml"},
    "capabilities": [
        {
            "name": "plan_remote_deploy",
            "type": "command",
            "uri": "deploy://agents/plan",
            "command": "PlanRemoteDeploy",
        },
        {
            "name": "apply_remote_deploy",
            "type": "command",
            "uri": "deploy://agents/apply",
            "command": "ApplyRemoteDeploy",
        },
        {
            "name": "verify_remote_agent",
            "type": "command",
            "uri": "deploy://agents/verify",
            "command": "VerifyRemoteAgent",
        },
        {
            "name": "start_remote_agent",
            "type": "command",
            "uri": "deploy://agents/start",
            "command": "StartRemoteAgent",
        },
        {
            "name": "deploy_verify_start",
            "type": "command",
            "uri": "workflow://agents/deploy-verify-start",
            "command": "DeployVerifyStart",
        },
    ],
}
