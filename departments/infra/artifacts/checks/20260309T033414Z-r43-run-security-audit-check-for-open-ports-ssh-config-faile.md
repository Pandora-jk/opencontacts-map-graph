# Infra Check (Run 43)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-09T03:34:14.571906Z

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

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
WARN: ufw unavailable on host
RISK: No host firewall tool detected (ufw/nft/iptables unavailable)
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
X11Forwarding no

## Recent SSH/Auth Findings
2026-03-08T02:05:52.932947+00:00 ip-172-31-34-63 sshd[287548]: Invalid user squid from 80.94.95.115 port 49010
2026-03-08T02:05:53.318018+00:00 ip-172-31-34-63 sshd[287548]: Connection closed by invalid user squid 80.94.95.115 port 49010 [preauth]
2026-03-08T03:43:28.819370+00:00 ip-172-31-34-63 sshd[289628]: Invalid user operator from 192.109.200.213 port 27140
2026-03-08T03:43:29.091880+00:00 ip-172-31-34-63 sshd[289628]: Disconnected from invalid user operator 192.109.200.213 port 27140 [preauth]
2026-03-08T05:30:41.757472+00:00 ip-172-31-34-63 sshd[291597]: Invalid user  from 159.223.145.49 port 53824

## Auth Risk Assessment
ALERT: 5 suspicious auth lines found in sampled logs (auth.log)
