# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/remote_deploy_agent.yaml
# Contract hash: sha256:cb604273489ae8add7f97a4cad7786e18f628fcb1528369b992e7e437be6846e

# ruff: noqa: E501

AGENT_CARD = {'name': 'remote-deploy-agent',
 'version': '0.1.0',
 'description': 'Deploy, verify and start generated agents on remote SSH hosts.',
 'generated_from': {'contract': 'contracts/agents/remote_deploy_agent.yaml',
                    'contract_hash': 'sha256:cb604273489ae8add7f97a4cad7786e18f628fcb1528369b992e7e437be6846e'},
 'capabilities': [{'name': 'plan_remote_deploy',
                   'type': 'command',
                   'description': 'Build rsync/verify plan for an SSH deployment '
                                  'selector.',
                   'uri': 'deploy://agents/plan',
                   'output_schema': 'app.deploy.v1.RemoteDeployPlan',
                   'renderer': 'detail',
                   'command': 'PlanRemoteDeploy',
                   'input_schema': 'app.deploy.v1.PlanRemoteDeployCommand',
                   'emits': []},
                  {'name': 'apply_remote_deploy',
                   'type': 'command',
                   'description': 'Sync generated agent package to remote host and '
                                  'verify path.',
                   'uri': 'deploy://agents/apply',
                   'output_schema': 'app.deploy.v1.RemoteDeployResult',
                   'renderer': 'detail',
                   'command': 'ApplyRemoteDeploy',
                   'input_schema': 'app.deploy.v1.ApplyRemoteDeployCommand',
                   'emits': []},
                  {'name': 'verify_remote_agent',
                   'type': 'command',
                   'description': 'Verify SSH connectivity, remote path and health '
                                  'endpoint.',
                   'uri': 'deploy://agents/verify',
                   'output_schema': 'app.deploy.v1.RemoteVerifyResult',
                   'renderer': 'detail',
                   'command': 'VerifyRemoteAgent',
                   'input_schema': 'app.deploy.v1.VerifyRemoteAgentCommand',
                   'emits': []},
                  {'name': 'start_remote_agent',
                   'type': 'command',
                   'description': 'Start agent process on remote host via SSH nohup '
                                  'and optional health wait.',
                   'uri': 'deploy://agents/start',
                   'output_schema': 'app.deploy.v1.RemoteStartResult',
                   'renderer': 'detail',
                   'command': 'StartRemoteAgent',
                   'input_schema': 'app.deploy.v1.StartRemoteAgentCommand',
                   'emits': []},
                  {'name': 'deploy_verify_start',
                   'type': 'command',
                   'description': 'End-to-end remote deploy, verify and start for an '
                                  'SSH deployment selector.',
                   'uri': 'workflow://agents/deploy-verify-start',
                   'output_schema': 'app.deploy.v1.DeployVerifyStartResult',
                   'renderer': 'detail',
                   'command': 'DeployVerifyStart',
                   'input_schema': 'app.deploy.v1.DeployVerifyStartCommand',
                   'emits': []}]}
