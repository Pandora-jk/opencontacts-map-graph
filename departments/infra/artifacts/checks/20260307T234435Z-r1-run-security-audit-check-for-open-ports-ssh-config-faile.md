# Infra Check (Run 1)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-07T23:44:35.456588Z

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
Listener owner(s): openclaw-gatewa
systemd-resolved: enabled=enabled, active=active
avahi-daemon: enabled=not-found, active=inactive
systemd-resolved config: no explicit MulticastDNS/LLMNR override found
managed drop-in ready: /home/ubuntu/.openclaw/workspace/systemd/99-openclaw-no-mdns.conf
live drop-in missing: /etc/systemd/resolved.conf.d/99-openclaw-no-mdns.conf
nsswitch hosts: hosts: files dns
RISK: local host resolution does not reference mdns; external udp/5353 is less likely to be required
HARDENING: set MulticastDNS=no if this host does not require mDNS service discovery
HARDENING: set LLMNR=no on public/cloud hosts unless explicitly required
HARDENING: preview the managed drop-in with `python3 tools/infra_mdns_hardening.py --stdout`
HARDENING: sync the managed workspace drop-in with `python3 tools/infra_mdns_hardening.py --write-managed-dropin`
HARDENING: install the managed drop-in with `sudo install -D -m 0644 /home/ubuntu/.openclaw/workspace/systemd/99-openclaw-no-mdns.conf /etc/systemd/resolved.conf.d/99-openclaw-no-mdns.conf`
HARDENING: restart resolved and verify with `sudo systemctl restart systemd-resolved && python3 tools/infra_mdns_hardening.py --validate-live`
HARDENING: if mDNS is unnecessary, disable avahi-daemon/systemd-resolved mDNS support or block udp/5353 upstream

## Firewall Status
WARN: ufw unavailable on host
RISK: No host firewall tool detected (ufw/nft/iptables unavailable)
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
X11Forwarding no

## Recent SSH/Auth Findings
No recent SSH/auth findings in sampled logs

## Auth Risk Assessment
No failed authentication attempts found in sampled logs (auth.log)
