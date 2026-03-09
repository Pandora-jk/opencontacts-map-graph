# Infra Check (Run 49)

- Task: **Monitor disk usage:** Alert if >80%.
- UTC: 2026-03-09T08:37:55.423104Z

## Disk Usage
Root usage: /: 94% used (18G/19G, avail 1.2G)
CRITICAL: Root filesystem usage is 94% (>90%)
Inodes: /: 15% used
Top disk usage under / (depth 1):
17G	/
9.3G	/usr
6.1G	/home
1.5G	/var
143M	/opt
105M	/tmp
8.7M	/etc
24K	/snap
Reclaim candidates (review before cleanup):
- 628M /var/cache/apt (APT package cache)
- 366M /home/ubuntu/.cache (user cache)
- 130M /var/log/journal (systemd journals)
No deleted-but-open files detected
