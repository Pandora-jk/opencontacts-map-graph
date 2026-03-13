# Infra Check (Run 215)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-13T06:29:12.623606Z

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
2026-03-12T15:04:25.901071+00:00 ip-172-31-34-63 sshd[142627]: Invalid user admin from 94.26.106.201 port 56588
2026-03-12T15:04:26.269096+00:00 ip-172-31-34-63 sshd[142627]: Disconnected from invalid user admin 94.26.106.201 port 56588 [preauth]
2026-03-12T16:11:00.445142+00:00 ip-172-31-34-63 sshd[145814]: Invalid user postgres from 209.97.188.199 port 59774
2026-03-12T16:11:00.707894+00:00 ip-172-31-34-63 sshd[145814]: Connection closed by invalid user postgres 209.97.188.199 port 59774 [preauth]

## Auth Risk Assessment
4 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
INFO: Auth event sources in sampled logs (4 events / 2 source(s)): 209.97.188.199 x2 (users: postgres); 94.26.106.201 x2 (users: admin)
