FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server rsync curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash deploy \
    && echo 'deploy:deploy' | chpasswd \
    && mkdir -p /home/deploy/.ssh /run/sshd /opt/agents/weather-map-agent \
    && chown -R deploy:deploy /home/deploy /opt/agents

RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

COPY mock_agent_server.py /opt/mock_agent_server.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh /opt/mock_agent_server.py

EXPOSE 22 8101
CMD ["/entrypoint.sh"]
