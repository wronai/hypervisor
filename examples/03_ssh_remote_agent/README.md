# Example 03 — remote agent host przez Docker + SSH

Kontener udaje zewnętrzną maszynę do testów wdrożeń SSH, skanowania HTTP i sterowania Dockerem przez `uri3`.

## Wymagania

```bash
pip install -e '.[dev]'
docker compose v2
sshpass   # apt install sshpass — do logowania hasłem
```

## 1. Hasło SSH (raz, przez uri3)

```bash
uri3 call 'env://HYPERVISOR_SSH_PASSWORD?action=set&value=deploy&persist=1'
```

Alternatywa: `export HYPERVISOR_SSH_PASSWORD=deploy` lub wpis w `.env`.

## 2. Start testenv

```bash
make docker-testenv-up
# to samo:
uri3 call 'docker://stack/ssh-testenv?action=up&build=1'
```

Kontener wystawia:

```txt
SSH:        ssh://deploy@localhost:2222/opt/agents   (hasło: deploy)
HTTP mock:  http://localhost:8101  (patrz uwaga o porcie poniżej)
Agent Card: /.well-known/agent-card.json
Health:     /health
```

### Uwaga: port HTTP

Compose mapuje `8101:8101`. Jeśli port `8101` na hoście jest zajęty, Docker może użyć innego portu:

```bash
docker port hypervisor-ssh-agent-host 8101
# np. 0.0.0.0:8102 → skanuj http://localhost:8102
uri3 scan http://localhost:8102
```

## 3. Sprawdzenie (scan / verify)

```bash
uri3 scan --all
uri3 scan ssh
uri3 scan docker
uri3 scan http

hypervisor verify-agent weather-map-agent.ssh-dev
hypervisor scan ssh://deploy@localhost:2222/opt/agents/weather-map-agent
```

Test SSH ręcznie:

```bash
ssh -p 2222 deploy@localhost 'ls -la /opt/agents'
```

## 4. Zdalny deploy (hypervisor)

```bash
hypervisor deploy-agent weather-map-agent.ssh-dev
hypervisor deploy-agent weather-map-agent.ssh-dev --apply
hypervisor run-agent weather-map-agent.ssh-dev --dry-run
hypervisor agent-status weather-map-agent.ssh-dev --no-health
```

## 5. Logi

**Logi kontenera Docker** (stdout mock agenta + sshd):

```bash
uri3 call 'docker://stack/ssh-testenv?action=logs&tail=100'
# lub bezpośrednio kontener:
uri3 call 'docker://container/hypervisor-ssh-agent-host?action=logs&tail=100'
hypervisor docker 'docker://stack/ssh-testenv?action=logs&tail=100'
```

**Status stacka:**

```bash
uri3 call 'docker://stack/ssh-testenv?action=ps'
uri3 scan docker://stack/ssh-testenv
```

**Logi aplikacji hypervisor** (pliki, nie Docker):

```bash
uri3 logs 'log://hypervisor?limit=20'
hypervisor logs weather-map-agent.local
```

## 6. Docker deploy agenta (opcjonalnie)

```bash
uri3 call 'docker://generate/weather-map-agent?action=generate'
hypervisor deploy-agent weather-map-agent.docker
hypervisor deploy-agent weather-map-agent.docker --apply
hypervisor verify-agent weather-map-agent.docker
hypervisor stop-agent weather-map-agent.docker
```

## 7. Stop testenv

```bash
make docker-testenv-down
# to samo:
uri3 call 'docker://stack/ssh-testenv?action=down&remove_volumes=1'
```

## Pliki

```txt
examples/03_ssh_remote_agent/docker-compose.yml
testenv/ssh_agent_host/          # Dockerfile, mock_agent_server.py
config/docker.uri.yaml           # stack ssh-testenv
config/ssh.uri.yaml              # profil deploy@localhost:2222
```
