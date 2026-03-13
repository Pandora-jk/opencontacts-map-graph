# Infra Check (Run 212)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-13T04:18:20.126292Z

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
sshd_config:X11Forwarding no
sshd_config.d/60-cloudimg-settings.conf:PasswordAuthentication no
sshd_config.d/99-openclaw-hardening.conf:PasswordAuthentication no
sshd_config.d/99-openclaw-hardening.conf:PermitRootLogin prohibit-password
sshd_config.d/99-openclaw-hardening.conf:PermitEmptyPasswords no
sshd_config.d/99-openclaw-hardening.conf:X11Forwarding no
sshd_config.d/99-openclaw-hardening.conf:AllowTcpForwarding no
sshd_config.d/99-openclaw-hardening.conf:AllowAgentForwarding no
sshd_config.d/99-openclaw-hardening.conf:MaxAuthTries 3
sshd_config.d/99-openclaw-hardening.conf:LoginGraceTime 30
sshd_config.d/99-openclaw-hardening.conf:MaxStartups 10:30:60

## Recent SSH/Auth Findings
2026-03-12T11:30:27.895898+00:00 ip-172-31-34-63 sshd[133647]: Invalid user admin from 157.230.252.59 port 38838
2026-03-12T11:30:28.677948+00:00 ip-172-31-34-63 sshd[133647]: Connection closed by invalid user admin 157.230.252.59 port 38838 [preauth]
2026-03-12T11:32:05.020013+00:00 ip-172-31-34-63 sshd[133857]: Invalid user admin from 157.230.252.59 port 54604
2026-03-12T12:46:07.624609+00:00 ip-172-31-34-63 sshd[136789]: Invalid user admin from 192.109.200.220 port 10756
2026-03-12T12:46:09.511839+00:00 ip-172-31-34-63 sshd[136789]: Disconnected from invalid user admin 192.109.200.220 port 10756 [preauth]
2026-03-12T13:03:34.071827+00:00 ip-172-31-34-63 sshd[138513]: Invalid user pi from 178.128.37.37 port 51842
2026-03-12T13:03:34.624628+00:00 ip-172-31-34-63 sshd[138513]: Connection closed by invalid user pi 178.128.37.37 port 51842 [preauth]
2026-03-12T15:04:25.901071+00:00 ip-172-31-34-63 sshd[142627]: Invalid user admin from 94.26.106.201 port 56588
2026-03-12T15:04:26.269096+00:00 ip-172-31-34-63 sshd[142627]: Disconnected from invalid user admin 94.26.106.201 port 56588 [preauth]

## Auth Risk Assessment
ALERT: 9 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
ALERT: Auth event sources in sampled logs (9 events / 4 source(s)): 157.230.252.59 x3 (users: admin); 178.128.37.37 x2 (users: pi); 192.109.200.220 x2 (users: admin); 94.26.106.201 x2 (users: admin)
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
