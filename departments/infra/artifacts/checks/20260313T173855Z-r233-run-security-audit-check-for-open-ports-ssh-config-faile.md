# Infra Check (Run 233)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-13T17:38:55.290324Z

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
sshd_config.d/99-openclaw-hardening.conf:MaxAuthTries 3
sshd_config.d/99-openclaw-hardening.conf:LoginGraceTime 30
sshd_config.d/99-openclaw-hardening.conf:MaxStartups 10:30:60

## Recent SSH/Auth Findings
2026-03-13T02:31:41.497314+00:00 ip-172-31-34-63 sshd[165769]: Accepted publickey for ubuntu from 1.145.101.55 port 1352 ssh2: ED25519 SHA256:qwy43PraEAaWyIZ2IMWXEUP9DC0xybOtqZAULFykJso

## Auth Risk Assessment
No failed authentication attempts found in sampled logs (auth.log)

## Auth Source Summary
No suspicious auth-event source summary available
