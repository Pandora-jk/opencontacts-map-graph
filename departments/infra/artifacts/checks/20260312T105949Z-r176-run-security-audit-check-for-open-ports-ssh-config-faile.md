# Infra Check (Run 176)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-12T10:59:49.518181Z

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
2026-03-11T16:23:09.389116+00:00 ip-172-31-34-63 sshd[91202]: Invalid user  from 101.126.135.131 port 53198
2026-03-11T16:23:16.326573+00:00 ip-172-31-34-63 sshd[91202]: Connection closed by invalid user  101.126.135.131 port 53198 [preauth]
2026-03-11T18:09:02.672181+00:00 ip-172-31-34-63 sshd[99818]: Invalid user  from 209.38.226.254 port 37616
2026-03-11T18:09:09.567339+00:00 ip-172-31-34-63 sshd[99818]: Connection closed by invalid user  209.38.226.254 port 37616 [preauth]
2026-03-11T18:42:08.242192+00:00 ip-172-31-34-63 sshd[102335]: AuthorizedKeysCommand /usr/share/ec2-instance-connect/eic_run_authorized_keys root SHA256:PGK2DFxX8v3S5AWyU/SiBvPQCwLTmtSeeG4x0ekPOZ4 failed, status 22

## Auth Risk Assessment
ALERT: 5 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
ALERT: Auth event sources in sampled logs (5 events / 2 source(s)): 101.126.135.131 x2; 209.38.226.254 x2
Note: 1 suspicious auth line(s) lacked a parseable source and were omitted from the source summary
HARDENING: review recurring auth-event sources for host/cloud firewall blocking or access-list restrictions
HARDENING: if these probes recur, consider SSH ban/rate-limit tooling such as fail2ban or sshguard
