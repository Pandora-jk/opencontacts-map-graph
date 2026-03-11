# Infra Check (Run 152)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-11T15:36:55.124108Z

## Open Ports
tcp *:22
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::ffff:127.0.0.1]:36349
tcp [::ffff:127.0.0.1]:46189
udp *:58627
udp 127.0.0.1:323
udp 127.0.0.53:53
udp 127.0.0.54:53
udp 172.31.34.63:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (1): udp/58627

## Unexpected Listener Details
ALERT: Detailed inspection for unexpected listeners (1): udp/58627
udp/58627 scope: *:*
udp/58627 owner not visible from current permissions/capabilities
HARDENING: inspect udp/58627 from an unrestricted shell with `ss -H -ulpn 'sport = :58627' 2>/dev/null | sed -n '1,10p'`
HARDENING: inspect/reconfigure the owning service before allowing external exposure on udp/58627
HARDENING: if udp/58627 is not required publicly, bind it to loopback/internal interfaces only or block it with host/cloud firewall policy

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
WARN: ufw installed but status visibility is blocked by current privileges
ufw: sudo: The "no new privileges" flag is set, which prevents sudo from running as root. sudo: If sudo is running in a container, you may need to adjust the container configuration to…
HARDENING: verify `sudo ufw status verbose` from an unrestricted host shell
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

## Auth Source Summary
ALERT: Auth event sources in sampled logs (8 events / 3 source(s)): 64.225.75.83 x4 (users: sol, solana); 164.92.146.128 x2 (users: sol); 115.190.119.177 x1
Note: 1 suspicious auth line(s) lacked a parseable source and were omitted from the source summary
HARDENING: review recurring auth-event sources for host/cloud firewall blocking or access-list restrictions
HARDENING: if these probes recur, consider SSH ban/rate-limit tooling such as fail2ban or sshguard
