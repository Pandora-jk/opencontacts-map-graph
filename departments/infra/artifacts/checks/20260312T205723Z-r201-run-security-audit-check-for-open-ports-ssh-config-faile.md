# Infra Check (Run 201)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-12T20:57:23.766403Z

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

## Recent SSH/Auth Findings
2026-03-12T04:06:02.913331+00:00 ip-172-31-34-63 sshd[119505]: Invalid user pi from 161.35.36.218 port 39670
2026-03-12T04:06:03.578215+00:00 ip-172-31-34-63 sshd[119505]: Connection closed by invalid user pi 161.35.36.218 port 39670 [preauth]

## Auth Risk Assessment
2 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
INFO: Auth event sources in sampled logs (2 events / 1 source(s)): 161.35.36.218 x2 (users: pi)
