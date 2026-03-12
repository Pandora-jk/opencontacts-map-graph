# Infra Check (Run 184)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-12T14:23:44.717969Z

## Open Ports
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53%lo:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::]:22
tcp [::ffff:127.0.0.1]:17808
tcp [::ffff:127.0.0.1]:34817
tcp [::ffff:127.0.0.1]:35737
udp *:44346
udp 127.0.0.1:323
udp 127.0.0.53%lo:53
udp 127.0.0.54:53
udp 172.31.34.63%enp39s0:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (1): udp/44346

## Unexpected Listener Details
ALERT: Detailed inspection for unexpected listeners (1): udp/44346
udp/44346 scope: *:*
udp/44346 owner(s): java
udp/44346 pid(s): 137452
HARDENING: inspect the owning process with `ps -fp 137452`
HARDENING: if udp/44346 is not required publicly, bind it to loopback/internal interfaces only or block it with host/cloud firewall policy

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
ufw: active
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
sshd_config:X11Forwarding no
sshd_config.d/60-cloudimg-settings.conf:PasswordAuthentication no

## Recent SSH/Auth Findings
2026-03-11T18:09:02.672181+00:00 ip-172-31-34-63 sshd[99818]: Invalid user  from 209.38.226.254 port 37616
2026-03-11T18:09:09.567339+00:00 ip-172-31-34-63 sshd[99818]: Connection closed by invalid user  209.38.226.254 port 37616 [preauth]
2026-03-11T18:42:08.242192+00:00 ip-172-31-34-63 sshd[102335]: AuthorizedKeysCommand /usr/share/ec2-instance-connect/eic_run_authorized_keys root SHA256:PGK2DFxX8v3S5AWyU/SiBvPQCwLTmtSeeG4x0ekPOZ4 failed, status 22
2026-03-11T20:45:01.123294+00:00 ip-172-31-34-63 sshd[105617]: Invalid user a from 79.249.90.245 port 56602
2026-03-11T20:45:36.357473+00:00 ip-172-31-34-63 sshd[105617]: Connection closed by invalid user a 79.249.90.245 port 56602 [preauth]

## Auth Risk Assessment
ALERT: 5 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
ALERT: Auth event sources in sampled logs (5 events / 2 source(s)): 209.38.226.254 x2; 79.249.90.245 x2 (users: a)
Note: 1 suspicious auth line(s) lacked a parseable source and were omitted from the source summary
HARDENING: review recurring auth-event sources for host/cloud firewall blocking or access-list restrictions
HARDENING: preview a managed sshd drop-in with `python3 tools/infra_sshd_hardening.py --stdout`
HARDENING: sync the managed workspace sshd config with `python3 tools/infra_sshd_hardening.py --write-managed-config`
HARDENING: stage/test the sshd install outside /etc with `python3 tools/infra_sshd_hardening.py --stage-dir /tmp/openclaw-sshd-stage --validate-live`
HARDENING: install the managed sshd config with `sudo install -D -m 0644 /home/ubuntu/.openclaw/workspace/ssh/99-openclaw-hardening.conf /etc/ssh/sshd_config.d/99-openclaw-hardening.conf`
HARDENING: reload ssh and verify with `sudo systemctl reload ssh && python3 tools/infra_sshd_hardening.py --validate-live` (expect LIVE_VALIDATION_DONE; LIVE_VALIDATION_FAILED means the managed config is missing/drifted)
HARDENING: preview a managed SSH ban config with `python3 tools/infra_ssh_ban_hardening.py --stdout`
HARDENING: sync the managed workspace fail2ban config with `python3 tools/infra_ssh_ban_hardening.py --write-managed-config`
HARDENING: stage/test the install outside /etc with `python3 tools/infra_ssh_ban_hardening.py --stage-dir /tmp/openclaw-fail2ban-stage --validate-live`
HARDENING: staged validation only confirms the managed config content/path; it does not enable host bans until the live /etc install and fail2ban restart
HARDENING: install the managed config with `sudo install -D -m 0644 /home/ubuntu/.openclaw/workspace/fail2ban/99-openclaw-sshd.local /etc/fail2ban/jail.d/99-openclaw-sshd.local`
HARDENING: restart fail2ban and verify with `sudo systemctl restart fail2ban && python3 tools/infra_ssh_ban_hardening.py --validate-live` (expect LIVE_VALIDATION_DONE; LIVE_VALIDATION_FAILED means the managed config is missing/drifted)
