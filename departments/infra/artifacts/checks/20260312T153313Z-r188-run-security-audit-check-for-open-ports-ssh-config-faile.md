# Infra Check (Run 188)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-12T15:33:13.213972Z

## Open Ports
tcp *:22
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::ffff:127.0.0.1]:34817
tcp [::ffff:127.0.0.1]:35737
udp *:44346
udp 127.0.0.1:323
udp 127.0.0.53:53
udp 127.0.0.54:53
udp 172.31.34.63:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (1): udp/44346

## Unexpected Listener Details
ALERT: Detailed inspection for unexpected listeners (1): udp/44346
udp/44346 scope: *:*
udp/44346 owner not visible from current permissions/capabilities
INFO: recent artifact attribution for udp/44346: owner(s): java (20260312T152345Z-r186-run-security-audit-check-for-open-ports-ssh-config-faile.md)
INFO: recent artifact pid(s) for udp/44346: 137452 (20260312T152345Z-r186-run-security-audit-check-for-open-ports-ssh-config-faile.md)
HARDENING: inspect udp/44346 from an unrestricted shell with `ss -H -ulpn 'sport = :44346' 2>/dev/null | sed -n '1,10p'`
HARDENING: inspect/reconfigure the owning service before allowing external exposure on udp/44346
HARDENING: if udp/44346 is not required publicly, bind it to loopback/internal interfaces only or block it with host/cloud firewall policy

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
WARN: ufw installed but status visibility is blocked by current privileges
ufw: sudo: The "no new privileges" flag is set, which prevents sudo from running as root. sudo: If sudo is running in a container, you may need to adjust the container configuration to…
HARDENING: verify `sudo ufw status verbose` from an unrestricted host shell
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
sshd_config:X11Forwarding no
sshd_config.d/60-cloudimg-settings.conf:PasswordAuthentication no

## Recent SSH/Auth Findings
2026-03-11T20:45:01.123294+00:00 ip-172-31-34-63 sshd[105617]: Invalid user a from 79.249.90.245 port 56602
2026-03-11T20:45:36.357473+00:00 ip-172-31-34-63 sshd[105617]: Connection closed by invalid user a 79.249.90.245 port 56602 [preauth]

## Auth Risk Assessment
2 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
INFO: Auth event sources in sampled logs (2 events / 1 source(s)): 79.249.90.245 x2 (users: a)
