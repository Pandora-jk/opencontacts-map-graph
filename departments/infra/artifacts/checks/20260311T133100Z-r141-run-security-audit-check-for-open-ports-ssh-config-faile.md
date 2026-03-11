# Infra Check (Run 141)

- Task: **Run security audit:** Check for open ports, SSH config, failed logins.
- UTC: 2026-03-11T13:31:00.523745Z

## Open Ports
tcp *:22
tcp 0.0.0.0:22
tcp 127.0.0.1:18789
tcp 127.0.0.1:18791
tcp 127.0.0.1:18792
tcp 127.0.0.53:53
tcp 127.0.0.54:53
tcp [::1]:18789
tcp [::ffff:127.0.0.1]:17564
tcp [::ffff:127.0.0.1]:36349
tcp [::ffff:127.0.0.1]:46189
udp *:58627
udp 127.0.0.1:323
udp 127.0.0.53:53
udp 127.0.0.54:53
udp 172.31.34.63:68
udp [::1]:323

## External Listener Assessment
ALERT: Unexpected externally exposed listeners (1): udp/58627

## Multicast DNS Exposure
No external mDNS listener detected

## Firewall Status
ufw: sudo: The "no new privileges" flag is set, which prevents sudo from running as root. sudo: If sudo is running in a container, you may need to adjust the container configuration to…
Note: upstream cloud firewalls/security groups are not visible from this host check

## SSH Config Snapshot
X11Forwarding no

## Recent SSH/Auth Findings
2026-03-10T10:35:55.366534+00:00 ip-172-31-34-63 sshd[6878]: Invalid user admin from 2.57.121.112 port 5711
2026-03-10T10:35:57.177140+00:00 ip-172-31-34-63 sshd[6878]: Disconnected from invalid user admin 2.57.121.112 port 5711 [preauth]
2026-03-10T13:10:42.031183+00:00 ip-172-31-34-63 sshd[13000]: Invalid user admin from 167.172.86.9 port 44084
2026-03-10T13:10:42.265712+00:00 ip-172-31-34-63 sshd[13000]: Connection closed by invalid user admin 167.172.86.9 port 44084 [preauth]
2026-03-10T13:11:47.476301+00:00 ip-172-31-34-63 sshd[13002]: Invalid user admin from 167.172.86.9 port 49548
2026-03-10T13:11:47.723580+00:00 ip-172-31-34-63 sshd[13002]: Connection closed by invalid user admin 167.172.86.9 port 49548 [preauth]
2026-03-10T13:14:52.117287+00:00 ip-172-31-34-63 sshd[13008]: userauth_pubkey: signature algorithm ssh-rsa not in PubkeyAcceptedAlgorithms [preauth]
2026-03-10T13:14:52.440750+00:00 ip-172-31-34-63 sshd[13008]: AuthorizedKeysCommand /usr/share/ec2-instance-connect/eic_run_authorized_keys root SHA256:ZQuQ8iwXswasBLhKJ0a5X40Hm+ttqHI5S2Hp+hf50FY failed, status 22

## Auth Risk Assessment
ALERT: 7 suspicious auth lines found in sampled logs (auth.log)
