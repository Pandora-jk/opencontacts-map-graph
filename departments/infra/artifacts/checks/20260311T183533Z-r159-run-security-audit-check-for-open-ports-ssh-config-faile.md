# Infra Check (Run 159)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-11T18:35:33.132815Z

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
2026-03-11T02:05:44.695889+00:00 ip-172-31-34-63 sshd[51575]: Invalid user  from 115.190.119.177 port 42040
2026-03-11T02:05:51.613584+00:00 ip-172-31-34-63 sshd[51575]: Connection closed by invalid user  115.190.119.177 port 42040 [preauth]
2026-03-11T04:45:16.884108+00:00 ip-172-31-34-63 sshd[59893]: Invalid user admin from 192.109.200.220 port 30272
2026-03-11T04:45:19.176946+00:00 ip-172-31-34-63 sshd[59893]: Disconnected from invalid user admin 192.109.200.220 port 30272 [preauth]
2026-03-11T04:45:22.958228+00:00 ip-172-31-34-63 sshd[59895]: Invalid user support from 192.109.200.220 port 20450
2026-03-11T05:23:30.388910+00:00 ip-172-31-34-63 sshd[60892]: Invalid user config from 204.76.203.207 port 62542
2026-03-11T05:23:30.908738+00:00 ip-172-31-34-63 sshd[60892]: Disconnected from invalid user config 204.76.203.207 port 62542 [preauth]
2026-03-11T05:23:33.171647+00:00 ip-172-31-34-63 sshd[60912]: Invalid user demo from 204.76.203.207 port 62544
2026-03-11T05:23:33.827052+00:00 ip-172-31-34-63 sshd[60912]: Disconnected from invalid user demo 204.76.203.207 port 62544 [preauth]

## Auth Risk Assessment
ALERT: 9 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
ALERT: Auth event sources in sampled logs (9 events / 3 source(s)): 204.76.203.207 x4 (users: config, demo); 192.109.200.220 x3 (users: admin, support); 115.190.119.177 x2
HARDENING: review recurring auth-event sources for host/cloud firewall blocking or access-list restrictions
HARDENING: if these probes recur, consider SSH ban/rate-limit tooling such as fail2ban or sshguard
