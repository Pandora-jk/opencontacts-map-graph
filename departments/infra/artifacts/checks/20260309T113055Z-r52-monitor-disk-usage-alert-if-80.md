# Infra Check (Run 52)

- Task: **Monitor disk usage:** Alert if >80%.
- UTC: 2026-03-09T11:30:55.589693Z

## Disk Usage
Root usage: /: 100% used (19G/19G, avail 153M)
CRITICAL: Root filesystem usage is 100% (>90%)
Inodes: /: 15% used
Top disk usage under / (depth 1):
18G	/
9.3G	/usr
7.1G	/home
1.5G	/var
143M	/opt
106M	/tmp
8.7M	/etc
24K	/snap
Reclaim candidates (review before cleanup):
- 628M /var/cache/apt (APT package cache)
- 366M /home/ubuntu/.cache (user cache)
- 143M /var/log/journal (systemd journals)
No deleted-but-open files detected
