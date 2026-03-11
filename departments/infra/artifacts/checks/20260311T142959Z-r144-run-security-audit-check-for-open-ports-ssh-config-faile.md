# Infra Check (Run 144)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-11T14:29:59.033780Z

## Open Ports
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53%lo:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::]:22
tcp [::ffff:127.0.0.1]:17564
tcp [::ffff:127.0.0.1]:36349
tcp [::ffff:127.0.0.1]:46189
udp *:58627
udp 127.0.0.1:323
udp 127.0.0.53%lo:53
udp 127.0.0.54:53
udp 172.31.34.63%enp39s0:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (1): udp/58627

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
ufw: active
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
X11Forwarding no

## Recent SSH/Auth Findings
2026-03-10T23:08:38.052575+00:00 ip-172-31-34-63 sshd[45426]: Invalid user sol from 164.92.146.128 port 33130
2026-03-10T23:08:38.330114+00:00 ip-172-31-34-63 sshd[45426]: Connection closed by invalid user sol 164.92.146.128 port 33130 [preauth]
2026-03-10T23:09:48.992071+00:00 ip-172-31-34-63 sshd[45430]: Invalid user solana from 64.225.75.83 port 39626
2026-03-10T23:09:49.270567+00:00 ip-172-31-34-63 sshd[45430]: Connection closed by invalid user solana 64.225.75.83 port 39626 [preauth]
2026-03-10T23:12:03.667735+00:00 ip-172-31-34-63 sshd[45659]: Invalid user sol from 64.225.75.83 port 52536
2026-03-10T23:12:03.938269+00:00 ip-172-31-34-63 sshd[45659]: Connection closed by invalid user sol 64.225.75.83 port 52536 [preauth]
2026-03-11T02:05:44.695889+00:00 ip-172-31-34-63 sshd[51575]: Invalid user  from 115.190.119.177 port 42040
2026-03-11T02:05:51.613584+00:00 ip-172-31-34-63 sshd[51575]: Connection closed by invalid user  115.190.119.177 port 42040 [preauth]

## Auth Risk Assessment
ALERT: 8 suspicious auth lines found in sampled logs (auth.log)
