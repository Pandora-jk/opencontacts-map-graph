# Infra Check (Run 241)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-13T23:48:52.428502Z

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

## SSH Hardening Validation
managed config ready: /home/ubuntu/.openclaw/workspace/ssh/99-openclaw-hardening.conf (mode 0644)
live config drift: /etc/ssh/sshd_config.d/99-openclaw-hardening.conf
ERROR: effective sshd policy drift detected
- AllowStreamLocalForwarding=yes (expected no)

## Recent SSH/Auth Findings
2026-03-13T06:24:00.353811+00:00 ip-172-31-34-63 sshd[184275]: Accepted publickey for ubuntu from 1.145.101.55 port 1394 ssh2: ED25519 SHA256:qwy43PraEAaWyIZ2IMWXEUP9DC0xybOtqZAULFykJso
2026-03-13T07:31:07.695554+00:00 ip-172-31-34-63 sshd[188363]: Invalid user admin from 159.223.63.31 port 35482
2026-03-13T07:31:08.198506+00:00 ip-172-31-34-63 sshd[188363]: Connection closed by invalid user admin 159.223.63.31 port 35482 [preauth]
2026-03-13T07:32:07.921357+00:00 ip-172-31-34-63 sshd[188373]: Invalid user admin from 159.223.63.31 port 35846
2026-03-13T07:32:08.127495+00:00 ip-172-31-34-63 sshd[188373]: Connection closed by invalid user admin 159.223.63.31 port 35846 [preauth]

## Auth Risk Assessment
4 suspicious auth lines found in sampled logs (auth.log)

## Auth Source Summary
INFO: Auth event sources in sampled logs (4 events / 1 source(s)): 159.223.63.31 x4 (users: admin)

## SSH Ban Hardening
managed config ready: /home/ubuntu/.openclaw/workspace/fail2ban/99-openclaw-sshd.local (mode 0644)
WARN: live config drift: /etc/fail2ban/jail.d/99-openclaw-sshd.local
INFO: managed fail2ban sshd jail policy: maxretry=3, findtime=10m, bantime=4h
fail2ban-client: /usr/bin/fail2ban-client
fail2ban service: enabled=enabled, active=active
INFO: fail2ban sshd jail status requires root; socket present: /var/run/fail2ban/fail2ban.sock (mode 0700, owner root:root)
