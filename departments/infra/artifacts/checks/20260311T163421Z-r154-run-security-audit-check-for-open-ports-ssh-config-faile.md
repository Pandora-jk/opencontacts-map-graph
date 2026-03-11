# Infra Check (Run 154)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-11T16:34:21.916289Z

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
2026-03-10T23:12:03.938269+00:00 ip-172-31-34-63 sshd[45659]: Connection closed by invalid user sol 64.225.75.83 port 52536 [preauth]
2026-03-11T02:05:44.695889+00:00 ip-172-31-34-63 sshd[51575]: Invalid user  from 115.190.119.177 port 42040
2026-03-11T02:05:51.613584+00:00 ip-172-31-34-63 sshd[51575]: Connection closed by invalid user  115.190.119.177 port 42040 [preauth]

## Auth Risk Assessment
3 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
INFO: Auth event sources in sampled logs (3 events / 2 source(s)): 115.190.119.177 x1; 64.225.75.83 x1 (users: sol)
Note: 1 suspicious auth line(s) lacked a parseable source and were omitted from the source summary
