# Infra Check (Run 210)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-13T02:58:42.293203Z

## Open Ports
tcp *:22
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53:53
tcp 127.0.0.54:53
tcp [::1]:18789
udp 127.0.0.1:323
udp 127.0.0.53:53
udp 127.0.0.54:53
udp 172.31.34.63:68
udp [::1]:323

## External Listener Assessment
Externally exposed listeners match allowlist (2): tcp/22, udp/68

## Unexpected Listener Details
No unexpected listener details to inspect

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
WARN: ufw installed but status visibility is blocked by current privileges
ufw: sudo: The "no new privileges" flag is set, which prevents sudo from running as root. sudo: If sudo is running in a container, you may need to adjust the container configuration to…
INFO: ufw boot config ENABLED=yes (/etc/ufw/ufw.conf)
HARDENING: verify `sudo ufw status verbose` from an unrestricted host shell
Other firewall tooling detected: nft, iptables
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
sshd_config:X11Forwarding no
sshd_config.d/60-cloudimg-settings.conf:PasswordAuthentication no

## Recent SSH/Auth Findings
2026-03-12T10:30:56.467289+00:00 ip-172-31-34-63 sshd[132137]: Invalid user support from 171.231.191.189 port 47884
2026-03-12T10:30:56.634521+00:00 ip-172-31-34-63 sshd[132137]: Connection closed by invalid user support 171.231.191.189 port 47884 [preauth]
2026-03-12T10:32:21.053041+00:00 ip-172-31-34-63 sshd[132152]: Invalid user squid from 171.231.190.54 port 53758
2026-03-12T10:32:21.678031+00:00 ip-172-31-34-63 sshd[132152]: Connection closed by invalid user squid 171.231.190.54 port 53758 [preauth]
2026-03-12T10:32:29.397229+00:00 ip-172-31-34-63 sshd[132158]: Invalid user user from 171.231.190.54 port 48558
2026-03-12T10:32:29.549052+00:00 ip-172-31-34-63 sshd[132158]: Connection closed by invalid user user 171.231.190.54 port 48558 [preauth]
2026-03-12T11:30:27.895898+00:00 ip-172-31-34-63 sshd[133647]: Invalid user admin from 157.230.252.59 port 38838
2026-03-12T11:30:28.677948+00:00 ip-172-31-34-63 sshd[133647]: Connection closed by invalid user admin 157.230.252.59 port 38838 [preauth]
2026-03-12T11:32:05.020013+00:00 ip-172-31-34-63 sshd[133857]: Invalid user admin from 157.230.252.59 port 54604

## Auth Risk Assessment
ALERT: 9 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
ALERT: Auth event sources in sampled logs (9 events / 3 source(s)): 171.231.190.54 x4 (users: squid, user); 157.230.252.59 x3 (users: admin); 171.231.191.189 x2 (users: support)
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
