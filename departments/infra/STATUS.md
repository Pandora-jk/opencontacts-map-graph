# Infra Status

- Last run (UTC): 2026-03-08T12:34:16Z
- Run count: 17
- Active task: **Run security audit:** Check for open ports, SSH config, failed logins.
- Selection reason: risk-based priority: ALERT: Unexpected externally exposed listeners (1): udp/5353; RISK: udp/5353 is mDNS/MulticastDNS; public/cloud hosts usually do not need it. Consider disabling MulticastDNS/LLMNR or blocking it with host/cloud firewall policy.; ALERT: External mDNS listener detected on udp/5353; RISK: local host resolution does not reference mdns; external udp/5353 is less likely to be required; WARN: ufw unavailable on host; RISK: No host firewall tool detected (ufw/nft/iptables unavailable); ALERT: 5 suspicious auth lines found in sampled logs (auth.log); unexpected udp/5353 listener still exposed
- Task progress count: 17
- Last artifact: departments/infra/artifacts/checks/20260308T123416Z-r17-run-security-audit-check-for-open-ports-ssh-config-faile.md
- Autonomous open queue: 4

