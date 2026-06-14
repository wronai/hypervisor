#!/usr/bin/env bash
set -euo pipefail
mkdir -p /run/sshd /opt/agents/weather-map-agent
chown -R deploy:deploy /opt/agents
/usr/sbin/sshd
su - deploy -c 'cd /opt/agents/weather-map-agent && python3 /opt/mock_agent_server.py' &
wait -n
