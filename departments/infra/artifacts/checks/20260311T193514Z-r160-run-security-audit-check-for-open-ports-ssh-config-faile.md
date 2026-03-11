# Infra Check (Run 160)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-11T19:35:14.033017Z

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
2026-03-11T04:45:16.884108+00:00 ip-172-31-34-63 sshd[59893]: Invalid user admin from 192.109.200.220 port 30272
2026-03-11T04:45:19.176946+00:00 ip-172-31-34-63 sshd[59893]: Disconnected from invalid user admin 192.109.200.220 port 30272 [preauth]
2026-03-11T04:45:22.958228+00:00 ip-172-31-34-63 sshd[59895]: Invalid user support from 192.109.200.220 port 20450
2026-03-11T05:23:30.388910+00:00 ip-172-31-34-63 sshd[60892]: Invalid user config from 204.76.203.207 port 62542
2026-03-11T05:23:30.908738+00:00 ip-172-31-34-63 sshd[60892]: Disconnected from invalid user config 204.76.203.207 port 62542 [preauth]
2026-03-11T05:23:33.171647+00:00 ip-172-31-34-63 sshd[60912]: Invalid user demo from 204.76.203.207 port 62544
2026-03-11T05:23:33.827052+00:00 ip-172-31-34-63 sshd[60912]: Disconnected from invalid user demo 204.76.203.207 port 62544 [preauth]
2026-03-11T06:52:38.909616+00:00 ip-172-31-34-63 sshd[64487]: userauth_pubkey: signature algorithm ssh-rsa not in PubkeyAcceptedAlgorithms [preauth]
2026-03-11T06:52:39.236354+00:00 ip-172-31-34-63 sshd[64487]: AuthorizedKeysCommand /usr/share/ec2-instance-connect/eic_run_authorized_keys root SHA256:tiCpUmN1iZO3KrPKz524b4C40+jOpylgMiztBZc4Kjg failed, status 22

## Auth Risk Assessment
ALERT: 8 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
ALERT: Auth event sources in sampled logs (8 events / 2 source(s)): 204.76.203.207 x4 (users: config, demo); 192.109.200.220 x3 (users: admin, support)
Note: 1 suspicious auth line(s) lacked a parseable source and were omitted from the source summary
HARDENING: review recurring auth-event sources for host/cloud firewall blocking or access-list restrictions
HARDENING: if these probes recur, consider SSH ban/rate-limit tooling such as fail2ban or sshguard
