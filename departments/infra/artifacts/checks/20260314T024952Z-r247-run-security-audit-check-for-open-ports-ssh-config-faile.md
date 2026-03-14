# Infra Check (Run 247)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-14T02:49:52.916383Z

## Open Ports
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53%lo:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::]:22
tcp [::ffff:127.0.0.1]:40161
udp *:59606
udp 127.0.0.1:323
udp 127.0.0.53%lo:53
udp 127.0.0.54:53
udp 172.31.34.63%enp39s0:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (1): udp/59606

## Unexpected Listener Details
ALERT: Detailed inspection for unexpected listeners (1): udp/59606
udp/59606 scope: *:*
udp/59606 owner(s): java
udp/59606 pid(s): 235854
HARDENING: inspect the owning process with `ps -fp 235854`
HARDENING: if udp/59606 is not required publicly, bind it to loopback/internal interfaces only or block it with host/cloud firewall policy

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
sshd_config.d/99-openclaw-hardening.conf:AllowStreamLocalForwarding no
sshd_config.d/99-openclaw-hardening.conf:PermitTunnel no
sshd_config.d/99-openclaw-hardening.conf:MaxAuthTries 3
sshd_config.d/99-openclaw-hardening.conf:LoginGraceTime 30
sshd_config.d/99-openclaw-hardening.conf:MaxStartups 10:30:60

## SSH Hardening Validation
managed config ready: /home/ubuntu/.openclaw/workspace/ssh/99-openclaw-hardening.conf (mode 0644)
live config installed: /etc/ssh/sshd_config.d/99-openclaw-hardening.conf (mode 0644)
INFO: effective sshd policy matches the managed hardening

## Recent SSH/Auth Findings
2026-03-13T10:15:38.756871+00:00 ip-172-31-34-63 sshd[191406]: Accepted publickey for ubuntu from 1.145.101.55 port 1366 ssh2: ED25519 SHA256:qwy43PraEAaWyIZ2IMWXEUP9DC0xybOtqZAULFykJso

## Auth Risk Assessment
No failed authentication attempts found in sampled logs (auth.log)

## Auth Source Summary
No suspicious auth-event source summary available

## SSH Ban Hardening
managed config ready: /home/ubuntu/.openclaw/workspace/fail2ban/99-openclaw-sshd.local (mode 0644)
live config installed: /etc/fail2ban/jail.d/99-openclaw-sshd.local (mode 0644)
INFO: managed fail2ban sshd jail policy: maxretry=3, findtime=10m, bantime=4h
fail2ban-client: /usr/bin/fail2ban-client
fail2ban service: enabled=enabled, active=active
INFO: fail2ban sshd jail status requires root; socket present: /var/run/fail2ban/fail2ban.sock (mode 0700, owner root:root)
