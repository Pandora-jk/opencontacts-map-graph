# Infra Check (Run 174)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-12T08:59:47.226187Z

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
2026-03-11T13:13:23.456843+00:00 ip-172-31-34-63 sshd[84054]: Invalid user squid from 116.110.156.53 port 56926
2026-03-11T13:13:23.629676+00:00 ip-172-31-34-63 sshd[84054]: Connection closed by invalid user squid 116.110.156.53 port 56926 [preauth]
2026-03-11T13:13:35.501084+00:00 ip-172-31-34-63 sshd[84056]: Invalid user installer from 116.110.156.53 port 39750
2026-03-11T13:33:55.768997+00:00 ip-172-31-34-63 sshd[84658]: Invalid user admin from 171.231.198.250 port 55006
2026-03-11T13:33:55.913600+00:00 ip-172-31-34-63 sshd[84658]: Connection closed by invalid user admin 171.231.198.250 port 55006 [preauth]
2026-03-11T13:57:20.116335+00:00 ip-172-31-34-63 sshd[85471]: Invalid user user3 from 94.26.106.200 port 20626
2026-03-11T13:57:20.407415+00:00 ip-172-31-34-63 sshd[85471]: Disconnected from invalid user user3 94.26.106.200 port 20626 [preauth]
2026-03-11T13:57:22.628156+00:00 ip-172-31-34-63 sshd[85473]: Invalid user squid from 94.26.106.200 port 20642
2026-03-11T13:57:22.917238+00:00 ip-172-31-34-63 sshd[85473]: Disconnected from invalid user squid 94.26.106.200 port 20642 [preauth]
2026-03-11T16:23:09.389116+00:00 ip-172-31-34-63 sshd[91202]: Invalid user  from 101.126.135.131 port 53198
2026-03-11T16:23:16.326573+00:00 ip-172-31-34-63 sshd[91202]: Connection closed by invalid user  101.126.135.131 port 53198 [preauth]

## Auth Risk Assessment
ALERT: 11 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
ALERT: Auth event sources in sampled logs (11 events / 4 source(s)): 94.26.106.200 x4 (users: squid, user3); 116.110.156.53 x3 (users: installer, squid); 101.126.135.131 x2; 171.231.198.250 x2 (users: admin)
HARDENING: review recurring auth-event sources for host/cloud firewall blocking or access-list restrictions
HARDENING: if these probes recur, consider SSH ban/rate-limit tooling such as fail2ban or sshguard
