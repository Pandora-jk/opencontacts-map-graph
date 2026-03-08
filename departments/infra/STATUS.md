# Infra Status

- Last run (UTC): 2026-03-08T21:57:35Z
- Run count: 40
- Active task: **Run security audit:** Check for open ports, SSH config, failed logins.
- Selection reason: risk-based priority: ALERT: Unexpected externally exposed listeners (1): udp/5353; RISK: udp/5353 is mDNS/MulticastDNS; public/cloud hosts usually do not need it. Consider disabling MulticastDNS/LLMNR or blocking it with host/cloud firewall policy.; ALERT: External mDNS listener detected on udp/5353; RISK: udp/5353 listener owner is not systemd-resolved/avahi-daemon: openclaw-gateway; RISK: the managed resolved drop-in is defense-in-depth, but it may not clear udp/5353 while that service still binds the socket; RISK: local host resolution does not reference mdns; external udp/5353 is less likely to be required; WARN: ufw unavailable on host; RISK: No host firewall tool detected (ufw/nft/iptables unavailable); ALERT: 5 suspicious auth lines found in sampled logs (auth.log); unexpected udp/5353 listener still exposed
- Task progress count: 40
- Last artifact: departments/infra/artifacts/checks/20260308T215735Z-r40-run-security-audit-check-for-open-ports-ssh-config-faile.md
- Autonomous open queue: 4

