# Infra Check (Run 249)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-14T04:55:31.721903Z

## Open Ports
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53%lo:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::]:22
tcp [::ffff:127.0.0.1]:46389
udp *:58214
udp 127.0.0.1:323
udp 127.0.0.53%lo:53
udp 127.0.0.54:53
udp 172.31.34.63%enp39s0:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (1): udp/58214

## Unexpected Listener Details
ALERT: Detailed inspection for unexpected listeners (1): udp/58214
udp/58214 scope: *:*
udp/58214 owner(s): java
udp/58214 pid(s): 246324
HARDENING: inspect the owning process with `ps -fp 246324`
HARDENING: if udp/58214 is not required publicly, bind it to loopback/internal interfaces only or block it with host/cloud firewall policy

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
No recent SSH/auth findings in sampled logs

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
