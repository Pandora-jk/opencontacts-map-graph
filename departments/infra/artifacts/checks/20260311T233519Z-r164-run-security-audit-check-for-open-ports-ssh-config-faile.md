# Infra Check (Run 164)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-11T23:35:19.506155Z

## Open Ports
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53%lo:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::]:22
tcp [::ffff:127.0.0.1]:17345
tcp [::ffff:127.0.0.1]:38113
tcp [::ffff:127.0.0.1]:43347
udp *:47706
udp 127.0.0.1:323
udp 127.0.0.53%lo:53
udp 127.0.0.54:53
udp 172.31.34.63%enp39s0:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (1): udp/47706

## Unexpected Listener Details
ALERT: Detailed inspection for unexpected listeners (1): udp/47706
udp/47706 scope: *:*
udp/47706 owner(s): java
udp/47706 pid(s): 106806
HARDENING: inspect the owning process with `ps -fp 106806`
HARDENING: if udp/47706 is not required publicly, bind it to loopback/internal interfaces only or block it with host/cloud firewall policy

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
ufw: active
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
X11Forwarding no

## Recent SSH/Auth Findings
2026-03-11T06:52:38.909616+00:00 ip-172-31-34-63 sshd[64487]: userauth_pubkey: signature algorithm ssh-rsa not in PubkeyAcceptedAlgorithms [preauth]
2026-03-11T06:52:39.236354+00:00 ip-172-31-34-63 sshd[64487]: AuthorizedKeysCommand /usr/share/ec2-instance-connect/eic_run_authorized_keys root SHA256:tiCpUmN1iZO3KrPKz524b4C40+jOpylgMiztBZc4Kjg failed, status 22
2026-03-11T07:39:32.465889+00:00 ip-172-31-34-63 sshd[66642]: Invalid user  from 134.199.162.79 port 46168
2026-03-11T07:39:40.453164+00:00 ip-172-31-34-63 sshd[66642]: Connection closed by invalid user  134.199.162.79 port 46168 [preauth]
2026-03-11T08:01:37.620492+00:00 ip-172-31-34-63 sshd[67526]: Invalid user  from 18.97.19.210 port 49860
2026-03-11T08:01:37.820287+00:00 ip-172-31-34-63 sshd[67526]: Connection closed by invalid user  18.97.19.210 port 49860 [preauth]
2026-03-11T08:34:44.877606+00:00 ip-172-31-34-63 sshd[68728]: Accepted publickey for ubuntu from 1.145.104.96 port 3748 ssh2: ED25519 SHA256:qwy43PraEAaWyIZ2IMWXEUP9DC0xybOtqZAULFykJso

## Auth Risk Assessment
ALERT: 5 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
ALERT: Auth event sources in sampled logs (5 events / 2 source(s)): 134.199.162.79 x2; 18.97.19.210 x2
Note: 1 suspicious auth line(s) lacked a parseable source and were omitted from the source summary
HARDENING: review recurring auth-event sources for host/cloud firewall blocking or access-list restrictions
HARDENING: if these probes recur, consider SSH ban/rate-limit tooling such as fail2ban or sshguard
