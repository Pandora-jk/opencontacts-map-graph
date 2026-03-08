# Infra Check (Run 37)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-08T21:33:17.654703Z

## Open Ports
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53%lo:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::]:22
udp 0.0.0.0:5353
udp 127.0.0.1:323
udp 127.0.0.53%lo:53
udp 127.0.0.54:53
udp 172.31.34.63%enp39s0:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (1): udp/5353
RISK: udp/5353 is mDNS/MulticastDNS; public/cloud hosts usually do not need it. Consider disabling MulticastDNS/LLMNR or blocking it with host/cloud firewall policy.

## Multicast DNS Exposure
ALERT: External mDNS listener detected on udp/5353
Listener scope: 0.0.0.0:* (2 socket(s))
Listener owner(s): openclaw-gateway
Listener PID(s): 255105
RISK: udp/5353 listener owner is not systemd-resolved/avahi-daemon: openclaw-gateway
RISK: the managed resolved drop-in is defense-in-depth, but it may not clear udp/5353 while that service still binds the socket
HARDENING: inspect the owning process before assuming the resolved drop-in will clear udp/5353: `ps -fp 255105`
HARDENING: if that process/service exposes Bonjour/mDNS discovery, disable it there or bind it to loopback/internal interfaces only
systemd-resolved: enabled=enabled, active=active
avahi-daemon: enabled=not-found, active=inactive
systemd-resolved config: no explicit MulticastDNS/LLMNR override found
managed drop-in ready: /home/ubuntu/.openclaw/workspace/systemd/99-openclaw-no-mdns.conf (mode 0644)
live drop-in missing: /etc/systemd/resolved.conf.d/99-openclaw-no-mdns.conf
nsswitch hosts: hosts: files dns
RISK: local host resolution does not reference mdns; external udp/5353 is less likely to be required
HARDENING: set MulticastDNS=no if this host does not require mDNS service discovery
HARDENING: set LLMNR=no on public/cloud hosts unless explicitly required
HARDENING: preview the managed drop-in with `python3 tools/infra_mdns_hardening.py --stdout`
HARDENING: sync the managed workspace drop-in with `python3 tools/infra_mdns_hardening.py --write-managed-dropin`
HARDENING: stage/test the install outside /etc with `python3 tools/infra_mdns_hardening.py --stage-dir /tmp/openclaw-mdns-stage --validate-live`
HARDENING: staged validation only confirms the drop-in content/path; it does not clear the live host listener
HARDENING: only install to /etc after the staged validation reports the staged drop-in installed and STAGED_VALIDATION_READY
HARDENING: install the managed drop-in with `sudo install -D -m 0644 /home/ubuntu/.openclaw/workspace/systemd/99-openclaw-no-mdns.conf /etc/systemd/resolved.conf.d/99-openclaw-no-mdns.conf`
HARDENING: restart resolved and verify with `sudo systemctl restart systemd-resolved && python3 tools/infra_mdns_hardening.py --validate-live` (expect LIVE_VALIDATION_DONE; LIVE_VALIDATION_FAILED means the drop-in is missing/drifted or udp/5353 is still exposed)
HARDENING: if mDNS is unnecessary, disable avahi-daemon/systemd-resolved mDNS support or block udp/5353 upstream

## Firewall Status
WARN: ufw unavailable on host
RISK: No host firewall tool detected (ufw/nft/iptables unavailable)
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
X11Forwarding no

## Recent SSH/Auth Findings
2026-03-08T02:05:52.932947+00:00 ip-172-31-34-63 sshd[287548]: Invalid user squid from 80.94.95.115 port 49010
2026-03-08T02:05:53.318018+00:00 ip-172-31-34-63 sshd[287548]: Connection closed by invalid user squid 80.94.95.115 port 49010 [preauth]
2026-03-08T03:43:28.819370+00:00 ip-172-31-34-63 sshd[289628]: Invalid user operator from 192.109.200.213 port 27140
2026-03-08T03:43:29.091880+00:00 ip-172-31-34-63 sshd[289628]: Disconnected from invalid user operator 192.109.200.213 port 27140 [preauth]
2026-03-08T05:30:41.757472+00:00 ip-172-31-34-63 sshd[291597]: Invalid user  from 159.223.145.49 port 53824

## Auth Risk Assessment
ALERT: 5 suspicious auth lines found in sampled logs (auth.log)
