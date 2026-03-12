# Infra Check (Run 166)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-12T01:36:05.808532Z

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
X11Forwarding no

## Recent SSH/Auth Findings
2026-03-11T08:34:44.877606+00:00 ip-172-31-34-63 sshd[68728]: Accepted publickey for ubuntu from 1.145.104.96 port 3748 ssh2: ED25519 SHA256:qwy43PraEAaWyIZ2IMWXEUP9DC0xybOtqZAULFykJso

## Auth Risk Assessment
No failed authentication attempts found in sampled logs (auth.log)

## Auth Source Summary
No suspicious auth-event source summary available
