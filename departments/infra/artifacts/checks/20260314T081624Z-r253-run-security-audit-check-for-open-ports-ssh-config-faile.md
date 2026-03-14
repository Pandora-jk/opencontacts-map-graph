# Infra Check (Run 253)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-14T08:16:24.889413Z

## Open Ports
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53%lo:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::]:22
udp 127.0.0.1:323
udp 127.0.0.53%lo:53
udp 127.0.0.54:53
udp 172.31.34.63%enp39s0:68
udp [::1]:323

## External Listener Assessment
Externally exposed listeners match allowlist (2): tcp/22, udp/68

## Unexpected Listener Details
No unexpected listener details to inspect

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
ufw: active
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
sshd_config:X11Forwarding no
sshd_config.d/60-cloudimg-settings.conf:PasswordAuthentication no
sshd_config.d/99-openclaw-hardening.conf:PasswordAuthentication no
sshd_config.d/99-openclaw-hardening.conf:PermitRootLogin prohibit-password
sshd_config.d/99-openclaw-hardening.conf:PermitEmptyPasswords no
sshd_config.d/99-openclaw-hardening.conf:X11Forwarding no
sshd_config.d/99-openclaw-hardening.conf:AllowTcpForwarding no
sshd_config.d/99-openclaw-hardening.conf:AllowAgentForwarding no
sshd_config.d/99-openclaw-hardening.conf:AllowStreamLocalForwarding no
sshd_config.d/99-openclaw-hardening.conf:PermitTunnel no
sshd_config.d/99-openclaw-hardening.conf:MaxAuthTries 3
sshd_config.d/99-openclaw-hardening.conf:LoginGraceTime 30
sshd_config.d/99-openclaw-hardening.conf:MaxStartups 10:30:60

## SSH Hardening Validation
managed config ready: /home/ubuntu/.openclaw/workspace/ssh/99-openclaw-hardening.conf (mode 0644)
live config installed: /etc/ssh/sshd_config.d/99-openclaw-hardening.conf (mode 0644)
INFO: effective sshd policy matches the managed hardening

## Recent SSH/Auth Findings
2026-03-13T18:07:49.686738+00:00 ip-172-31-34-63 sshd[215715]: Disconnecting authenticating user root 155.4.119.66 port 43674: Too many authentication failures [preauth]
2026-03-13T18:07:53.316843+00:00 ip-172-31-34-63 sshd[215717]: Disconnecting authenticating user root 155.4.119.66 port 44200: Too many authentication failures [preauth]
2026-03-13T18:07:56.718274+00:00 ip-172-31-34-63 sshd[215720]: Disconnecting authenticating user root 155.4.119.66 port 44842: Too many authentication failures [preauth]
2026-03-13T18:07:59.789607+00:00 ip-172-31-34-63 sshd[215722]: Disconnecting authenticating user root 155.4.119.66 port 45394: Too many authentication failures [preauth]

## Auth Risk Assessment
4 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
Auth-event source summary unavailable (4 suspicious line(s) lacked a parseable source)

## SSH Ban Hardening
managed config ready: /home/ubuntu/.openclaw/workspace/fail2ban/99-openclaw-sshd.local (mode 0644)
live config installed: /etc/fail2ban/jail.d/99-openclaw-sshd.local (mode 0644)
INFO: managed fail2ban sshd jail policy: maxretry=3, findtime=10m, bantime=4h
fail2ban-client: /usr/bin/fail2ban-client
fail2ban service: enabled=enabled, active=active
INFO: fail2ban sshd jail status requires root; socket present: /var/run/fail2ban/fail2ban.sock (mode 0700, owner root:root)
