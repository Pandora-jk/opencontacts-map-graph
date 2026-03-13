# Infra Check (Run 223)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-13T13:48:21.441957Z

## Open Ports
tcp *:22
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53:53
tcp 127.0.0.54:53
tcp [::1]:18789
udp 127.0.0.1:323
udp 127.0.0.53:53
udp 127.0.0.54:53
udp 172.31.34.63:68
udp [::1]:323

## External Listener Assessment
Externally exposed listeners match allowlist (2): tcp/22, udp/68

## Unexpected Listener Details
No unexpected listener details to inspect

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
WARN: ufw installed but status visibility is blocked by current privileges
ufw: sudo: The "no new privileges" flag is set, which prevents sudo from running as root. sudo: If sudo is running in a container, you may need to adjust the container configuration to…
INFO: ufw boot config ENABLED=yes (/etc/ufw/ufw.conf)
HARDENING: verify `sudo ufw status verbose` from an unrestricted host shell
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
sshd_config.d/99-openclaw-hardening.conf:MaxAuthTries 3
sshd_config.d/99-openclaw-hardening.conf:LoginGraceTime 30
sshd_config.d/99-openclaw-hardening.conf:MaxStartups 10:30:60

## Recent SSH/Auth Findings
2026-03-12T20:51:01.819691+00:00 ip-172-31-34-63 sshd[155585]: Invalid user a from 123.209.73.212 port 33550
2026-03-12T20:51:01.857342+00:00 ip-172-31-34-63 sshd[155585]: Connection closed by invalid user a 123.209.73.212 port 33550 [preauth]
2026-03-12T23:12:17.701697+00:00 ip-172-31-34-63 sshd[160140]: Invalid user admin from 176.65.132.218 port 49986
2026-03-12T23:12:19.329708+00:00 ip-172-31-34-63 sshd[160140]: Disconnected from invalid user admin 176.65.132.218 port 49986 [preauth]

## Auth Risk Assessment
4 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
INFO: Auth event sources in sampled logs (4 events / 2 source(s)): 123.209.73.212 x2 (users: a); 176.65.132.218 x2 (users: admin)
