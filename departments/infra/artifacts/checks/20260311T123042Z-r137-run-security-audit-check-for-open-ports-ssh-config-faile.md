# Infra Check (Run 137)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-11T12:30:42.612509Z

## Open Ports
tcp *:22
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::ffff:127.0.0.1]:17564
tcp [::ffff:127.0.0.1]:36349
tcp [::ffff:127.0.0.1]:46189
udp *:58627
udp 127.0.0.1:323
udp 127.0.0.53:53
udp 127.0.0.54:53
udp 172.31.34.63:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (4): tcp/17564, tcp/36349, tcp/46189, udp/58627

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
WARN: ufw unavailable on host
RISK: No host firewall tool detected (ufw/nft/iptables unavailable)
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
X11Forwarding no

## Recent SSH/Auth Findings
2026-03-10T07:59:02.779758+00:00 ip-172-31-34-63 sshd[1688]: Invalid user  from 35.216.254.237 port 54646
2026-03-10T07:59:03.091793+00:00 ip-172-31-34-63 sshd[1688]: Connection closed by invalid user  35.216.254.237 port 54646 [preauth]
2026-03-10T10:35:55.366534+00:00 ip-172-31-34-63 sshd[6878]: Invalid user admin from 2.57.121.112 port 5711
2026-03-10T10:35:57.177140+00:00 ip-172-31-34-63 sshd[6878]: Disconnected from invalid user admin 2.57.121.112 port 5711 [preauth]

## Auth Risk Assessment
4 suspicious auth lines found in sampled logs (auth.log)
